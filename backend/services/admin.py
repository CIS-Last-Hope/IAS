import shutil
import uuid
from datetime import (
    datetime,
    timedelta,
)
from pathlib import Path
from typing import Type

from fastapi import (
    Depends,
    HTTPException,
    status, UploadFile,
)

from fastapi.security import OAuth2PasswordBearer
from jose import (
    JWTError,
    jwt,
)

from passlib.hash import bcrypt
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .course import get_mime_type, pptx_to_images
from .. import (
    models,
    tables,
)

from ..database import get_session, engine
from ..models import Lesson
from ..settings import settings
from sqlalchemy import create_engine, MetaData, Table, select

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/admin/sign-in/')
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)


def get_current_user(token: str = Depends(oauth2_scheme)) -> models.Admin:
    return AuthAdminService.verify_token(token)


class AuthAdminService:
    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.verify(plain_password, hashed_password)

    @classmethod
    def hash_password(cls, password: str) -> str:
        return bcrypt.hash(password)

    @classmethod
    def verify_token(cls, token: str) -> models.Admin:
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=[settings.jwt_algorithm],
            )
        except JWTError:
            raise exception from None

        admin_data = payload.get('admin')
        admin_flag = payload.get('is_admin')

        exception = HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Forbidden',
        )

        if not admin_flag:
            raise exception

        try:
            user = models.Admin.parse_obj(admin_data)
        except ValidationError:
            raise exception from None

        return user

    @classmethod
    def create_token(cls, admin: tables.Admin) -> models.AdminToken:
        admin_data = models.Admin.from_orm(admin)
        now = datetime.utcnow()
        payload = {
            'iat': now,
            'nbf': now,
            'exp': now + timedelta(seconds=settings.jwt_expiration),
            'sub': str(admin_data.id),
            'admin': admin_data.dict(),
            'is_admin': True
        }
        token = jwt.encode(
            payload,
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm,
        )
        return models.AdminToken(access_token=token)

    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    async def register_new_admin(self, admin_data: models.AdminCreate, admin_code: str) -> models.AdminToken:
        if admin_code != settings.admin_code:
            exception = HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Forbidden',
            )
            raise exception
        admin = tables.Admin(
            email=admin_data.email,
            username=admin_data.username,
            password_hash=self.hash_password(admin_data.password),
        )
        try:
            self.session.add(admin)
            self.session.commit()
        except SQLAlchemyError:
            exception = HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Username already in use',
            )
            raise exception
        return self.create_token(admin)

    async def authenticate_admin(self, username: str, password: str) -> models.AdminToken:
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )

        admin = (
            self.session
            .query(tables.Admin)
            .filter(tables.Admin.username == username)
            .first()
        )

        if not admin:
            raise exception

        if not self.verify_password(password, admin.password_hash):
            raise exception

        return self.create_token(admin)


class AdminModeration:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    async def create_course(self, course: models.Course) -> models.Course:
        existing_course = self.session.query(tables.Course).filter(
            (tables.Course.title == course.title)
        ).first()

        exception = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bad request"
        )

        if existing_course:
            raise exception

        course = tables.Course(
            title=course.title,
            description=course.description,
            creator_id=1
        )

        try:
            self.session.add(course)
            self.session.commit()
        except ValueError:
            self.session.rollback()
            raise exception
        return course

    async def read_course(self, title: str) -> models.Course:
        course = self.session.query(tables.Course).filter(
            (tables.Course.title == title)
        ).first()
        if not course:
            raise HTTPException(status_code=404, detail="Record not found")
        return course

    async def update_course(self, title: str, course_data: models.CourseUpdate) -> models.Course:
        course = self.session.query(tables.Course).filter(
            (tables.Course.title == title)
        ).first()
        if not course:
            raise HTTPException(status_code=404, detail="Record not found")

        if course_data.title:
            course.title = course_data.title
        if course_data.description:
            course.description = course_data.description

        exception = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bad request"
        )
        try:
            self.session.commit()
        except ValueError:
            self.session.rollback()
            raise exception
        return course

    async def delete_course(self, title: str):
        course = self.session.query(tables.Course).filter(
            (tables.Course.title == title)
        ).first()

        course_dir = Path(f"uploads/{course.id}")
        if course_dir.exists():
            shutil.rmtree(course_dir)

        if not course:
            raise HTTPException(status_code=404, detail="Record not found")

        self.session.delete(course)
        self.session.commit()

    async def create_lesson(self, course_id: int, lesson_id: int, file: UploadFile):
        course = self.session.query(tables.Course).filter(
            (tables.Course.id == course_id)
        ).first()

        exception = HTTPException(
            status_code=404,
            detail="Course not found")
        if not course:
            raise exception

        course_dir = UPLOAD_DIR / str(course_id)
        course_dir.mkdir(exist_ok=True, parents=True)

        original_filename = file.filename
        file_path = course_dir / original_filename

        if file_path.exists():
            unique_filename = f"{file_path.stem}_{uuid.uuid4().hex}{file_path.suffix}"
            file_path = course_dir / unique_filename
            original_filename = unique_filename

        with file_path.open("wb") as f:
            f.write(file.file.read())

        mime_type = await get_mime_type(file_path)
        if mime_type == 'application/vnd.openxmlformats-officedocument.presentationml.presentation':
            file_path = await pptx_to_images(file_path, original_filename, course_id)

        lessons = self.session.query(tables.Lesson).filter(
            (tables.Lesson.course_id == course_id)
        ).all()

        for lesson in reversed(lessons):
            if lesson_id <= lesson.lesson_id:
                lesson.lesson_id += 1
                self.session.add(lesson)

        lesson = tables.Lesson(
            filename=file.filename,
            filepath=str(file_path),
            course_id=course_id,
            lesson_id=lesson_id
        )
        self.session.add(lesson)
        self.session.commit()

        return lesson

    async def read_lesson(self, course_id: int, lesson_id: int):
        lesson = self.session.query(tables.Lesson).filter(
            tables.Lesson.lesson_id == lesson_id,
            tables.Lesson.course_id == course_id,
        ).first()

        exception = HTTPException(
            status_code=404,
            detail="Lesson not found")

        if not lesson:
            raise exception

        mime_type = await get_mime_type(lesson.filepath)
        if mime_type == 'application/octet-stream':
            mime_type = 'multipart/x-mixed-replace; boundary=separator'
            path = Path(lesson.filepath)
            files = list(path.glob("*"))

            def file_generator():
                for file_path in files:
                    mime_type = 'image/jpeg'
                    yield f"--separator\nContent-Type: {mime_type}\n\n".encode('utf-8')
                    with open(file_path, "rb") as file:
                        yield from file
                    yield b"\n"

            file = file_generator()
        else:
            path = Path(lesson.filepath)
            file = path.open('rb')
        return file, mime_type

    async def delete_lesson(self, course_id: int, lesson_id: int):
        lesson = self.session.query(tables.Lesson).filter(
            tables.Lesson.lesson_id == lesson_id,
            tables.Lesson.course_id == course_id
        ).first()

        exception = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The file does not exist"
        )

        filepath = lesson.filepath
        file_path = Path(filepath)
        if file_path.is_dir():
            if file_path.exists():
                shutil.rmtree(file_path)
                file_path = str(file_path) + '.pptx'
                file_path = Path(file_path)
            else:
                raise exception
        if file_path.exists():
            file_path.unlink()
        else:
            raise exception

        self.session.delete(lesson)
        self.session.commit()

        lessons = self.session.query(tables.Lesson).filter(
            (tables.Lesson.course_id == course_id)
        ).all()

        for lesson in lessons:
            if lesson_id <= lesson.lesson_id:
                lesson.lesson_id -= 1
                self.session.add(lesson)

        self.session.commit()

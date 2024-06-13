import shutil
from pathlib import Path

from fastapi import Depends, HTTPException, status, UploadFile
from sqlalchemy.orm import Session

from .. import tables, models
from ..database import get_session

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)


class CourseService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    async def create_new_course(self, course: models.BaseCourse, user_id: int) -> models.Course:
        existing_course = self.session.query(tables.Course).filter(
            (tables.Course.title == course.title)
        ).first()

        exception = HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course with this title already exists"
        )

        if existing_course:
            raise exception

        course = tables.Course(
            title=course.title,
            description=course.description,
            creator_id=user_id,
        )

        try:
            self.session.add(course)
            self.session.commit()
        except ValueError:
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bad request"
            )
        return course

    async def upload_file(self, course_id: int, file: UploadFile, user_id: int):
        course = self.session.query(tables.Course).filter(
            (tables.Course.id == course_id)
             ).first()

        exception = HTTPException(
            status_code=404,
            detail="Course not found")
        if not course:
            raise exception

        exception = HTTPException(
            status_code=403,
            detail="Forbidden"
        )
        if course.creator_id != user_id:
            raise exception

        course_dir = UPLOAD_DIR / str(course_id)
        course_dir.mkdir(exist_ok=True, parents=True)

        file_location = course_dir / file.filename
        with file_location.open("wb") as f:
            f.write(file.file.read())

        material = tables.Material(
            filename=file.filename,
            filepath=str(file_location),
            course_id=course_id
        )
        self.session.add(material)
        self.session.commit()

        return {"filename": file.filename}

    async def download_file(self, course_id: int, user_id: int) -> str:
        course = self.session.query(tables.Course).filter(
            (tables.Course.id == course_id)
             ).first()

        exception = HTTPException(
            status_code=404,
            detail="Course not found")
        if not course:
            raise exception

        course_dir = UPLOAD_DIR / str(course_id)
        exception = HTTPException(
                status_code=404,
                detail="No materials found for this course"
            )
        if not course_dir.exists() or not any(course_dir.iterdir()):
            raise exception

        archive_path = course_dir.with_suffix('.zip')
        shutil.make_archive(str(course_dir), 'zip', root_dir=str(course_dir))

        return str(archive_path)

    async def delete_course(self, course_id: int, user_id: int):
        course = self.session.query(tables.Course).filter(
            tables.Course.id == course_id
        ).first()

        exception = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
        )
        if not course:
            raise exception

        exception = HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this course"
        )
        if course.creator_id != user_id:
            raise exception

        course_dir = Path(f"uploads/{course_id}")
        if course_dir.exists():
            shutil.rmtree(course_dir)

        self.session.delete(course)
        self.session.commit()

    async def update_course(self, course_id: int, course_data: models.CourseUpdate, user_id: int) -> models.Course:
        course = self.session.query(tables.Course).filter(
            tables.Course.id == course_id
        ).first()

        exception = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
        )
        if not course:
            raise exception

        exception = HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to update this course"
        )
        if course.creator_id != user_id:
            raise exception

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

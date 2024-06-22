import shutil
from pathlib import Path

from fastapi import Depends, HTTPException, status, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from .. import tables, models
from ..database import get_session

from typing import List
import torch
from sentence_transformers import SentenceTransformer, util

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)

# Загрузка предварительно обученной модели Sentence-BERT
sbert_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')


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

    async def recommend_courses(self, course_id: int) -> List[models.Course]:
        # Получаем текущий курс
        course = self.session.query(tables.Course).filter(
            tables.Course.id == course_id
        ).first()

        if not course:
            raise HTTPException(
                status_code=404,
                detail="Course not found"
            )

        # Получаем все курсы, кроме текущего
        all_courses = self.session.query(tables.Course).filter(
            tables.Course.id != course_id
        ).all()

        if not all_courses:
            raise HTTPException(
                status_code=404,
                detail="No other courses found"
            )

        # Собираем текстовые описания всех курсов (включая текущий)
        descriptions = [course.description] + [other_course.description for other_course in all_courses]

        # Получаем эмбеддинги текстов с помощью Sentence-BERT
        embeddings = sbert_model.encode(descriptions, convert_to_tensor=True)

        # Вычисляем косинусное сходство между текущим курсом и всеми остальными курсами
        similarity_scores = util.pytorch_cos_sim(embeddings[0], embeddings[1:])

        # Получаем индексы курсов, с которыми текущий курс имеет наибольшее сходство
        similar_indices = similarity_scores.argsort(descending=True)[0][:3].cpu().numpy()  # берем 3 наиболее похожих курсов

        # Формируем список рекомендуемых курсов
        recommended_courses = [all_courses[idx] for idx in similar_indices]

        return recommended_courses

    async def rate_course(self, course_id: int, rating: int, user_id: int):
        if rating < 1 or rating > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating must be between 1 and 5"
            )

        course = self.session.query(tables.Course).filter(tables.Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        existing_rating = self.session.query(tables.CourseRating).filter(
            tables.CourseRating.course_id == course_id,
            tables.CourseRating.user_id == user_id
        ).first()

        if existing_rating:
            existing_rating.rating = rating
        else:
            new_rating = tables.CourseRating(course_id=course_id, user_id=user_id, rating=rating)
            self.session.add(new_rating)

        self.session.commit()
        self._update_average_rating(course_id)

    def _update_average_rating(self, course_id: int):
        average_rating = self.session.query(func.avg(tables.CourseRating.rating)).filter(
            tables.CourseRating.course_id == course_id
        ).scalar()

        course = self.session.query(tables.Course).filter(tables.Course.id == course_id).first()
        course.average_rating = average_rating
        self.session.commit()

    async def get_all_courses(self) -> List[models.Course]:
        courses = self.session.query(tables.Course).all()
        return [models.Course.from_orm(course) for course in courses]

    async def get_course_by_id(self, course_id: int):
        return self.session.query(tables.Course).filter(tables.Course.id == course_id).first()




from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import tables, models
from ..database import get_session


class CourseService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    async def create_new_course(self, course: models.CourseCreate, user_id: int) -> tables.Course:
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

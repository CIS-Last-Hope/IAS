from typing import Optional

from pydantic import BaseModel


class Lesson(BaseModel):
    course_id: int
    lesson_id: int
    filename: str

    class Config:
        from_attributes = True


class BaseCourse(BaseModel):
    title: str
    description: str

    class Config:
        from_attributes = True


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class Course(BaseCourse):
    id: int
    creator_id: int


class RateCourse(BaseModel):
    rating: int

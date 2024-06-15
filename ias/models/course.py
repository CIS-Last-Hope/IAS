from typing import Optional

from pydantic import BaseModel


class BaseCourse(BaseModel):
    title: str
    description: str


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class Course(BaseCourse):
    id: int
    creator_id: int

    class Config:
        from_attributes = True

class RateCourse(BaseModel):
    rating: int

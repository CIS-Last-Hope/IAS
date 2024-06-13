from typing import Optional

from pydantic import BaseModel


class BaseCourse(BaseModel):
    title: str
    description: str


class CourseCreate(BaseCourse):
    creator_id: int
    
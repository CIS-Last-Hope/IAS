from fastapi import APIRouter, Depends

from ..models import BaseCourse, User
from ..services.auth import get_current_user
from ..services.course import CourseService

router = APIRouter(
    prefix='/course',
)


@router.post('/create')
async def create_course(course_data: BaseCourse,
                        current_user: User = Depends(get_current_user),
                        service: CourseService = Depends()):
    return await service.create_new_course(course_data, current_user.id)


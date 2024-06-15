from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse

from ..models import BaseCourse, User, CourseUpdate, Course
from ..services.auth import get_current_user
from ..services.course import CourseService

from typing import List


router = APIRouter(
    prefix='/course',
)


@router.post('/create', response_model=Course)
async def create_course(course_data: BaseCourse,
                        current_user: User = Depends(get_current_user),
                        service: CourseService = Depends()):
    return await service.create_new_course(course_data, current_user.id)


@router.post('/{course_id}/materials/upload', response_model=dict)
async def upload_material(course_id: int,
                          file: UploadFile = File(...),
                          current_user: User = Depends(get_current_user),
                          service: CourseService = Depends()):
    return await service.upload_file(course_id, file, current_user.id)


@router.get('/{course_id}/materials/download', response_class=FileResponse)
async def download_material(course_id: int,
                            current_user: User = Depends(get_current_user),
                            service: CourseService = Depends()):
    archive_path = await service.download_file(course_id, current_user.id)
    return FileResponse(path=archive_path, filename=f"course_{course_id}_materials.zip")


@router.delete('/{course_id}', status_code=204)
async def delete_course(course_id: int,
                        current_user: User = Depends(get_current_user),
                        service: CourseService = Depends()):
    await service.delete_course(course_id, current_user.id)
    return {"detail": "Course deleted successfully"}


@router.put('/{course_id}', response_model=Course)
async def update_course(course_id: int,
                        course_data: CourseUpdate,
                        current_user: User = Depends(get_current_user),
                        service: CourseService = Depends()):
    return await service.update_course(course_id, course_data, current_user.id)

@router.get('/{course_id}/recommendations', response_model=List[Course])
async def get_recommendations(course_id: int,
                              current_user: User = Depends(get_current_user),
                              service: CourseService = Depends()):
    try:
        recommended_courses = await service.recommend_courses(course_id)
        return recommended_courses
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})

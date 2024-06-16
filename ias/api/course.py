from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse, JSONResponse

from ..models import BaseCourse, User, CourseUpdate, Course, RateCourse
from ..services.auth import get_current_user
from ..services.course import CourseService
from ..database import get_session
from sqlalchemy.orm import Session

from typing import List


router = APIRouter(
    prefix='/course',
)

@router.get('/', response_model=List[Course])
async def get_all_courses(
    current_user: User = Depends(get_current_user),
    service: CourseService = Depends()
):
    try:
        courses = await service.get_all_courses()
        return courses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

@router.get('/{course_id}', response_model=Course)
async def get_course_details(course_id: int,
                             current_user: User = Depends(get_current_user),
                             service: CourseService = Depends()):
    try:
        course = await service.get_course_by_id(course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        return course
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

@router.post('/{course_id}/rate', status_code=200)
async def rate_course(course_id: int,
                      rating: RateCourse,
                      current_user: User = Depends(get_current_user),
                      service: CourseService = Depends()):
    await service.rate_course(course_id, rating.rating, current_user.id)
    return {"detail": "Rating added successfully"}

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, status, UploadFile, File
from fastapi.responses import StreamingResponse

from ..models.admin import (
    AdminCreate,
    AdminToken,
    Admin
)

from ..models.course import Course, CourseUpdate, BaseCourse, Lesson

from ..services.admin import get_current_user, AuthAdminService, AdminModeration

from typing import List

router = APIRouter(
    prefix='/admin',
)


@router.post('/sign-up/', response_model=AdminToken, status_code=status.HTTP_201_CREATED)
async def sign_up(admin_data: AdminCreate, admin_code: str, auth_service: AuthAdminService = Depends()):
    return await auth_service.register_new_admin(admin_data, admin_code)


@router.post('/sign-in/', response_model=AdminToken)
async def sign_in(auth_data: OAuth2PasswordRequestForm = Depends(), auth_service: AuthAdminService = Depends()):
    return await auth_service.authenticate_admin(auth_data.username, auth_data.password)


@router.get('/admin/', response_model=Admin)
async def get_user(admin: Admin = Depends(get_current_user)):
    return await admin


@router.post('/admin/course/create/', response_model=Course)
async def create_course(course_data: BaseCourse, admin_service: AdminModeration = Depends(),
                        admin: Admin = Depends(get_current_user)):
    return await admin_service.create_course(course_data)


@router.get('/admin/course/', response_model=List[Course])
async def read_all_courses(admin_service: AdminModeration = Depends(), admin: Admin = Depends(get_current_user)):
    return await admin_service.read_all_courses()

@router.get('/admin/course/read/', response_model=Course)
async def read_course(title: str, admin_service: AdminModeration = Depends(), admin: Admin = Depends(get_current_user)):
    return await admin_service.read_course(title)


@router.put('/admin/course/update/', response_model=Course)
async def update_course(title: str, course_data: CourseUpdate, admin_service: AdminModeration = Depends(),
                        admin: Admin = Depends(get_current_user)):
    return await admin_service.update_course(title, course_data)


@router.delete('/admin/course/delete/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(title: str, admin_service: AdminModeration = Depends(), admin: Admin = Depends(get_current_user)):
    return await admin_service.delete_course(title)


@router.post('/admin/lesson/create/', response_model=Lesson)
async def create_lesson(course_id: int, lesson_id: int, file: UploadFile = File(...), admin_service: AdminModeration = Depends(),
                        admin: Admin = Depends(get_current_user)):
    return await admin_service.create_lesson(course_id, lesson_id, file)


@router.get('/admin/lesson/read/')
async def read_lesson(course_id: int, lesson_id: int, admin_service: AdminModeration = Depends(),
                      admin: Admin = Depends(get_current_user)):
    file, mime_type = await admin_service.read_lesson(course_id, lesson_id)
    return StreamingResponse(content=file, media_type=mime_type)

@router.get('/admin/{course_id}/lessons')
async def get_all_lessons_in_course(course_id: int,
                                    admin: Admin = Depends(get_current_user),
                                    admin_service: AdminModeration = Depends()):
    return await admin_service.get_all_lessons(course_id)

@router.delete('/admin/lesson/delete/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson(course_id: int, lesson_id: int, admin_service: AdminModeration = Depends(),
                        admin: Admin = Depends(get_current_user)):
    return await admin_service.delete_lesson(course_id, lesson_id)


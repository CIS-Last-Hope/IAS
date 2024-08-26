from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, status

from ..models.admin import (
    AdminCreate,
    AdminToken,
    Admin
)
from ..services.admin import get_current_user, AuthAdminService

router = APIRouter(
    prefix='/admin',
)


@router.post('/sign-up/', response_model=AdminToken, status_code=status.HTTP_201_CREATED)
def sign_up(admin_data: AdminCreate, auth_service: AuthAdminService = Depends()):
    return auth_service.register_new_admin(admin_data)


@router.post('/sign-in/', response_model=AdminToken)
def sign_in(auth_data: OAuth2PasswordRequestForm = Depends(), auth_service: AuthAdminService = Depends(),):
    return auth_service.authenticate_admin(auth_data.username, auth_data.password)


@router.get('/user/', response_model=Admin)
def get_user(admin: Admin = Depends(get_current_user)):
    return admin


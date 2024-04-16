from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse

from ..models.auth import (
    User,
    UserCreate,
    Token,
)
from ..services.auth import AuthService, get_current_user

router = APIRouter(
    prefix='/auth',
)


@router.post('/sign-up', response_model=Token)
async def sign_up(user_data: UserCreate, service: AuthService = Depends()):
    return await service.register_new_user(user_data)


@router.post('/qr')
async def get_qr_code(form_data: OAuth2PasswordRequestForm = Depends(), service: AuthService = Depends()):
    return StreamingResponse(await service.generate_qr(form_data.username), media_type="image/png")


@router.post('/sign-in')
async def sign_in(form_data: OAuth2PasswordRequestForm = Depends(), service: AuthService = Depends()):
    return await service.authenticate_user(
        form_data.username,
        form_data.password
    )


@router.post('/verify-otp', response_model=Token)
async def verify_otp(username: str, otp_code: str, service: AuthService = Depends()):
    return await service.verify_otp(username, otp_code)


@router.get('/user', response_model=User)
def get_user(user: User = Depends(get_current_user)):
    return user

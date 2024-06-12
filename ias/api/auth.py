from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse

from ..models.auth import (
    User,
    UserCreate,
    Token,
)
from ..services.auth import AuthService

router = APIRouter(
    prefix='/auth',
)


@router.post('/sign-up')
async def sign_up(user_data: UserCreate, service: AuthService = Depends()):
    return await service.register_new_user(user_data)


@router.post('/qr')
async def get_qr_code(session_id: str, service: AuthService = Depends()):
    return StreamingResponse(await service.generate_qr(session_id), media_type="image/png")


@router.post('/sign-in')
async def sign_in(form_data: OAuth2PasswordRequestForm = Depends(), service: AuthService = Depends()):
    return await service.authenticate_user(
        form_data.username,
        form_data.password
    )


@router.post('/verify-otp', response_model=Token)
async def verify_otp(session_id: str, otp_code: str, service: AuthService = Depends()):
    return await service.verify_otp(session_id, otp_code)



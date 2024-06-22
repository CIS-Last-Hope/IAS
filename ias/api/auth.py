from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse, JSONResponse

from ..models.auth import (
    UserCreate,
    Token,
    User
)
from ..services.auth import AuthService, get_current_user

router = APIRouter(
    prefix='/auth',
)

@router.get('/current-user', response_model=User)
async def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user

@router.post('/sign-up', response_model=dict)
async def sign_up(user_data: UserCreate, service: AuthService = Depends()):
    session_id = await service.register_new_user(user_data)
    return JSONResponse(content={"session_id": session_id})


@router.get('/qr')
async def get_qr_code(session_id: str, service: AuthService = Depends()):
    try:
        return StreamingResponse(await service.generate_qr(session_id), media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/sign-in')
async def sign_in(form_data: OAuth2PasswordRequestForm = Depends(), service: AuthService = Depends()):
    session_id = await service.authenticate_user(
        form_data.username,
        form_data.password
    )
    return JSONResponse(content={"session_id": session_id})


@router.post('/verify-otp', response_model=Token)
async def verify_otp(session_id: str, otp_code: str, service: AuthService = Depends()):
    return await service.verify_otp(session_id, otp_code)



import base64
import os
import secrets
from datetime import datetime, timedelta

import pyqrcode as pyqrcode
from pyotp import TOTP
from io import BytesIO

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.hash import bcrypt
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from .. import tables, models
from ..database import get_session
from ..settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/sign-in')


class AuthService:
    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.verify(plain_password, hashed_password)

    @classmethod
    def hash_password(cls, password: str) -> str:
        return bcrypt.hash(password)

    @classmethod
    def validate_token(cls, token: str) -> models.User:
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={
                'WWW-Authenticate': 'Bearer'
            },
        )

        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=[settings.jwt_algorithm],
            )
        except JWTError:
            raise exception from None

        user_data = payload.get('user')

        try:
            user = models.User.parse_obj(user_data)
        except ValueError:
            raise exception from None

        return user

    @classmethod
    def create_token(cls, user: tables.User) -> models.Token:
        user_data = models.User.model_validate(user)

        now = datetime.utcnow()

        payload = {
            'iat': now,
            'nbf': now,
            'exp': now + timedelta(seconds=settings.jwt_exepiration),
            'sub': str(user_data.id),
            'user': user_data.dict()
        }
        token = jwt.encode(
            payload,
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm,
        )

        return models.Token(access_token=token)

    def save_session(self, session_id: str, user_id: int):
        session = tables.Session(id=session_id, user_id=user_id)
        self.session.add(session)
        self.session.commit()

    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    async def register_new_user(self, user_data: models.UserCreate):
        existing_user = self.session.query(tables.User).filter(
            (tables.User.username == user_data.username) |
            (tables.User.email == user_data.email)
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this username or email already exists"
            )

        user = tables.User(
            email=user_data.email,
            username=user_data.username,
            password_hash=self.hash_password(user_data.password),
            google_auth_secret=base64.b32encode(os.urandom(10)).decode('utf-8'),
        )

        try:
            self.session.add(user)
            self.session.commit()
        except ValueError:
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this username or email already exists"
            )
        session_id = secrets.token_hex(16)
        self.save_session(session_id, user.id)
        return session_id

    async def authenticate_user(self, username: str, password: str):
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={
                'WWW-Authenticate': 'Bearer'
            },
        )

        user = (
            self.session
            .query(tables.User)
            .filter(tables.User.username == username)
            .first()
        )
        if not user:
            raise exception

        if not self.verify_password(password, user.password_hash):
            raise exception

        session_id = secrets.token_hex(16)
        self.save_session(session_id, user.id)
        return session_id

    async def generate_qr(self, session_id: str) -> BytesIO:
        user_id = (
            self.session
            .query(tables.Session.user_id)
            .filter(tables.Session.id == session_id)
            .scalar()
        )

        user = (
            self.session
            .query(tables.User)
            .filter(tables.User.id == user_id)
            .first()
        )
        uri = f'otpauth://totp/MyApp:{user.username}?secret={user.google_auth_secret}&issuer=MyApp'
        url = pyqrcode.create(uri)
        stream = BytesIO()
        url.png(stream, scale=3)
        stream.seek(0)
        return stream

    async def verify_otp(self, session_id: str, otp: str) -> models.Token:
        user_id = (
            self.session
            .query(tables.Session.user_id)
            .filter(tables.Session.id == session_id)
            .scalar()
        )

        user = (
            self.session
            .query(tables.User)
            .filter(tables.User.id == user_id)
            .first()
        )
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect otp',
            headers={
                'WWW-Authenticate': 'Bearer'
            },
        )
        user_secret = user.google_auth_secret
        totp = TOTP(user_secret)
        if not totp.verify(otp):
            raise exception
        return self.create_token(user)

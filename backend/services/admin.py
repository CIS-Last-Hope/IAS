from datetime import (
    datetime,
    timedelta,
)

from fastapi import (
    Depends,
    HTTPException,
    status,
)

from fastapi.security import OAuth2PasswordBearer
from jose import (
    JWTError,
    jwt,
)

from passlib.hash import bcrypt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from .. import (
    models,
    tables,
)

from ..database import get_session
from ..settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/admin/sign-in/')


def get_current_user(token: str = Depends(oauth2_scheme)) -> models.Admin:
    return AuthAdminService.verify_token(token)


class AuthAdminService:
    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.verify(plain_password, hashed_password)

    @classmethod
    def hash_password(cls, password: str) -> str:
        return bcrypt.hash(password)

    @classmethod
    def verify_token(cls, token: str) -> models.Admin:
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=[settings.jwt_algorithm],
            )
        except JWTError:
            raise exception from None

        admin_data = payload.get('admin')
        admin_flag = payload.get('is_admin')

        exception = HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Forbidden',
        )

        if not admin_flag:
            raise exception

        try:
            user = models.Admin.parse_obj(admin_data)
        except ValidationError:
            raise exception from None

        return user

    @classmethod
    def create_token(cls, admin: tables.Admin) -> models.AdminToken:
        admin_data = models.Admin.from_orm(admin)
        now = datetime.utcnow()
        payload = {
            'iat': now,
            'nbf': now,
            'exp': now + timedelta(seconds=settings.jwt_expiration),
            'sub': str(admin_data.id),
            'admin': admin_data.dict(),
            'is_admin': True
        }
        token = jwt.encode(
            payload,
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm,
        )
        return models.AdminToken(access_token=token)

    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def register_new_admin(self, admin_data: models.AdminCreate) -> models.AdminToken:
        admin = tables.Admin(
            email=admin_data.email,
            username=admin_data.username,
            password_hash=self.hash_password(admin_data.password),
        )
        self.session.add(admin)
        self.session.commit()
        return self.create_token(admin)

    def authenticate_admin(self, username: str, password: str) -> models.AdminToken:
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )

        admin = (
            self.session
            .query(tables.Admin)
            .filter(tables.Admin.username == username)
            .first()
        )

        if not admin:
            raise exception

        if not self.verify_password(password, admin.password_hash):
            raise exception

        return self.create_token(admin)
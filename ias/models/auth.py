from typing import Optional

from pydantic import BaseModel


class BaseUser(BaseModel):
    email: str
    username: str


class UserCreate(BaseUser):
    password: str


class User(BaseUser):
    id: Optional[int]
    google_auth_secret: Optional[str]

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'

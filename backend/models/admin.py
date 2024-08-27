from pydantic import BaseModel


class BaseAdmin(BaseModel):
    email: str
    username: str


class AdminCreate(BaseAdmin):
    password: str


class Admin(BaseAdmin):
    id: int

    class Config:
        from_attributes = True


class AdminToken(BaseModel):
    access_token: str
    token_type: str = 'bearer'


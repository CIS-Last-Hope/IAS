from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    server_host: str
    server_port: int
    database_url: str

    jwt_secret: str
    jwt_algorithm: str
    jwt_expiration: int

    api_key_antivirus: str

    admin_code: str


settings = Settings(
    _env_file='backend/.env',
    _env_file_encoding='utf-8',
)

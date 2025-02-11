from async_fastapi_jwt_auth import AuthJWT
from dotenv import find_dotenv, load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(find_dotenv())


class DefaultSettings(BaseSettings):
    """Class to store default project settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class AppSettings(DefaultSettings):
    name: str = Field(...)
    host: str = Field(...)
    port: int = Field(...)
    root_path: str = Field(...)
    base_url: str = Field(...)
    health_check_path: str = Field(...)
    app: str = "main:app"
    debug: bool = Field(...)
    log_level: str = Field(...)

    model_config = SettingsConfigDict(env_prefix="APP_")


class ApiSettings(DefaultSettings):
    docs_url: str = Field(...)
    openapi_url: str = Field(...)
    version: str = Field(...)
    blacklist: str = Field(...)

    model_config = SettingsConfigDict(env_prefix="API_")


class PGSettings(DefaultSettings):
    db: str = Field(...)
    user: str = Field(...)
    password: str = Field(...)
    host: str = Field(...)
    port: int = Field(...)
    dsn: str = Field(...)
    dsn_local: str = Field(...)
    async_schema: str = Field(...)
    dsn_pg: str = Field(...)
    echo_sql_queries: bool = True

    model_config = SettingsConfigDict(env_prefix="POSTGRES_")


class Auth(DefaultSettings):
    max_age: int = Field(default=60 * 5, description="Max age of tokens in seconds")

    model_config = SettingsConfigDict(env_prefix="AUTH_")


class BackoffSettings(DefaultSettings):
    max_tries: int = Field(...)
    max_time: int = Field(...)

    model_config = SettingsConfigDict(env_prefix="BACKOFF_")


class JWTSettings(DefaultSettings):
    """Class to store JWT project settings."""

    permissions_enabled: bool = Field(default=False, description="Enable permissions check in JWT")
    authjwt_algorithm: str = Field(...)
    authjwt_secret_key: str = Field(...)
    authjwt_token_location: set[str] = {"cookies"}
    authjwt_cookie_csrf_protect: bool = False
    authjwt_access_token_expires: int = Field(...)

    model_config = SettingsConfigDict(env_prefix="JWT_")


class Settings(DefaultSettings):
    debug: bool = False
    app: AppSettings = AppSettings()
    api: ApiSettings = ApiSettings()
    pg: PGSettings = PGSettings()
    auth: Auth = Auth()
    backoff: BackoffSettings = BackoffSettings()


settings = Settings()


def get_settings() -> Settings:
    """Provide settings."""
    return settings


@AuthJWT.load_config
def get_config() -> JWTSettings:
    return JWTSettings()

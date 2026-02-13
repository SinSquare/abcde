"""Application configuration."""

from pydantic_settings import BaseSettings


class Config(BaseSettings, env_prefix="ABCDE_"):
    """App config model."""

    db_url: str = "sqlite:////tmp/database.db"

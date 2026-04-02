from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMINS: str = Field(default="")
    SQLITE_PATH: str = Field(default="sqlite+aiosqlite:///./food_order.db")
    TIMEZONE: str = Field(default="Asia/Tashkent")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def admin_ids(self) -> list[int]:
        if not self.ADMINS.strip():
            return []
        return [int(x.strip()) for x in self.ADMINS.split(",") if x.strip()]


settings = Settings()

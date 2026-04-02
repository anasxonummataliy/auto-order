from datetime import datetime, date
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, Integer, DateTime, Date
from sqlalchemy import Enum as SqlEnum

from app.db.base import Base
from app.db.models.enums import AccountStatus


class Account(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    phone: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    api_id: Mapped[int] = mapped_column(Integer, nullable=False)
    api_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    session_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    bot_username: Mapped[str] = mapped_column(String(255), nullable=False)

    order_time: Mapped[str] = mapped_column(String(5), default="18:00", nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_order_enabled: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    status: Mapped[AccountStatus] = mapped_column(
        SqlEnum(AccountStatus),
        default=AccountStatus.NEW,
        nullable=False,
    )

    last_order_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

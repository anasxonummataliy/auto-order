from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger
from app.db.base import Base


class Admin(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_user_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)

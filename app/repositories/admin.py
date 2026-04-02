from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Admin


class AdminRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_tg_user_id(self, tg_user_id: int) -> Admin | None:
        stmt = select(Admin).where(Admin.tg_user_id == tg_user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, tg_user_id: int) -> Admin:
        admin = Admin(tg_user_id=tg_user_id)
        self.session.add(admin)
        await self.session.commit()
        await self.session.refresh(admin)
        return admin

    async def exists(self, tg_user_id: int) -> bool:
        admin = await self.get_by_tg_user_id(tg_user_id)
        return admin is not None

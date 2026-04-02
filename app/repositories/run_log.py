from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import RunLog


class RunLogRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self, account_id: int, success: bool, message: str | None = None
    ) -> RunLog:
        log = RunLog(
            account_id=account_id,
            success=success,
            message=message,
        )
        self.session.add(log)
        await self.session.commit()
        await self.session.refresh(log)
        return log

    async def get_last_logs(self, limit: int = 20) -> list[RunLog]:
        stmt = select(RunLog).order_by(RunLog.id.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

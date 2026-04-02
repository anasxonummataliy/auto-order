from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Account, AccountStatus


class AccountRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        phone: str,
        api_id: int,
        api_hash: str,
        session_name: str,
        bot_username: str,
        order_time: str,
    ) -> Account:
        account = Account(
            phone=phone,
            api_id=api_id,
            api_hash=api_hash,
            session_name=session_name,
            bot_username=bot_username,
            order_time=order_time,
            status=AccountStatus.NEW,
            is_active=True,
            is_order_enabled=False,
        )
        self.session.add(account)
        await self.session.commit()
        await self.session.refresh(account)
        return account

    async def get_all(self) -> list[Account]:
        stmt = select(Account).order_by(Account.id.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, account_id: int) -> Account | None:
        stmt = select(Account).where(Account.id == account_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_phone(self, phone: str) -> Account | None:
        stmt = select(Account).where(Account.phone == phone)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def set_order_enabled(self, account_id: int, enabled: bool) -> Account | None:
        account = await self.get_by_id(account_id)
        if not account:
            return None

        account.is_order_enabled = enabled
        await self.session.commit()
        await self.session.refresh(account)
        return account

    async def update_order_time(
        self, account_id: int, order_time: str
    ) -> Account | None:
        account = await self.get_by_id(account_id)
        if not account:
            return None

        account.order_time = order_time
        await self.session.commit()
        await self.session.refresh(account)
        return account

    async def update_status(
        self, account_id: int, status: AccountStatus
    ) -> Account | None:
        account = await self.get_by_id(account_id)
        if not account:
            return None

        account.status = status
        await self.session.commit()
        await self.session.refresh(account)
        return account

    async def get_enabled_for_scheduler(self) -> list[Account]:
        stmt = select(Account).where(
            Account.is_active == True,  # noqa: E712
            Account.is_order_enabled == True,  # noqa: E712
            Account.status == AccountStatus.ACTIVE,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

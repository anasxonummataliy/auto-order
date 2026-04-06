from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.bot.states import LoginState
from app.db.models import AccountStatus
from app.db.session import AsyncSessionLocal
from app.repositories import AccountRepository
from app.services.account_auth import AccountAuthService

router = Router()


@router.callback_query(lambda c: c.data.startswith("send_code:"))
async def send_code_handler(callback: CallbackQuery, state: FSMContext):
    account_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        repo = AccountRepository(session)
        account = await repo.get_by_id(account_id)

        if not account:
            await callback.answer("Account topilmadi.", show_alert=True)
            return

        auth_service = AccountAuthService(account)
        result = await auth_service.send_code()

        if not result["success"]:
            await repo.update_status(account.id, AccountStatus.ERROR)
            await callback.message.answer(result["message"])
            await callback.answer()
            return

        await repo.update_status(account.id, AccountStatus.CODE_SENT)

        await state.update_data(
            login_account_id=account.id,
            phone_code_hash=result["phone_code_hash"],
        )

    await callback.message.answer(
        f"📨 Kod yuborildi: {account.phone}\n"
        f"Endi '🔑 Kodni kiritish' tugmasini bosing."
    )
    await callback.answer("Kod yuborildi")


@router.callback_query(lambda c: c.data.startswith("enter_code:"))
async def enter_code_start_handler(callback: CallbackQuery, state: FSMContext):
    account_id = int(callback.data.split(":")[1])

    await state.update_data(login_account_id=account_id)
    await state.set_state(LoginState.waiting_code)

    await callback.message.answer(
        "Telegramga kelgan kodni yuboring.\n" "Masalan: 12345"
    )
    await callback.answer()


@router.message(LoginState.waiting_code)
async def enter_code_handler(message: Message, state: FSMContext):
    code = message.text.strip()
    data = await state.get_data()

    account_id = data.get("login_account_id")
    phone_code_hash = data.get("phone_code_hash")

    if not account_id or not phone_code_hash:
        await message.answer("Session ma'lumotlari topilmadi. Qaytadan kod yuboring.")
        await state.clear()
        return

    async with AsyncSessionLocal() as session:
        repo = AccountRepository(session)
        account = await repo.get_by_id(account_id)

        if not account:
            await message.answer("Account topilmadi.")
            await state.clear()
            return

        auth_service = AccountAuthService(account)
        result = await auth_service.confirm_code(
            code=code,
            phone_code_hash=phone_code_hash,
        )

        if result.get("success"):
            await repo.update_status(account.id, AccountStatus.ACTIVE)
            await repo.set_active_flag(account.id, True)

            await message.answer(
                f"✅ Account aktiv qilindi.\n\n"
                f"Phone: {account.phone}\n"
                f"Status: active"
            )
            await state.clear()
            return

        if result.get("need_password"):
            await state.set_state(LoginState.waiting_password)
            await message.answer("2FA parolni yuboring:")
            return

        await repo.update_status(account.id, AccountStatus.ERROR)
        await message.answer(result["message"])
        await state.clear()


@router.message(LoginState.waiting_password)
async def enter_password_handler(message: Message, state: FSMContext):
    password = message.text.strip()
    data = await state.get_data()

    account_id = data.get("login_account_id")
    if not account_id:
        await message.answer("Account topilmadi.")
        await state.clear()
        return

    async with AsyncSessionLocal() as session:
        repo = AccountRepository(session)
        account = await repo.get_by_id(account_id)

        if not account:
            await message.answer("Account topilmadi.")
            await state.clear()
            return

        auth_service = AccountAuthService(account)
        result = await auth_service.confirm_password(password)

        if result.get("success"):
            await repo.update_status(account.id, AccountStatus.ACTIVE)
            await repo.set_active_flag(account.id, True)

            await message.answer(
                f"✅ 2FA orqali account aktiv qilindi.\n\n"
                f"Phone: {account.phone}\n"
                f"Status: active"
            )
            await state.clear()
            return

        await repo.update_status(account.id, AccountStatus.ERROR)
        await message.answer(result["message"])
        await state.clear()

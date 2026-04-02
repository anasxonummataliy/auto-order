from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.bot.states import AddAccountState
from app.bot.keyboards.inline import (
    account_detail_keyboard,
    account_list_keyboard,
)
from app.db.session import AsyncSessionLocal
from app.repositories import AccountRepository

router = Router()


@router.callback_query(lambda c: c.data == "add_account")
async def add_account_start(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(AddAccountState.phone)
    await callback.message.answer("Telefon raqamni yuboring. Masalan: +998901234567")
    await callback.answer()


@router.message(AddAccountState.phone)
async def add_account_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    await state.update_data(phone=phone)
    await state.set_state(AddAccountState.api_id)
    await message.answer("API_ID ni yuboring:")


@router.message(AddAccountState.api_id)
async def add_account_api_id(message: Message, state: FSMContext):
    try:
        api_id = int(message.text.strip())
    except ValueError:
        await message.answer("API_ID son bo'lishi kerak.")
        return

    await state.update_data(api_id=api_id)
    await state.set_state(AddAccountState.api_hash)
    await message.answer("API_HASH ni yuboring:")


@router.message(AddAccountState.api_hash)
async def add_account_api_hash(message: Message, state: FSMContext):
    api_hash = message.text.strip()
    await state.update_data(api_hash=api_hash)
    await state.set_state(AddAccountState.bot_username)
    await message.answer("BOT_USERNAME ni yuboring. Masalan: food_bot")


@router.message(AddAccountState.bot_username)
async def add_account_bot_username(message: Message, state: FSMContext):
    bot_username = message.text.strip().replace("@", "")
    await state.update_data(bot_username=bot_username)
    await state.set_state(AddAccountState.order_time)
    await message.answer("Buyurtma vaqtini yuboring. Masalan: 18:00")


@router.message(AddAccountState.order_time)
async def add_account_order_time(message: Message, state: FSMContext):
    order_time = message.text.strip()

    if len(order_time) != 5 or ":" not in order_time:
        await message.answer("Vaqt noto'g'ri formatda. Masalan: 18:00")
        return

    data = await state.get_data()

    session_name = f"sessions/account_{data['phone'].replace('+', '')}"

    async with AsyncSessionLocal() as session:
        repo = AccountRepository(session)

        existing = await repo.get_by_phone(data["phone"])
        if existing:
            await message.answer("Bu phone bilan account allaqachon mavjud.")
            await state.clear()
            return

        account = await repo.create(
            phone=data["phone"],
            api_id=data["api_id"],
            api_hash=data["api_hash"],
            session_name=session_name,
            bot_username=data["bot_username"],
            order_time=order_time,
        )

    await state.clear()
    await message.answer(
        f"Account qo'shildi.\n\n"
        f"ID: {account.id}\n"
        f"Phone: {account.phone}\n"
        f"Bot: @{account.bot_username}\n"
        f"Vaqt: {account.order_time}\n"
        f"Status: {account.status.value}"
    )


@router.callback_query(lambda c: c.data == "accounts_list")
async def accounts_list_handler(callback: CallbackQuery):
    async with AsyncSessionLocal() as session:
        repo = AccountRepository(session)
        accounts = await repo.get_all()

    if not accounts:
        await callback.message.edit_text(
            "Hozircha accountlar yo'q.",
            reply_markup=account_list_keyboard([]),
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        "Accountlar ro'yxati:",
        reply_markup=account_list_keyboard(accounts),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("account_detail:"))
async def account_detail_handler(callback: CallbackQuery):
    account_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        repo = AccountRepository(session)
        account = await repo.get_by_id(account_id)

    if not account:
        await callback.answer("Account topilmadi.", show_alert=True)
        return

    text = (
        f"Account ma'lumotlari:\n\n"
        f"ID: {account.id}\n"
        f"Phone: {account.phone}\n"
        f"Bot: @{account.bot_username}\n"
        f"Order time: {account.order_time}\n"
        f"Order enabled: {account.is_order_enabled}\n"
        f"Status: {account.status.value}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=account_detail_keyboard(account.id, account.is_order_enabled),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("enable:"))
async def enable_account_handler(callback: CallbackQuery):
    account_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        repo = AccountRepository(session)
        account = await repo.set_order_enabled(account_id, True)

    if not account:
        await callback.answer("Account topilmadi.", show_alert=True)
        return

    await callback.message.edit_text(
        f"✅ Yoqildi\n\n"
        f"Phone: {account.phone}\n"
        f"Vaqt: {account.order_time}\n"
        f"Status: {account.status.value}",
        reply_markup=account_detail_keyboard(account.id, account.is_order_enabled),
    )
    await callback.answer("Yoqildi")


@router.callback_query(lambda c: c.data.startswith("disable:"))
async def disable_account_handler(callback: CallbackQuery):
    account_id = int(callback.data.split(":")[1])

    async with AsyncSessionLocal() as session:
        repo = AccountRepository(session)
        account = await repo.set_order_enabled(account_id, False)

    if not account:
        await callback.answer("Account topilmadi.", show_alert=True)
        return

    await callback.message.edit_text(
        f"⛔ O'chirildi\n\n"
        f"Phone: {account.phone}\n"
        f"Vaqt: {account.order_time}\n"
        f"Status: {account.status.value}",
        reply_markup=account_detail_keyboard(account.id, account.is_order_enabled),
    )
    await callback.answer("O'chirildi")

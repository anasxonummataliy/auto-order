from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from app.bot.keyboards.inline import main_menu_keyboard

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "Admin panelga xush kelibsiz.",
        reply_markup=main_menu_keyboard(),
    )


@router.callback_query(lambda c: c.data == "back_main")
async def back_main_handler(callback: CallbackQuery):
    await callback.message.edit_text(
        "Admin panelga xush kelibsiz.",
        reply_markup=main_menu_keyboard(),
    )
    await callback.answer()

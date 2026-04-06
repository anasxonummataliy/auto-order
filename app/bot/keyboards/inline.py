from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.db.models import Account


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Account qo'shish", callback_data="add_account"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📋 Accountlar", callback_data="accounts_list"
                ),
            ],
        ]
    )


def account_list_keyboard(accounts: list[Account]) -> InlineKeyboardMarkup:
    keyboard = []

    for account in accounts:
        status_emoji = "🟢" if account.is_order_enabled else "🔴"
        text = f"{status_emoji} {account.phone} | {account.order_time}"
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=text, callback_data=f"account_detail:{account.id}"
                )
            ]
        )

    keyboard.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_main")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.db.models import Account


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Account qo'shish", callback_data="add_account"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📋 Accountlar", callback_data="accounts_list"
                ),
            ],
        ]
    )


def account_list_keyboard(accounts: list[Account]) -> InlineKeyboardMarkup:
    keyboard = []

    for account in accounts:
        status_emoji = "🟢" if account.is_order_enabled else "🔴"
        text = f"{status_emoji} {account.phone} | {account.order_time}"
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=text, callback_data=f"account_detail:{account.id}"
                )
            ]
        )

    keyboard.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_main")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def account_detail_keyboard(account_id: int, is_enabled: bool) -> InlineKeyboardMarkup:
    toggle_text = "⛔ O'chirish" if is_enabled else "✅ Yoqish"
    toggle_action = "disable" if is_enabled else "enable"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=toggle_text, callback_data=f"{toggle_action}:{account_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📨 Kod yuborish", callback_data=f"send_code:{account_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔑 Kodni kiritish", callback_data=f"enter_code:{account_id}"
                )
            ],
            [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="accounts_list")],
        ]
    )

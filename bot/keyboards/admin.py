from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def admin_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📡 Sources",
                    callback_data="admin:sources",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 Subscriptions",
                    callback_data="admin:subs",
                )
            ],
        ]
    )

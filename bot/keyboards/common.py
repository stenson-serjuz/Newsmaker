from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Back", callback_data="nav:back")]
        ]
    )

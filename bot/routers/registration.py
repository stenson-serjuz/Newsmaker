from aiogram import Router
from aiogram.types import Message


router = Router(name="registration")


@router.message()
async def auto_register_chat(message: Message) -> None:
    """
    Auto registration:

    - triggered when bot added to chat
    - future: call registration service
    """
    if message.chat.type in ("group", "supergroup", "channel"):
        await message.answer("Chat registered.")

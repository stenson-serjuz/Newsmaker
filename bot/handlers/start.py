from aiogram import Router
from aiogram.types import Message

router = Router(name="start")


@router.message(commands=["start"])
async def start_handler(message: Message) -> None:
    await message.answer("Welcome. Use menu to manage your settings.")

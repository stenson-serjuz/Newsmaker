# bot/handlers/start.py

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="start")


@router.message(Command("start"))
async def start_handler(message: Message) -> None:
    await message.answer("Welcome. Use menu to manage your settings.")

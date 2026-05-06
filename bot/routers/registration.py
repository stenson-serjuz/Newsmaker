from aiogram import Router, F
from aiogram.types import Message

router = Router(name="registration")


@router.message(F.new_chat_members)
async def register_chat(message: Message) -> None:
    """
    Silent registration:
    - no spam
    - only triggered on bot add
    """
    for user in message.new_chat_members:
        if user.is_bot:
            # future: call registration service
            return


@router.message(F.text == "/add")
async def register_topic(message: Message) -> None:
    """
    Topic registration flow:
    - must be inside topic/thread
    """
    if not message.is_topic_message:
        return

    # future: bind topic
    await message.answer("Topic registered.", disable_notification=True)

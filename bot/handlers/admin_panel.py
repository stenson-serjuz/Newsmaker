from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.keyboards.admin import admin_main_keyboard
from bot.states.admin import AdminStates

router = Router(name="admin_panel")


@router.callback_query(lambda c: c.data == "admin:open")
async def open_admin_panel(
    call: CallbackQuery,
    state: FSMContext,
) -> None:
    await state.set_state(AdminStates.main)

    await call.message.edit_text(
        "Admin panel",
        reply_markup=admin_main_keyboard(),
    )

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.keyboards.admin import admin_main_keyboard
from bot.states.admin import AdminStates

router = Router(name="admin_panel")


@router.callback_query(F.data == "admin:open")
async def open_admin_panel(
    call: CallbackQuery,
    state: FSMContext,
) -> None:
    await state.set_state(AdminStates.main)

    await call.message.edit_text(
        "Admin panel",
        reply_markup=admin_main_keyboard(),
    )


@router.callback_query(F.data == "nav:back")
async def handle_back(
    call: CallbackQuery,
    state: FSMContext,
) -> None:
    await state.clear()

    await call.message.edit_text("Back to main menu")

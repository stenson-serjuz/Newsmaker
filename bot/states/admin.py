from aiogram.fsm.state import StatesGroup, State


class AdminStates(StatesGroup):
    main = State()
    managing_sources = State()

from aiogram import Router


def build_base_router() -> Router:
    router = Router(name="base")
    return router

from aiogram import Router


def build_superuser_router() -> Router:
    router = Router(name="superuser")
    return router

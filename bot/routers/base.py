from aiogram import Router

from bot.routers.admin import build_admin_router
from bot.routers.registration import router as registration_router
from bot.handlers.start import router as start_router


def build_root_router() -> Router:
    router = Router(name="root")

    router.include_router(start_router)
    router.include_router(registration_router)
    router.include_router(build_admin_router())

    return router

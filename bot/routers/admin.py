from aiogram import Router

from bot.handlers.admin_panel import router as admin_panel_router


def build_admin_router() -> Router:
    router = Router(name="admin")

    router.include_router(admin_panel_router)

    return router

from aiogram import Router

from . import apply, faq, menu, start

router = Router()
router.include_router(start.router)
router.include_router(menu.router)
router.include_router(faq.router)
router.include_router(apply.router)

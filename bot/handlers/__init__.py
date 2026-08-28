from aiogram import Router

from . import admin, apply, faq, menu, purchase, start

router = Router()
router.include_router(start.router)
router.include_router(menu.router)
router.include_router(faq.router)
router.include_router(apply.router)
router.include_router(purchase.router)
router.include_router(admin.router)

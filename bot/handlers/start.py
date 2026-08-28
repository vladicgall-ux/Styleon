from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from .. import content, content_store, keyboards
from ..config import is_admin

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    text = await content_store.get_text("welcome", content.WELCOME_TEXT)
    photo = await content_store.get_photo("welcome", content.WELCOME_PHOTO)
    await message.answer_photo(
        photo=content_store.to_input(photo),
        caption=text,
        reply_markup=keyboards.main_menu(is_admin=is_admin(message.from_user.id)),
    )


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    await message.answer(
        "Выбирай нужный раздел 👇",
        reply_markup=keyboards.main_menu(is_admin=is_admin(message.from_user.id)),
    )

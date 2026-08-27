from aiogram import Router
from aiogram.filters import Command
from aiogram.types import FSInputFile, Message

from .. import content, keyboards

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer_photo(
        photo=FSInputFile(content.WELCOME_PHOTO),
        caption=content.WELCOME_TEXT,
        reply_markup=keyboards.main_menu(),
    )


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    await message.answer(
        "Выбирай нужный раздел 👇",
        reply_markup=keyboards.main_menu(),
    )

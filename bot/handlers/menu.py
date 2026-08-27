from aiogram import F, Router
from aiogram.types import CallbackQuery, FSInputFile

from .. import content, keyboards

router = Router()


@router.callback_query(F.data == "menu")
async def show_menu(callback: CallbackQuery):
    await callback.message.answer("Выбирай нужный раздел 👇", reply_markup=keyboards.main_menu())
    await callback.answer()


@router.callback_query(F.data == "course")
async def show_course(callback: CallbackQuery):
    await callback.message.answer_photo(
        photo=FSInputFile(content.COURSE_PHOTO),
        caption=content.COURSE_TEXT,
        reply_markup=keyboards.course_menu(),
    )
    await callback.answer()


@router.callback_query(F.data == "format")
async def show_format(callback: CallbackQuery):
    await callback.message.answer_photo(
        photo=FSInputFile(content.FORMAT_PHOTO),
        caption=content.FORMAT_TEXT,
        reply_markup=keyboards.back_to_menu(),
    )
    await callback.answer()


@router.callback_query(F.data == "program")
async def show_program(callback: CallbackQuery):
    await callback.message.answer(content.PROGRAM_INTRO, reply_markup=keyboards.program_menu())
    await callback.answer()


@router.callback_query(F.data.startswith("program:"))
async def show_program_block(callback: CallbackQuery):
    key = callback.data.split(":", 1)[1]
    block = content.PROGRAM_BLOCKS[key]
    lines = [f"📚 <b>{block['title']}</b>\n"]
    for i, (title, desc) in enumerate(block["lessons"], start=1):
        lines.append(f"<b>{i}. {title}</b>\n{desc}")
    await callback.message.answer("\n\n".join(lines), reply_markup=keyboards.program_block_menu())
    await callback.answer()


@router.callback_query(F.data == "pricing")
async def show_pricing(callback: CallbackQuery):
    await send_tariff(callback, "listener")


@router.callback_query(F.data.startswith("pricing:"))
async def show_tariff(callback: CallbackQuery):
    key = callback.data.split(":", 1)[1]
    await send_tariff(callback, key)


async def send_tariff(callback: CallbackQuery, key: str):
    tariff = content.TARIFFS[key]
    lines = [f"💳 <b>{tariff['title']} — {tariff['price']}</b>\n", tariff["note"], ""]
    for feature in tariff["features"]:
        lines.append(f"— {feature}")
    await callback.message.answer("\n".join(lines), reply_markup=keyboards.pricing_menu(key))
    await callback.answer()


@router.callback_query(F.data == "teachers")
async def show_teachers(callback: CallbackQuery):
    await callback.message.answer(
        "👩‍🏫 <b>Преподаватели курса</b>\n\nУчитесь у практикующих стилистов. Выберите, о ком узнать подробнее:",
        reply_markup=keyboards.teachers_menu(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("teachers:"))
async def show_teacher_card(callback: CallbackQuery):
    key = callback.data.split(":", 1)[1]
    teacher = content.TEACHERS[key]
    caption = f"<b>{teacher['name']}</b>\n<i>{teacher['role']}</i>\n\n{teacher['text']}"
    await callback.message.answer_photo(
        photo=FSInputFile(teacher["photo"]),
        caption=caption,
        reply_markup=keyboards.teacher_card_menu(),
    )
    await callback.answer()


@router.callback_query(F.data == "about")
async def show_about(callback: CallbackQuery):
    await callback.message.answer_photo(
        photo=FSInputFile(content.ABOUT_PHOTO),
        caption=content.ABOUT_TEXT,
        reply_markup=keyboards.back_to_menu(),
    )
    await callback.answer()


@router.callback_query(F.data == "reviews")
async def show_reviews(callback: CallbackQuery):
    await callback.message.answer(content.REVIEWS_TEXT, reply_markup=keyboards.back_to_menu())
    await callback.answer()

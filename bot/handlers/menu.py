from aiogram import F, Router
from aiogram.types import CallbackQuery

from .. import content, content_store, keyboards
from ..config import is_admin

router = Router()


@router.callback_query(F.data == "menu")
async def show_menu(callback: CallbackQuery):
    await callback.message.answer(
        "Выбирай нужный раздел 👇",
        reply_markup=keyboards.main_menu(is_admin=is_admin(callback.from_user.id)),
    )
    await callback.answer()


@router.callback_query(F.data == "course")
async def show_course(callback: CallbackQuery):
    text = await content_store.get_text("course", content.COURSE_TEXT)
    photo = await content_store.get_photo("course", content.COURSE_PHOTO)
    await callback.message.answer_photo(
        photo=content_store.to_input(photo),
        caption=text,
        reply_markup=keyboards.course_menu(),
    )
    await callback.answer()


@router.callback_query(F.data == "format")
async def show_format(callback: CallbackQuery):
    text = await content_store.get_text("format", content.FORMAT_TEXT)
    photo = await content_store.get_photo("format", content.FORMAT_PHOTO)
    await callback.message.answer_photo(
        photo=content_store.to_input(photo),
        caption=text,
        reply_markup=keyboards.back_to_menu(),
    )
    await callback.answer()


@router.callback_query(F.data == "program")
async def show_program(callback: CallbackQuery):
    text = await content_store.get_text("program_intro", content.PROGRAM_INTRO)
    await callback.message.answer(text, reply_markup=keyboards.program_menu())
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
    default_body = "\n".join([tariff["note"], ""] + [f"— {f}" for f in tariff["features"]])
    body = await content_store.get_text(f"tariff_{key}", default_body)
    text = f"💳 <b>{tariff['title']} — {tariff['price']}</b>\n\n{body}"
    await callback.message.answer(text, reply_markup=keyboards.pricing_menu(key))
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
    default_caption = f"<b>{teacher['name']}</b>\n<i>{teacher['role']}</i>\n\n{teacher['text']}"
    store_key = f"teacher_{key}"
    caption = await content_store.get_text(store_key, default_caption)
    photo = await content_store.get_photo(store_key, teacher["photo"])
    await callback.message.answer_photo(
        photo=content_store.to_input(photo),
        caption=caption,
        reply_markup=keyboards.teacher_card_menu(),
    )
    await callback.answer()


@router.callback_query(F.data == "about")
async def show_about(callback: CallbackQuery):
    text = await content_store.get_text("about", content.ABOUT_TEXT)
    photo = await content_store.get_photo("about", content.ABOUT_PHOTO)
    await callback.message.answer_photo(
        photo=content_store.to_input(photo),
        caption=text,
        reply_markup=keyboards.back_to_menu(),
    )
    await callback.answer()


@router.callback_query(F.data == "reviews")
async def show_reviews(callback: CallbackQuery):
    text = await content_store.get_text("reviews", content.REVIEWS_TEXT)
    await callback.message.answer(text, reply_markup=keyboards.back_to_menu())
    await callback.answer()

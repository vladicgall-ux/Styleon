from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .. import content, content_store
from ..config import is_admin

router = Router()


class EditContent(StatesGroup):
    text = State()
    photo = State()


# --- registry of editable sections: key -> {label, photo (Path|None), text (callable)} ---

SIMPLE_SECTIONS = {
    "welcome": {"label": "👋 Приветствие (/start)", "photo": content.WELCOME_PHOTO, "text": lambda: content.WELCOME_TEXT},
    "course": {"label": "🎓 О курсе", "photo": content.COURSE_PHOTO, "text": lambda: content.COURSE_TEXT},
    "format": {"label": "🧵 Формат обучения", "photo": content.FORMAT_PHOTO, "text": lambda: content.FORMAT_TEXT},
    "about": {"label": "🏫 О школе", "photo": content.ABOUT_PHOTO, "text": lambda: content.ABOUT_TEXT},
    "reviews": {"label": "💬 Отзывы", "photo": None, "text": lambda: content.REVIEWS_TEXT},
    "program_intro": {"label": "📚 Программа (вступление)", "photo": None, "text": lambda: content.PROGRAM_INTRO},
}

TEACHER_SECTIONS = {
    f"teacher_{key}": {
        "label": f"👩‍🏫 {t['name']}",
        "photo": t["photo"],
        "text": (lambda t=t: f"<b>{t['name']}</b>\n<i>{t['role']}</i>\n\n{t['text']}"),
    }
    for key, t in content.TEACHERS.items()
}

TARIFF_SECTIONS = {
    f"tariff_{key}": {
        "label": f"💳 Тариф «{t['title']}»",
        "photo": None,
        "text": (lambda t=t: "\n".join([t["note"], ""] + [f"— {f}" for f in t["features"]])),
    }
    for key, t in content.TARIFFS.items()
}

ALL_SECTIONS = {**SIMPLE_SECTIONS, **TEACHER_SECTIONS, **TARIFF_SECTIONS}


def _resolve_section(key: str) -> dict:
    if key.startswith("faq_"):
        index = int(key.split("_", 1)[1])
        question, default_answer = content.FAQ[index]
        return {"label": f"❓ {question}", "photo": None, "text": lambda: default_answer}
    return ALL_SECTIONS[key]


def settings_menu():
    kb = InlineKeyboardBuilder()
    for key in ("welcome", "course", "format", "about", "reviews", "program_intro"):
        kb.button(text=SIMPLE_SECTIONS[key]["label"], callback_data=f"settings:{key}")
    kb.button(text="💳 Тарифы", callback_data="settings_group:tariff")
    kb.button(text="👩‍🏫 Преподаватели", callback_data="settings_group:teacher")
    kb.button(text="❓ Вопросы FAQ", callback_data="settings_group:faq")
    kb.adjust(1)
    kb.row(InlineKeyboardButton(text="⬅ В главное меню", callback_data="menu"))
    return kb.as_markup()


def group_menu(group: str):
    items = TARIFF_SECTIONS if group == "tariff" else TEACHER_SECTIONS
    kb = InlineKeyboardBuilder()
    for key, meta in items.items():
        kb.button(text=meta["label"], callback_data=f"settings:{key}")
    kb.adjust(1)
    kb.row(InlineKeyboardButton(text="⬅ К настройкам", callback_data="settings"))
    return kb.as_markup()


def faq_group_menu():
    kb = InlineKeyboardBuilder()
    for i, (question, _) in enumerate(content.FAQ):
        kb.button(text=question, callback_data=f"settings:faq_{i}")
    kb.adjust(1)
    kb.row(InlineKeyboardButton(text="⬅ К настройкам", callback_data="settings"))
    return kb.as_markup()


def section_detail_menu(key: str, has_photo: bool):
    kb = InlineKeyboardBuilder()
    kb.button(text="✏️ Изменить текст", callback_data=f"settings_text:{key}")
    if has_photo:
        kb.button(text="🖼 Изменить фото", callback_data=f"settings_photo:{key}")
    kb.button(text="♻️ Сбросить к исходному", callback_data=f"settings_reset:{key}")
    kb.adjust(1)
    kb.row(InlineKeyboardButton(text="⬅ Назад", callback_data="settings"))
    return kb.as_markup()


async def _send_settings_menu(message: Message):
    await message.answer(
        "⚙️ <b>Настройки контента</b>\n\nВыберите раздел для редактирования:",
        reply_markup=settings_menu(),
    )


@router.message(Command("settings"))
async def cmd_settings(message: Message):
    if not is_admin(message.from_user.id):
        return
    await _send_settings_menu(message)


@router.callback_query(F.data == "settings")
async def show_settings(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Недоступно", show_alert=True)
        return
    await _send_settings_menu(callback.message)
    await callback.answer()


@router.callback_query(F.data.startswith("settings_group:"))
async def show_group(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Недоступно", show_alert=True)
        return
    group = callback.data.split(":", 1)[1]
    if group == "faq":
        await callback.message.answer("Выберите вопрос:", reply_markup=faq_group_menu())
    else:
        await callback.message.answer("Выберите раздел:", reply_markup=group_menu(group))
    await callback.answer()


@router.callback_query(F.data.startswith("settings:"))
async def show_section(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Недоступно", show_alert=True)
        return
    key = callback.data.split(":", 1)[1]
    meta = _resolve_section(key)
    current_text = await content_store.get_text(key, meta["text"]())
    has_photo = meta["photo"] is not None

    if has_photo:
        current_photo = await content_store.get_photo(key, meta["photo"])
        await callback.message.answer_photo(
            photo=content_store.to_input(current_photo),
            caption=f"<b>{meta['label']}</b>\n\n{current_text}",
        )
    else:
        await callback.message.answer(f"<b>{meta['label']}</b>\n\n{current_text}")

    await callback.message.answer("Что изменить?", reply_markup=section_detail_menu(key, has_photo))
    await callback.answer()


@router.callback_query(F.data.startswith("settings_text:"))
async def ask_new_text(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Недоступно", show_alert=True)
        return
    key = callback.data.split(":", 1)[1]
    await state.set_state(EditContent.text)
    await state.update_data(key=key)
    await callback.message.answer(
        "Пришлите новый текст одним сообщением. Поддерживается HTML-разметка Telegram "
        "(<b>жирный</b>, <i>курсив</i>)."
    )
    await callback.answer()


@router.message(EditContent.text)
async def save_new_text(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    data = await state.get_data()
    key = data["key"]
    await content_store.set_text(key, message.html_text or message.text)
    await state.clear()
    await message.answer("Текст обновлён ✅")
    await _send_settings_menu(message)


@router.callback_query(F.data.startswith("settings_photo:"))
async def ask_new_photo(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Недоступно", show_alert=True)
        return
    key = callback.data.split(":", 1)[1]
    await state.set_state(EditContent.photo)
    await state.update_data(key=key)
    await callback.message.answer("Пришлите новое фото.")
    await callback.answer()


@router.message(EditContent.photo, F.photo)
async def save_new_photo(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    data = await state.get_data()
    key = data["key"]
    file_id = message.photo[-1].file_id
    await content_store.set_photo(key, file_id)
    await state.clear()
    await message.answer("Фото обновлено ✅")
    await _send_settings_menu(message)


@router.message(EditContent.photo)
async def wrong_photo_type(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("Пришлите, пожалуйста, именно фото.")


@router.callback_query(F.data.startswith("settings_reset:"))
async def reset_section(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Недоступно", show_alert=True)
        return
    key = callback.data.split(":", 1)[1]
    await content_store.reset(key)
    await callback.answer("Сброшено к исходному ✅")
    await callback.message.answer("Готово. Раздел сброшен к исходному содержимому.")
    await _send_settings_menu(callback.message)

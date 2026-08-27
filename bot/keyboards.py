from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from . import content


def main_menu() -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.button(text="🎓 О курсе «Персональный стилист»", callback_data="course")
    kb.button(text="🧵 Формат обучения", callback_data="format")
    kb.button(text="📚 Программа курса", callback_data="program")
    kb.button(text="💳 Тарифы и цены", callback_data="pricing")
    kb.button(text="👩‍🏫 Преподаватели", callback_data="teachers")
    kb.button(text="🏫 О школе STYLE ON", callback_data="about")
    kb.button(text="💬 Отзывы выпускниц", callback_data="reviews")
    kb.button(text="❓ Частые вопросы", callback_data="faq")
    kb.button(text="📝 Оставить заявку", callback_data="apply")
    kb.row(
        InlineKeyboardButton(text="🔗 Мы в VK", url=content.VK_COMMUNITY),
        InlineKeyboardButton(text="🌐 Сайт школы", url=content.WEBSITE),
    )
    kb.adjust(1)
    return kb.as_markup()


def back_to_menu(extra_row: list[InlineKeyboardButton] | None = None):
    kb = InlineKeyboardBuilder()
    if extra_row:
        kb.row(*extra_row)
    kb.row(InlineKeyboardButton(text="⬅ В главное меню", callback_data="menu"))
    return kb.as_markup()


def course_menu():
    return back_to_menu(
        [
            InlineKeyboardButton(text="📚 Программа", callback_data="program"),
            InlineKeyboardButton(text="💳 Тарифы", callback_data="pricing"),
        ]
    )


def program_menu():
    kb = InlineKeyboardBuilder()
    for key, block in content.PROGRAM_BLOCKS.items():
        kb.button(text=block["short"], callback_data=f"program:{key}")
    kb.adjust(1)
    kb.row(InlineKeyboardButton(text="⬅ В главное меню", callback_data="menu"))
    return kb.as_markup()


def program_block_menu():
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="⬅ К программе", callback_data="program"),
        InlineKeyboardButton(text="🏠 Меню", callback_data="menu"),
    )
    return kb.as_markup()


def pricing_menu(active: str):
    kb = InlineKeyboardBuilder()
    row = []
    for key in content.TARIFF_ORDER:
        title = content.TARIFFS[key]["title"]
        label = f"• {title} •" if key == active else title
        row.append(InlineKeyboardButton(text=label, callback_data=f"pricing:{key}"))
    kb.row(*row)
    kb.row(InlineKeyboardButton(text="📝 Оставить заявку", callback_data="apply"))
    kb.row(InlineKeyboardButton(text="⬅ В главное меню", callback_data="menu"))
    return kb.as_markup()


def teachers_menu():
    kb = InlineKeyboardBuilder()
    for key, teacher in content.TEACHERS.items():
        kb.button(text=teacher["name"], callback_data=f"teachers:{key}")
    kb.adjust(1)
    kb.row(InlineKeyboardButton(text="⬅ В главное меню", callback_data="menu"))
    return kb.as_markup()


def teacher_card_menu():
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="⬅ К преподавателям", callback_data="teachers"),
        InlineKeyboardButton(text="🏠 Меню", callback_data="menu"),
    )
    return kb.as_markup()


def faq_menu():
    kb = InlineKeyboardBuilder()
    for i, (question, _) in enumerate(content.FAQ):
        kb.button(text=question, callback_data=f"faq:{i}")
    kb.adjust(1)
    kb.row(InlineKeyboardButton(text="⬅ В главное меню", callback_data="menu"))
    return kb.as_markup()


def faq_answer_menu():
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="⬅ К вопросам", callback_data="faq"),
        InlineKeyboardButton(text="🏠 Меню", callback_data="menu"),
    )
    return kb.as_markup()


def apply_start_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="📝 Заполнить заявку в боте", callback_data="apply:start")
    kb.button(text="💬 Написать в VK", url=content.VK_MESSAGE)
    kb.adjust(1)
    kb.row(InlineKeyboardButton(text="⬅ В главное меню", callback_data="menu"))
    return kb.as_markup()


def tariff_choice_menu():
    kb = InlineKeyboardBuilder()
    for key in content.TARIFF_ORDER:
        kb.button(text=content.TARIFFS[key]["title"], callback_data=f"apply_tariff:{key}")
    kb.button(text="Пока не решил(а)", callback_data="apply_tariff:unset")
    kb.adjust(1)
    return kb.as_markup()


def cancel_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="Отменить", callback_data="apply:cancel")
    return kb.as_markup()

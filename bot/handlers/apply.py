from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from .. import content, keyboards
from ..config import ADMIN_CHAT_ID

router = Router()


class ApplyForm(StatesGroup):
    name = State()
    contact = State()
    tariff = State()


@router.callback_query(F.data == "apply")
async def show_apply(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(content.CONTACT_TEXT, reply_markup=keyboards.apply_start_menu())
    await callback.answer()


@router.message(Command("apply"))
async def cmd_apply(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(content.CONTACT_TEXT, reply_markup=keyboards.apply_start_menu())


@router.callback_query(F.data == "apply:start")
async def start_apply_form(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ApplyForm.name)
    await callback.message.answer(
        "Как вас зовут? Напишите имя одним сообщением.",
        reply_markup=keyboards.cancel_menu(),
    )
    await callback.answer()


@router.callback_query(F.data == "apply:cancel")
async def cancel_apply_form(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Заявка отменена.", reply_markup=keyboards.main_menu())
    await callback.answer()


@router.message(ApplyForm.name)
async def apply_got_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(ApplyForm.contact)
    await message.answer(
        "Отлично! Оставьте номер телефона или ник в Telegram/VK для связи.",
        reply_markup=keyboards.cancel_menu(),
    )


@router.message(ApplyForm.contact)
async def apply_got_contact(message: Message, state: FSMContext):
    await state.update_data(contact=message.text)
    await state.set_state(ApplyForm.tariff)
    await message.answer(
        "Какой тариф вас интересует?",
        reply_markup=keyboards.tariff_choice_menu(),
    )


@router.callback_query(ApplyForm.tariff, F.data.startswith("apply_tariff:"))
async def apply_got_tariff(callback: CallbackQuery, state: FSMContext):
    key = callback.data.split(":", 1)[1]
    tariff_title = content.TARIFFS[key]["title"] if key != "unset" else "не выбран"
    data = await state.get_data()
    await state.clear()

    user = callback.from_user
    lead_lines = [
        "📝 <b>Новая заявка со STYLE ON бота</b>",
        f"Имя: {data.get('name')}",
        f"Контакт: {data.get('contact')}",
        f"Тариф: {tariff_title}",
        f"Telegram: @{user.username}" if user.username else f"Telegram ID: {user.id}",
    ]
    lead_text = "\n".join(lead_lines)

    if ADMIN_CHAT_ID:
        await callback.bot.send_message(ADMIN_CHAT_ID, lead_text)

    await callback.message.answer(
        "Спасибо! Заявка принята 🤍 Мы свяжемся с вами в ближайшее время.",
        reply_markup=keyboards.main_menu(),
    )
    await callback.answer()

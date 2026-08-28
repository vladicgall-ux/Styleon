from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .. import content, keyboards, storage
from ..config import ADMIN_CHAT_ID, is_admin

router = Router()


class PaymentForm(StatesGroup):
    fio = State()
    receipt = State()


def _requisites_text(tariff_key: str) -> str:
    tariff = content.TARIFFS[tariff_key]
    return (
        f"💳 <b>Оплата тарифа «{tariff['title']}» — {tariff['price']}</b>\n\n"
        "Переведите сумму по номеру телефона:\n\n"
        f"<b>{content.SELLER_PHONE}</b>\n"
        f"{content.SELLER_BANK}\n"
        f"Получатель: {content.SELLER_NAME}\n\n"
        "После оплаты нажмите кнопку ниже."
    )


def _paid_button(tariff_key: str):
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Я оплатил(а)", callback_data=f"buy_paid:{tariff_key}")
    kb.row(InlineKeyboardButton(text="⬅ К тарифам", callback_data="pricing"))
    return kb.as_markup()


@router.callback_query(F.data.startswith("buy:"))
async def start_buy(callback: CallbackQuery):
    tariff_key = callback.data.split(":", 1)[1]
    await callback.message.answer(_requisites_text(tariff_key), reply_markup=_paid_button(tariff_key))
    await callback.answer()


@router.callback_query(F.data.startswith("buy_paid:"))
async def buy_paid(callback: CallbackQuery, state: FSMContext):
    tariff_key = callback.data.split(":", 1)[1]
    order_id = await storage.create_order(
        user_id=callback.from_user.id,
        username=callback.from_user.username,
        tariff_key=tariff_key,
    )
    await state.set_state(PaymentForm.fio)
    await state.update_data(order_id=order_id)
    await callback.message.answer("Напишите, пожалуйста, вашу Фамилию Имя Отчество одним сообщением.")
    await callback.answer()


@router.message(PaymentForm.fio)
async def got_fio(message: Message, state: FSMContext):
    data = await state.get_data()
    await storage.update_order(data["order_id"], fio=message.text)
    await state.set_state(PaymentForm.receipt)
    await message.answer("Загрузите, пожалуйста, чек об оплате — фотографией или файлом.")


@router.message(PaymentForm.receipt, F.photo | F.document)
async def got_receipt(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.photo:
        file_id = message.photo[-1].file_id
        receipt_type = "photo"
    else:
        file_id = message.document.file_id
        receipt_type = "document"
    await storage.update_order(data["order_id"], receipt_file_id=file_id, receipt_type=receipt_type)

    kb = InlineKeyboardBuilder()
    kb.button(text="📤 Отправить заявку", callback_data="buy_submit")
    await message.answer("Чек получен. Отправить заявку на проверку?", reply_markup=kb.as_markup())


@router.message(PaymentForm.receipt)
async def receipt_wrong_type(message: Message):
    await message.answer("Пожалуйста, отправьте чек фотографией или файлом (документом).")


@router.callback_query(PaymentForm.receipt, F.data == "buy_submit")
async def submit_order(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    order_id = data["order_id"]
    order = await storage.get_order(order_id)
    await storage.update_order(order_id, status="pending_review")
    await state.clear()

    tariff = content.TARIFFS[order["tariff_key"]]
    username_part = f"@{order['username']}" if order["username"] else f"id{order['user_id']}"
    caption = (
        "🧾 <b>Новая оплата — на проверку</b>\n\n"
        f"ФИО: {order['fio']}\n"
        f"Тариф: {tariff['title']} ({tariff['price']})\n"
        f"Telegram: {username_part}\n"
        f"Order ID: <code>{order_id}</code>"
    )
    confirm_kb = InlineKeyboardBuilder()
    confirm_kb.button(text="✅ Подтвердить оплату", callback_data=f"admin_confirm:{order_id}")

    if ADMIN_CHAT_ID:
        if order["receipt_type"] == "photo":
            await callback.bot.send_photo(
                ADMIN_CHAT_ID, order["receipt_file_id"], caption=caption, reply_markup=confirm_kb.as_markup()
            )
        else:
            await callback.bot.send_document(
                ADMIN_CHAT_ID, order["receipt_file_id"], caption=caption, reply_markup=confirm_kb.as_markup()
            )

    await callback.message.answer(
        "Спасибо! Заявка на оплату отправлена. Мы проверим чек и пришлём ссылку на канал курса в ближайшее время 🤍",
        reply_markup=keyboards.main_menu(is_admin=is_admin(callback.from_user.id)),
    )
    await callback.answer()

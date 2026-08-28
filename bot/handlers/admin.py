from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .. import content, storage
from ..config import ADMIN_CHAT_ID

router = Router()

STATUS_LABELS = {
    "draft": "черновик",
    "pending_review": "на проверке",
    "confirmed": "подтверждена, ждёт ссылку",
    "completed": "завершена",
}


class AdminLink(StatesGroup):
    link = State()


def _is_admin(user_id: int) -> bool:
    return bool(ADMIN_CHAT_ID) and str(user_id) == str(ADMIN_CHAT_ID)


@router.callback_query(F.data.startswith("admin_confirm:"))
async def admin_confirm(callback: CallbackQuery, state: FSMContext):
    if not _is_admin(callback.from_user.id):
        await callback.answer("Недоступно", show_alert=True)
        return

    order_id = callback.data.split(":", 1)[1]
    order = await storage.get_order(order_id)
    if not order:
        await callback.answer("Заявка не найдена", show_alert=True)
        return

    await storage.update_order(order_id, status="confirmed")
    await state.set_state(AdminLink.link)
    await state.update_data(order_id=order_id)
    await callback.message.answer(
        f"Оплата подтверждена (ФИО: {order['fio']}).\nВставьте ссылку на канал/курс для отправки клиенту:"
    )
    await callback.answer()


@router.message(AdminLink.link)
async def admin_got_link(message: Message, state: FSMContext):
    if not _is_admin(message.from_user.id):
        return
    await state.update_data(link=message.text)
    kb = InlineKeyboardBuilder()
    kb.button(text="📤 Отправить клиенту", callback_data="admin_send_link")
    await message.answer(f"Ссылка: {message.text}\nОтправить клиенту?", reply_markup=kb.as_markup())


@router.callback_query(AdminLink.link, F.data == "admin_send_link")
async def admin_send_link(callback: CallbackQuery, state: FSMContext):
    if not _is_admin(callback.from_user.id):
        await callback.answer("Недоступно", show_alert=True)
        return

    data = await state.get_data()
    order_id = data["order_id"]
    link = data["link"]
    order = await storage.get_order(order_id)
    await storage.update_order(order_id, channel_link=link, status="completed")
    await state.clear()

    tariff = content.TARIFFS[order["tariff_key"]]
    await callback.bot.send_message(
        order["user_id"],
        f"🎉 Оплата подтверждена! Добро пожаловать в {content.SCHOOL_NAME}.\n"
        f"Ваш тариф: {tariff['title']}.\n\n"
        f"Ссылка на канал курса:\n{link}",
    )
    await callback.message.answer("Ссылка отправлена клиенту ✅")
    await callback.answer()


@router.message(Command("stats"))
async def stats(message: Message):
    if not _is_admin(message.from_user.id):
        return

    orders = await storage.list_orders()
    if not orders:
        await message.answer("Пока нет заявок.")
        return

    by_tariff: dict[str, int] = {}
    total_paid = 0
    for order in orders:
        if order["status"] in ("confirmed", "completed"):
            by_tariff[order["tariff_key"]] = by_tariff.get(order["tariff_key"], 0) + 1
            total_paid += 1

    lines = ["📊 <b>Статистика продаж</b>\n"]
    for key, count in by_tariff.items():
        lines.append(f"— {content.TARIFFS[key]['title']}: {count}")
    lines.append(f"\nВсего оплат: {total_paid}")

    lines.append("\n<b>Последние заявки:</b>")
    for order in orders[-15:]:
        title = content.TARIFFS[order["tariff_key"]]["title"]
        who = order.get("fio") or (f"@{order['username']}" if order["username"] else f"id{order['user_id']}")
        status_label = STATUS_LABELS.get(order["status"], order["status"])
        lines.append(f"{who} — {title} — {status_label}")

    await message.answer("\n".join(lines))

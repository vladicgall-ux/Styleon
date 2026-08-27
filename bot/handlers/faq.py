from aiogram import F, Router
from aiogram.types import CallbackQuery

from .. import content, keyboards

router = Router()


@router.callback_query(F.data == "faq")
async def show_faq(callback: CallbackQuery):
    await callback.message.answer(
        "❓ <b>Частые вопросы</b>\n\nВыберите вопрос:",
        reply_markup=keyboards.faq_menu(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("faq:"))
async def show_faq_answer(callback: CallbackQuery):
    index = int(callback.data.split(":", 1)[1])
    question, answer = content.FAQ[index]
    await callback.message.answer(
        f"<b>{question}</b>\n\n{answer}",
        reply_markup=keyboards.faq_answer_menu(),
    )
    await callback.answer()

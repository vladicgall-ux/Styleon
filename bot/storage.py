"""Простое файловое хранилище заявок на оплату (data/orders.json).

Достаточно для одного бота/одного администратора: без внешней БД,
но с блокировкой на запись, чтобы конкурентные хендлеры не затирали
друг друга.
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DATA_DIR = Path(__file__).parent.parent / "data"
ORDERS_FILE = DATA_DIR / "orders.json"

_lock = asyncio.Lock()


def _ensure_file() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    if not ORDERS_FILE.exists():
        ORDERS_FILE.write_text("{}", encoding="utf-8")


def _load() -> dict:
    _ensure_file()
    return json.loads(ORDERS_FILE.read_text(encoding="utf-8"))


def _save(data: dict) -> None:
    ORDERS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


async def create_order(user_id: int, username: Optional[str], tariff_key: str) -> str:
    async with _lock:
        data = _load()
        order_id = uuid.uuid4().hex
        data[order_id] = {
            "order_id": order_id,
            "user_id": user_id,
            "username": username,
            "tariff_key": tariff_key,
            "fio": None,
            "receipt_file_id": None,
            "receipt_type": None,
            "status": "draft",
            "channel_link": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        _save(data)
        return order_id


async def update_order(order_id: str, **fields) -> None:
    async with _lock:
        data = _load()
        if order_id in data:
            data[order_id].update(fields)
            _save(data)


async def get_order(order_id: str) -> Optional[dict]:
    async with _lock:
        return _load().get(order_id)


async def list_orders() -> list[dict]:
    async with _lock:
        return list(_load().values())

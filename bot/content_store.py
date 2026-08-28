"""Пользовательские правки контента (data/content_overrides.json).

Позволяет администратору менять тексты и фото прямо из бота, не трогая
код. Если для ключа нет правки — используется значение по умолчанию
из content.py, которое хендлер передаёт сам.
"""

import asyncio
import json
from pathlib import Path
from typing import Union

from aiogram.types import FSInputFile

DATA_DIR = Path(__file__).parent.parent / "data"
OVERRIDES_FILE = DATA_DIR / "content_overrides.json"

_lock = asyncio.Lock()


def _ensure_file() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    if not OVERRIDES_FILE.exists():
        OVERRIDES_FILE.write_text("{}", encoding="utf-8")


def _load() -> dict:
    _ensure_file()
    return json.loads(OVERRIDES_FILE.read_text(encoding="utf-8"))


def _save(data: dict) -> None:
    OVERRIDES_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


async def get_text(key: str, default: str) -> str:
    async with _lock:
        data = _load()
        return data.get(key, {}).get("text", default)


async def get_photo(key: str, default: Union[str, Path]) -> Union[str, Path]:
    async with _lock:
        data = _load()
        override = data.get(key, {}).get("photo")
        return override if override else default


async def set_text(key: str, text: str) -> None:
    async with _lock:
        data = _load()
        data.setdefault(key, {})["text"] = text
        _save(data)


async def set_photo(key: str, file_id: str) -> None:
    async with _lock:
        data = _load()
        data.setdefault(key, {})["photo"] = file_id
        _save(data)


async def reset(key: str) -> None:
    async with _lock:
        data = _load()
        data.pop(key, None)
        _save(data)


def to_input(photo: Union[str, Path]):
    """A saved override is a Telegram file_id (str); the default is a local Path."""
    return photo if isinstance(photo, str) else FSInputFile(photo)

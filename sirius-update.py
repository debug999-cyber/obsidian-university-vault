#!/usr/bin/env python3
"""Sirius Schedule Updater.

Скрипт предназначен для запуска из кастомного Obsidian-плагина Sirius Schedule,
но его также можно запускать вручную.

По умолчанию:
- группа берётся из SIRIUS_GROUP или из DEFAULT_GROUP;
- vault берётся из OBSIDIAN_VAULT или из папки, где лежит этот файл;
- недостающие Python-зависимости и Chromium для Playwright устанавливаются
  автоматически, если SIRIUS_AUTO_INSTALL не равен "0".
"""

from __future__ import annotations

import asyncio
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════════
# НАСТРОЙКИ
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT_GROUP = "К0000-00/0"  # замени в настройках плагина или через SIRIUS_GROUP
GROUP_NAME = os.getenv("SIRIUS_GROUP", DEFAULT_GROUP).strip() or DEFAULT_GROUP
VAULT_PATH = Path(os.getenv("OBSIDIAN_VAULT", Path(__file__).resolve().parent)).expanduser()
OUTPUT_FILE = VAULT_PATH / "sirius-schedule.json"
BASE_URL = "https://schedule.siriusuniversity.ru/list"
AUTO_INSTALL = os.getenv("SIRIUS_AUTO_INSTALL", "1") != "0"

PAIR_SLOTS = {
    "08:00": 0, "08:30": 0, "08:45": 1,
    "10:20": 2, "11:55": 3, "13:30": 4,
    "15:05": 5, "16:40": 6, "18:15": 7,
}


def run(cmd: list[str]) -> None:
    print("$ " + " ".join(cmd))
    subprocess.check_call(cmd)


def ensure_dependencies() -> None:
    """Пытается автоматически поставить зависимости для первого запуска."""
    missing = []
    if importlib.util.find_spec("bs4") is None:
        missing.append("beautifulsoup4")
    if importlib.util.find_spec("playwright") is None:
        missing.append("playwright")

    if missing:
        if not AUTO_INSTALL:
            raise RuntimeError(
                "Не установлены зависимости: " + ", ".join(missing) +
                ". Выполни: pip install -r requirements.txt"
            )
        req = Path(__file__).resolve().parent / "requirements.txt"
        if req.exists():
            run([sys.executable, "-m", "pip", "install", "-r", str(req)])
        else:
            run([sys.executable, "-m", "pip", "install", *missing])


def install_playwright_chromium() -> None:
    if not AUTO_INSTALL:
        raise RuntimeError("Chromium для Playwright не установлен. Выполни: playwright install chromium")
    run([sys.executable, "-m", "playwright", "install", "chromium"])


# ═══════════════════════════════════════════════════════════════════════════════
# ПАРСЕР
# ═══════════════════════════════════════════════════════════════════════════════

class SiriusParser:
    async def fetch(self, group_name: str) -> list:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = await context.new_page()

            try:
                await page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
                await page.click('div[x-on\\:click="open = ! open"]')
                await page.fill('input[id="searchListInput"]', group_name)
                await page.wait_for_selector("ul#searchList li", timeout=5000)
                group_item = page.locator("ul#searchList li", has_text=group_name).first
                await group_item.click()
                await page.wait_for_selector("table.table-list tbody tr", timeout=10000)
                await asyncio.sleep(3)

                html = await page.content()
                return self._parse_html(html)

            finally:
                await browser.close()

    def _parse_html(self, html: str) -> list:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        lessons = []

        for row in soup.select("table.table-list tbody tr"):
            cells = row.find_all("td")
            if len(cells) < 8:
                continue

            lesson = {
                "date": self._clean(cells[0].get_text()),
                "day": self._clean(cells[1].get_text()),
                "start": self._clean(cells[2].get_text()),
                "end": self._clean(cells[3].get_text()),
                "subject": self._clean(cells[4].get_text()),
                "type": self._clean(cells[5].get_text()),
                "room": self._clean_room(cells[6].get_text()),
                "teacher": self._clean_teacher(cells[7].get_text()),
                "pairNum": self._infer_pair_num(self._clean(cells[2].get_text())),
            }

            if self._is_valid(lesson):
                lessons.append(lesson)

        return lessons

    @staticmethod
    def _clean(text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def _clean_room(text: str) -> str:
        room = SiriusParser._clean(text)
        if len(room) >= 4:
            half = len(room) // 2
            if room[:half] == room[half:]:
                room = room[:half]
        return room

    @staticmethod
    def _clean_teacher(text: str) -> str:
        cleaned = SiriusParser._clean(text)
        if len(cleaned) > 60 and any(kw in cleaned.lower() for kw in ["колледж", "автономной", "организации", "университет"]):
            return ""
        if "лицей" in cleaned.lower() and "сириус" in cleaned.lower():
            return ""
        return cleaned

    @staticmethod
    def _infer_pair_num(time: str) -> int:
        h, m = map(int, time.split(":"))
        minutes = h * 60 + m
        closest, min_diff = 0, float("inf")
        for slot_time, slot_num in PAIR_SLOTS.items():
            sh, sm = map(int, slot_time.split(":"))
            diff = abs(minutes - (sh * 60 + sm))
            if diff < min_diff:
                min_diff = diff
                closest = slot_num
        return closest

    @staticmethod
    def _is_valid(l: dict) -> bool:
        return bool(l.get("subject") and l.get("start") and l.get("date") and len(l["subject"]) > 2)


def save_schedule(lessons: list):
    by_date = {}
    for l in lessons:
        date = l["date"]
        by_date.setdefault(date, []).append(l)

    data = {
        "updated": datetime.now().isoformat(),
        "group": GROUP_NAME,
        "total_lessons": len(lessons),
        "by_date": by_date,
        "lessons": lessons
    }

    OUTPUT_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Сохранено: {OUTPUT_FILE}")
    print(f"   Пар: {len(lessons)} | Дней: {len(by_date)}")


async def fetch_with_browser_autoinstall() -> list:
    parser = SiriusParser()
    try:
        return await parser.fetch(GROUP_NAME)
    except Exception as e:
        text = str(e)
        if "Executable doesn't exist" in text or "playwright install" in text.lower():
            print("Chromium для Playwright не найден. Устанавливаю автоматически...")
            install_playwright_chromium()
            return await parser.fetch(GROUP_NAME)
        raise


async def main():
    print(f"Загрузка расписания для {GROUP_NAME}...")

    if not VAULT_PATH.exists():
        print(f"Папка не найдена: {VAULT_PATH}")
        print("   Укажи OBSIDIAN_VAULT или положи скрипт в корень vault")
        return 1

    ensure_dependencies()
    lessons = await fetch_with_browser_autoinstall()

    if not lessons:
        print("Не удалось загрузить расписание")
        return 1

    save_schedule(lessons)
    print("\nГотово. Obsidian автоматически перечитает JSON.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

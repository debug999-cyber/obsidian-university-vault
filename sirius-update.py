#!/usr/bin/env python3
"""Sirius Schedule Updater"""

import asyncio
import json
import re
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

# ═══════════════════════════════════════════════════════════════════════════════
# НАСТРОЙКИ (измени только здесь)
# ═══════════════════════════════════════════════════════════════════════════════

GROUP_NAME = "К0709-25/1"  # ← ЗАМЕНИ НА СВОЮ ГРУППУ

# Путь к хранилищу Obsidian:
# Windows: Path("C:/Users/Имя/Documents/Obsidian Vault")
# Если путь с кириллицей — используй raw строку: r"D:\Учеба\тесты"
VAULT_PATH = Path(r"D:\Учеба\тесты")  # ← ЗАМЕНИ НА СВОЙ ПУТЬ

OUTPUT_FILE = VAULT_PATH / "sirius-schedule.json"
BASE_URL = "https://schedule.siriusuniversity.ru/list"

PAIR_SLOTS = {
    "08:00": 0, "08:30": 0, "08:45": 1,
    "10:20": 2, "11:55": 3, "13:30": 4,
    "15:05": 5, "16:40": 6, "18:15": 7,
}

# ═══════════════════════════════════════════════════════════════════════════════
# ПАРСЕР
# ═══════════════════════════════════════════════════════════════════════════════

class SiriusParser:
    async def fetch(self, group_name: str) -> list:
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
        if date not in by_date:
            by_date[date] = []
        by_date[date].append(l)

    data = {
        "updated": datetime.now().isoformat(),
        "group": GROUP_NAME,
        "total_lessons": len(lessons),
        "by_date": by_date,
        "lessons": lessons
    }

    OUTPUT_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ Сохранено: {OUTPUT_FILE}")
    print(f"   Пар: {len(lessons)} | Дней: {len(by_date)}")


async def main():
    print(f"🚀 Загрузка расписания для {GROUP_NAME}...")

    if not VAULT_PATH.exists():
        print(f"❌ Папка не найдена: {VAULT_PATH}")
        print("   Измени VAULT_PATH в скрипте (строка 18)")
        return

    parser = SiriusParser()
    lessons = await parser.fetch(GROUP_NAME)

    if not lessons:
        print("❌ Не удалось загрузить расписание")
        return

    save_schedule(lessons)
    print("\n🎉 Готово! Нажми кнопку в Obsidian.")


if __name__ == "__main__":
    asyncio.run(main())
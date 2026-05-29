#!/usr/bin/env python3
"""Vault health check: ссылки, frontmatter, сроки, пустые файлы и мусор.
Запускать из корня vault: python 50-Система/Скрипты/vault-health-check.py
"""
from __future__ import annotations
from pathlib import Path
from datetime import date
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "50-Система" / "Отчёты"
REPORT_MD = REPORT_DIR / "VAULT_HEALTH.md"
REPORT_JSON = REPORT_DIR / "vault-health.json"
IGNORE_PARTS = {".git", ".trash", "node_modules", "__pycache__"}
IGNORE_PREFIXES = {"50-Система/Архив/"}
REQUIRED_FOR_DUE = ["title", "type", "subject", "due_date", "status"]


def iter_files(pattern="*"):
    for p in ROOT.rglob(pattern):
        if p.is_file() and not any(part in IGNORE_PARTS for part in p.parts) and not any(p.relative_to(ROOT).as_posix().startswith(pref) for pref in IGNORE_PREFIXES):
            yield p


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def frontmatter(text: str) -> dict[str, str]:
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return {}
    data = {}
    key = None
    for raw in m.group(1).splitlines():
        if not raw.strip() or raw.startswith(" ") or raw.startswith("-"):
            continue
        if ":" in raw:
            key, value = raw.split(":", 1)
            data[key.strip()] = value.strip().strip('"')
    return data


def main() -> int:
    md_files = list(iter_files("*.md"))
    all_files = list(iter_files("*"))
    by_stem: dict[str, list[Path]] = {}
    by_path_no_ext = set()
    for p in md_files:
        by_stem.setdefault(p.stem, []).append(p)
        by_path_no_ext.add(rel(p)[:-3])

    empty = [rel(p) for p in md_files if not p.read_text(encoding="utf-8", errors="ignore").strip()]
    os_junk = [rel(p) for p in all_files if p.name.startswith("._") or p.name in {".DS_Store", "Thumbs.db"}]
    broken_links = []
    dynamic_links_skipped = 0
    due_issues = []
    invalid_dates = []
    personal_hints = []

    for p in md_files:
        text = p.read_text(encoding="utf-8", errors="ignore")
        fm = frontmatter(text)
        if any(x in text.lower() for x in ["пароль", "password", "secret", "token", "api_key", "apikey"]):
            personal_hints.append(rel(p))
        if "due_date" in fm:
            for k in REQUIRED_FOR_DUE:
                if not fm.get(k):
                    due_issues.append({"file": rel(p), "missing": k})
            raw = fm.get("due_date", "").strip()
            if raw:
                try:
                    date.fromisoformat(raw[:10])
                except Exception:
                    invalid_dates.append({"file": rel(p), "due_date": raw})
        for target in re.findall(r"\[\[([^\]|#]+)", text):
            target = target.strip().removesuffix(".md")
            if not target or target.startswith('"') or "," in target or target.startswith("Имя файла") or any(x in target for x in ['" +', '+ "', '[0]', '${']):
                dynamic_links_skipped += 1
                continue
            if target in by_path_no_ext:
                continue
            candidates = by_stem.get(Path(target).name, [])
            if not candidates:
                broken_links.append({"from": rel(p), "to": target})

    result = {
        "generated": date.today().isoformat(),
        "stats": {"markdown_files": len(md_files), "all_files": len(all_files)},
        "empty_files": empty,
        "os_junk": os_junk,
        "broken_links": broken_links,
        "dynamic_links_skipped": dynamic_links_skipped,
        "due_issues": due_issues,
        "invalid_dates": invalid_dates,
        "personal_hints": sorted(set(personal_hints)),
    }
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    def bullet(items, limit=50):
        if not items:
            return "- нет\n"
        out = []
        for x in items[:limit]:
            out.append(f"- `{x}`" if isinstance(x, str) else f"- `{x}`")
        if len(items) > limit:
            out.append(f"- ... ещё {len(items)-limit}")
        return "\n".join(out) + "\n"

    md = [
        "---", "cssclasses:", "  - university-dashboard", "---", "",
        "# Отчёт проверки vault", "",
        f"Дата проверки: **{result['generated']}**", "",
        "## Статистика", "",
        f"- Markdown-файлов: **{len(md_files)}**",
        f"- Всего файлов: **{len(all_files)}**", "",
        "## Пустые Markdown-файлы", "", bullet(empty),
        "## OS-мусор", "", bullet(os_junk),
        "## Битые wiki-ссылки", "", bullet([f"{x['from']} → {x['to']}" for x in broken_links]),
        "## Проблемы frontmatter у заметок со сроками", "", bullet([f"{x['file']}: нет `{x['missing']}`" for x in due_issues]),
        "## Невалидные due_date", "", bullet([f"{x['file']}: {x['due_date']}" for x in invalid_dates]),
        "## Возможные личные/секретные упоминания", "", bullet(sorted(set(personal_hints))),
        "## Примечание", "",
        f"Динамических ссылок в JS пропущено: **{dynamic_links_skipped}**. Это нормально для шаблонов и DataviewJS.", "",
    ]
    REPORT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"OK: {rel(REPORT_MD)}")
    print(json.dumps(result["stats"], ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

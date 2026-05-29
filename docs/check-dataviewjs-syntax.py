#!/usr/bin/env python3
"""Проверяет синтаксис всех ```dataviewjs``` блоков через `node --check`.
Запускать из корня vault: python docs/check-dataviewjs-syntax.py
"""
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
IGNORE_PARTS = {".git", ".trash", "node_modules", "__pycache__"}
IGNORE_PREFIXES = {"50-Система/Архив/"}

blocks = []
for p in ROOT.rglob("*.md"):
    rel = p.relative_to(ROOT).as_posix()
    if any(part in IGNORE_PARTS for part in p.parts):
        continue
    if any(rel.startswith(prefix) for prefix in IGNORE_PREFIXES):
        continue
    text = p.read_text(encoding="utf-8", errors="ignore")
    for i, code in enumerate(re.findall(r"```dataviewjs\n(.*?)\n```", text, re.S), start=1):
        blocks.append((rel, i, code))

errors = []
for rel, index, code in blocks:
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as f:
        f.write(code)
        tmp = f.name
    result = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
    if result.returncode != 0:
        errors.append((rel, index, result.stderr.strip()))

print(f"DataviewJS blocks checked: {len(blocks)}")
print(f"Syntax errors: {len(errors)}")

for rel, index, err in errors:
    print("\n" + "=" * 80)
    print(f"{rel} / block #{index}")
    print(err)

sys.exit(1 if errors else 0)

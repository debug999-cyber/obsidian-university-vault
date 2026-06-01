# 07 — Sirius schedule

В проекте есть два связанных механизма работы с расписанием:

1. **встроенный плагин Obsidian** `sirius-schedule`;
2. **внешний Python-скрипт** `sirius-update.py`.

## 1. Встроенный плагин

Настройки:
- `.obsidian/plugins/sirius-schedule/data.json`

Сейчас там важны параметры:

| Ключ | Что означает |
|---|---|
| `jsonPath` | путь до JSON-файла расписания |
| `groupName` | учебная группа |
| `autoUpdateOnStart` | обновлять ли при запуске |
| `showNotifications` | показывать ли уведомления |
| `cachePath` | путь до кэша |

### Что обычно меняют

- `groupName`
- `jsonPath`

## 2. Внешний скрипт `sirius-update.py`

Этот скрипт:
- открывает сайт расписания Sirius;
- ищет группу;
- парсит пары;
- сохраняет их в `sirius-schedule.json`.

### Самые важные переменные

| Переменная | Где | Что поменять |
|---|---|---|
| `GROUP_NAME` | `sirius-update.py` | свою учебную группу |
| `VAULT_PATH` | `sirius-update.py` | абсолютный путь до vault |
| `OUTPUT_FILE` | `sirius-update.py` | обычно не трогают |

### Что нужно новичку

Если ты переносишь проект на другой компьютер, почти наверняка нужно поменять:

- `GROUP_NAME`
- `VAULT_PATH`

## 3. Где лежат данные расписания

Файл:
- `sirius-schedule.json`

Это **не логика**, а **данные**.

Его обычно не редактируют руками, потому что он пересобирается.

## 4. Как безопасно заменить группу

1. Измени `.obsidian/plugins/sirius-schedule/data.json` → `groupName`
2. Измени `sirius-update.py` → `GROUP_NAME`
3. Измени `sirius-update.py` → `VAULT_PATH`
4. Запусти обновление
5. Проверь, что `sirius-schedule.json` обновился

## 5. Что нужно установить для Python-скрипта

Скрипт использует:
- Python 3
- Playwright
- BeautifulSoup (`bs4`)

Если хочешь пользоваться именно внешним скриптом, нужно поставить эти зависимости отдельно.

## 6. Если расписание не обновляется

Проверяй в таком порядке:

1. верная ли группа;
2. верный ли путь к vault;
3. установлен ли Playwright;
4. не поменялся ли сайт Sirius;
5. может ли Obsidian читать `sirius-schedule.json`.

Подробнее — в `docs/08-TROUBLESHOOTING.md`.

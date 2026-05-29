# Архитектура vault

## Верхний уровень

```text
00-Inbox/              входящие заметки
10-Университет/        учебные предметы
20-Проекты/            проекты
30-Личное/             личный раздел
40-Знания/             база знаний
50-Система/            системные страницы, шаблоны, отчёты, скрипты
99-Архив/              архив
Tags/                  индекс тегов
Home.md                главный рабочий стол
sirius-update.py       обновление расписания Sirius
sirius-schedule.json   локальный JSON расписания
```

## Поток данных дедлайнов

```text
Учебная заметка
  frontmatter: due_date + status
      ↓
DataviewJS
      ↓
50-Система/Дашборды/Дедлайны.md
      ↓
Home.md / блок "Требуют внимания"
```

Статус `Готово` исключает задачу из активных дедлайнов.

## Поток MOC

```text
Папка предмета
      ↓
DataviewJS читает все Markdown-файлы
      ↓
MOC — Предмет.md
      ↓
группировка по type
```

MOC не должен хранить ручной список всех ссылок, если он может собрать их динамически.

## Расписание Sirius

```text
Obsidian / Home.md / команда sirius-update-from-site
      ↓
.obsidian/plugins/sirius-schedule/main.js
      ↓ запускает Python через child_process
sirius-update.py
      ↓ парсинг сайта + автоустановка зависимостей при необходимости
sirius-schedule.json
      ↓ автоматическое перечитывание JSON
Obsidian UI / Calendar / модальные окна расписания
```

Команды Obsidian:

```text
sirius-schedule:sirius-update-from-site   # скачать с сайта и перечитать JSON
sirius-schedule:sirius-reload             # только перечитать JSON
```

Автообновление работает в Obsidian Desktop. На мобильном Obsidian запуск Python невозможен.

## Дизайн-система

Основной CSS:

```text
.obsidian/snippets/university-dashboard-v5.css
```

Ключевые классы:

- `university-dashboard`
- `ud-page`
- `ud-hero`
- `ud-stat-grid`
- `ud-stat`
- `ud-action-row`
- `ud-btn`
- `ud-search`
- `ud-section`
- `ud-list`
- `ud-grid-2`
- `ud-card`
- `ud-card-main`
- `ud-card-link`
- `ud-card-meta`
- `ud-card-tag`
- `ud-date-block`
- `ud-pill`
- `ud-empty`

## Где писать новую логику

- Новый dashboard — в `50-Система/Дашборды/`.
- Новый скрипт проверки/обслуживания — в `50-Система/Скрипты/`.
- Новый отчёт — в `50-Система/Отчёты/`.
- Документация для GitHub/ИИ — в `docs/`.
- Obsidian-пользовательская документация — можно дублировать в `50-Система/Документация/`, если нужно видеть её внутри vault.

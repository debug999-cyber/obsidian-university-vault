# 01 — Start here

Этот документ нужен человеку, который впервые открыл проект и хочет быстро запустить его без чтения всего vault.

## Минимальный сценарий запуска

1. Открой папку проекта как vault в Obsidian.
2. Проверь community plugins.
3. Проверь CSS snippets.
4. Открой `Home.md`.
5. Создай тестовую заметку через кнопку **Новая заметка**.

## Что должно быть включено

### Community plugins

В проекте используются:
- Templater
- Dataview
- Auto Note Mover
- Automatic Linker
- Obsidian Tasks Plugin
- Persistent Graph
- Modal Forms
- Audio Transcription
- Make.md
- Sirius Schedule
- Zoottelkeeper

Список хранится в `.obsidian/community-plugins.json`.

### CSS snippets

Должны быть включены:
- `university-dashboard-v5`
- `system-metadata-v2`
- `system-indexes-v2`
- `professional-dark-v5`

Настройка лежит в `.obsidian/appearance.json`.

## Что открыть первым

| Файл | Что увидишь |
|---|---|
| `Home.md` | Главную панель проекта |
| `50-Система/Дашборды/Дедлайны.md` | Список задач по срокам |
| `10-Университет/Университет.md` | Обзор учебных заметок |
| `50-Система/Шаблоны/Новая заметка.md` | Логику генерации новых записей |

## Первая проверка проекта

### Проверка 1: UI
- Открой `Home.md`
- Убедись, что видны карточки, поиск, блоки предметов и дедлайнов
- Если всё выглядит "голым" — проблема почти наверняка в snippets

### Проверка 2: Dataview
- На `Home.md` должны отображаться реальные данные, а не сырой код
- Если видишь кодовые блоки вместо результата — Dataview не активен

### Проверка 3: Templater
- Нажми кнопку **Новая заметка**
- Должен открыться сценарий создания заметки
- Если кнопка не работает — смотри `docs/08-TROUBLESHOOTING.md`

### Проверка 4: Дедлайны
- Открой `50-Система/Дашборды/Дедлайны.md`
- Должны появиться заметки, у которых есть `due_date`

## Если проект открываешь не для использования, а для настройки

Читай дальше в таком порядке:

1. `docs/02-VAULT-STRUCTURE.md`
2. `docs/03-CHANGE-MAP.md`
3. `docs/04-DASHBOARDS-AND-STYLES.md`
4. `docs/05-TEMPLATES-AND-CONTENT.md`
5. `docs/07-SIRIUS-SCHEDULE.md`

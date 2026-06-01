# 06 — Plugins

Проект завязан на набор community plugins. Ниже — коротко, зачем каждый нужен.

## Критически важные

| Плагин | Зачем нужен |
|---|---|
| `templater-obsidian` | создание и маршрутизация новых заметок |
| `dataview` | все dashboard и MOC-страницы |
| `sirius-schedule` | интеграция расписания |

Без этих трёх проект теряет основную автоматику.

## Важные, но не критичные для базового запуска

| Плагин | Роль |
|---|---|
| `auto-note-mover` | авто-логика по папкам и тегам |
| `automatic-linker` | автоссылки и форматирование |
| `obsidian-tasks-plugin` | задачи |
| `persistent-graph` | стабильная работа графа |
| `modalforms` | формы/диалоги, если будешь расширять систему |
| `make-md` | структура и служебные индексы |
| `zoottelkeeper-obsidian-plugin` | Zettelkasten/связи |
| `audio-transcription` | работа с аудио |

## Где лежат настройки плагинов

Почти всегда здесь:

- `.obsidian/plugins/<plugin-id>/data.json`

Примеры:
- `.obsidian/plugins/sirius-schedule/data.json`
- `.obsidian/plugins/auto-note-mover/data.json`
- `.obsidian/plugins/automatic-linker/data.json`
- `.obsidian/plugins/templater-obsidian/data.json`

## Core plugins

Список лежит в `.obsidian/core-plugins.json`.

Здесь уже включены полезные стандартные функции:
- File explorer
- Search
- Graph
- Backlinks
- Daily notes
- Templates
- Outline
- Word count
- Page preview

## Что важно помнить

- Не редактируй `main.js` плагинов без крайней необходимости.
- Редактируй только `data.json`, если понимаешь, что делаешь.
- Если проект переносится на другой компьютер — сначала поставь плагины, потом проверяй vault.

## Если какой-то плагин пропал

Признаки:
- Dataview-код показывается как текст;
- кнопка **Новая заметка** не работает;
- расписание не обновляется;
- стиль есть, но логики нет.

В таком случае смотри `docs/08-TROUBLESHOOTING.md`.

# Quality Checklist

Используй этот чеклист перед завершением любой задачи.

## Автоматические проверки

### 1. Health-check vault

```bash
python 50-Система/Скрипты/vault-health-check.py
```

Ожидаемо:

- пустые файлы: нет;
- OS-мусор: нет;
- битые wiki-ссылки: нет;
- невалидные `due_date`: нет.

### 2. Python syntax

```bash
python -m py_compile sirius-update.py 50-Система/Скрипты/vault-health-check.py
```

### 3. Sirius plugin JS syntax

```bash
node --check .obsidian/plugins/sirius-schedule/main.js
```

### 4. DataviewJS syntax

Если есть Node.js:

```bash
python docs/check-dataviewjs-syntax.py
```

## Ручные проверки в Obsidian

После крупных изменений пользователь должен проверить:

- `Home.md` открывается без ошибок Dataview.
- `50-Система/Дашборды/Дедлайны.md` открывается без ошибок.
- Кнопка `Готово / Вернуть` меняет `status`.
- Кнопка `Новая заметка` запускает Templater.
- MOC-страницы показывают карточки.
- Поиск на functional pages фильтрует карточки.
- Кнопка `Скачать расписание` запускает обновление с сайта Sirius.
- В настройках Sirius Schedule указана правильная группа и путь к Python.
- CSS snippet `university-dashboard-v5.css` включён.
- Плагины Dataview и Templater включены.

## Проверка публичности

Перед публикацией на GitHub проверить:

- нет паролей;
- нет API-ключей;
- нет приватных email/логинов;
- нет личных файлов в `30-Личное`;
- `.gitignore` закрывает OS-мусор и рабочее состояние Obsidian.

## Отчёт пользователю

В финальном ответе указать:

- что изменено;
- какие файлы изменены;
- какие проверки запущены;
- что осталось проверить вручную;
- какие риски/предупреждения есть.

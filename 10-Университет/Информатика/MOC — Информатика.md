> Map of Content для предмета «Информатика». Автоматически собирает все заметки.

## Все материалы

```dataview
LIST
FROM "10-Университет/Информатика"
WHERE file.name != this.file.name
SORT file.name ASC
```

## По типам и срокам

```dataview
TABLE type, status, due_date, priority
FROM "10-Университет/Информатика"
WHERE due_date AND file.name != this.file.name
SORT due_date ASC
```


## Связанные заметки
- [[2026-05-22 — тест мос]]

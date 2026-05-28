---
cssclasses:
  - university-dashboard
---

> Map of Content для предмета «Обществознание». Автоматически собирает все заметки.

```dataviewjs
const container = dv.container;
container.classList.add("university-dashboard");

const pages = dv.pages("10-Университет/Обществознание")
    .where(p => p.file.name != "MOC — Обществознание")
    .sort(p => p.file.name)
    .array();

const typeColors = {
    "ДЗ": "--ud-blue",
    "Лекция": "--ud-green",
    "Конспект": "--ud-teal",
    "Проект": "--ud-orange",
    "Лаба": "--ud-purple",
    "Экзамен": "--ud-red",
    "Источник": "--ud-frost",
    "Разное": "--ud-frost"
};

const byType = {};
for (const p of pages) {
    const t = p.type || "Разное";
    if (!byType[t]) byType[t] = [];
    byType[t].push(p);
}

const сегодня = DateTime.now().startOf("day");
const месяцы = ["янв","фев","мар","апр","мая","июн","июл","авг","сен","окт","ноя","дек"];

for (const [type, items] of Object.entries(byType)) {
    const colorVar = typeColors[type] || "--ud-frost";

    const section = container.createEl("div", { cls: "ud-moc-section" });
    const header = section.createEl("div", { cls: "ud-moc-header ud-section" });
    header.style.setProperty("--ud-color", "var(" + colorVar + ")");
    header.createEl("span", { cls: "ud-section-dot" });
    const title = header.createEl("span", { text: type, cls: "ud-section-title" });
    title.style.textTransform = "uppercase";
    header.createEl("span", { text: String(items.length), cls: "ud-section-count" });

    const list = section.createEl("div", { cls: "ud-moc-list ud-list" });

    for (const p of items) {
        const card = list.createEl("div", { cls: "ud-card" });
        card.style.setProperty("--ud-border-color", "var(" + colorVar + ")");
        card.addEventListener("dblclick", () => app.workspace.openLinkText(p.file.path, "", false));

        const main = card.createEl("div", { cls: "ud-card-main" });
        const link = main.createEl("a", { text: p.file.name, cls: "ud-card-link" });
        link.addEventListener("click", (e) => {
            e.stopPropagation();
            app.workspace.openLinkText(p.file.path, "", false);
        });

        const meta = main.createEl("div", { cls: "ud-card-meta" });
        if (p.status && p.status !== "Готово") {
            const statusTag = meta.createEl("span", { text: p.status, cls: "ud-card-tag" });
            if (p.status === "В работе") statusTag.style.color = "var(--ud-status-work)";
            if (p.status === "На проверке") statusTag.style.color = "var(--ud-status-today)";
            if (p.status === "Идея") statusTag.style.color = "var(--ud-status-soon)";
        }
        if (p.due_date) {
            const д = DateTime.fromISO(p.due_date);
            const дней = Math.ceil(д.diff(сегодня, "days").days);
            const dateText = д.day + " " + месяцы[д.month-1];
            const dateTag = meta.createEl("span", { text: dateText, cls: "ud-card-tag" });
            if (дней < 0) dateTag.style.color = "var(--ud-status-overdue)";
            else if (дней === 0) dateTag.style.color = "var(--ud-status-today)";
            else if (дней <= 2) dateTag.style.color = "var(--ud-status-soon)";
        }
    }
}

if (pages.length === 0) {
    container.createEl("div", { text: "Пока нет заметок", cls: "ud-empty" });
}
```


## Связанные заметки
- [[2026-05-24 — дд]]

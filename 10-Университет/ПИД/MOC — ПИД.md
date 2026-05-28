---
cssclasses:
  - university-dashboard
---

> Map of Content для предмета «ПИД»

```dataviewjs
const pages = dv.pages("\"10-Университет/ПИД\"")
    .where(p => p.file.name != dv.current().file.name)
    .sort(p => p.file.name)
    .array();

const container = dv.container;
container.classList.add("university-dashboard");

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
        
        const link = card.createEl("a", { text: p.file.name, cls: "ud-card-link" });
        link.addEventListener("click", (e) => {
            e.stopPropagation();
            app.workspace.openLinkText(p.file.path, "", false);
        });
        
        const meta = card.createEl("div", { cls: "ud-card-meta" });
        
        if (p.status && p.status !== "Готово") {
            meta.createEl("span", { text: p.status, cls: "ud-card-tag" });
        }
        if (p.due_date) {
            meta.createEl("span", { text: p.due_date, cls: "ud-card-tag" });
        }
    }
}

if (pages.length === 0) {
    container.createEl("div", { text: "Пока нет заметок", cls: "ud-empty" });
}
```


## Связанные заметки
- [[2026-05-23 — вцв]]
- [[2026-05-23 — фвфвф]]
- [[2026-05-23 — ыофвд]]
- [[Untitled]]
- [[Untitled 1]]
- [[Untitled 2]]

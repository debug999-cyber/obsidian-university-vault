---
cssclasses:
  - university-dashboard
---

# Теги

```dataviewjs
const root = dv.container;
root.classList.add("university-dashboard", "ud-page");
const tags = dv.pages().file.tags.array().sort((a,b) => a.localeCompare(b, "ru"));
const counts = {};
for (const t of tags) counts[t] = (counts[t] || 0) + 1;
const hero = root.createEl("div", { cls: "ud-hero" });
const left = hero.createEl("div");
left.createEl("h1", { text: "Теги" });
left.createEl("p", { text: "Автоматический индекс тегов хранилища." });
const stats = hero.createEl("div", { cls: "ud-stat-grid" });
const item = stats.createEl("div", { cls: "ud-stat" });
item.style.setProperty("--ud-color", "var(--ud-teal)");
item.createEl("strong", { text: String(Object.keys(counts).length) });
item.createEl("span", { text: "уникальных" });
const list = root.createEl("div", { cls: "ud-list ud-grid-2" });
for (const [tag, count] of Object.entries(counts).sort((a,b) => b[1]-a[1])) {
  const row = list.createEl("div", { cls: "ud-card" });
  row.style.setProperty("--ud-border-color", "var(--ud-teal)");
  const main = row.createEl("div", { cls: "ud-card-main" });
  main.createEl("a", { text: tag, cls: "ud-card-link" });
  const meta = main.createEl("div", { cls: "ud-card-meta" });
  meta.createEl("span", { text: `${count} заметок`, cls: "ud-card-tag" });
}
if (!Object.keys(counts).length) root.createEl("div", { text: "Теги пока не используются.", cls: "ud-empty" });
```

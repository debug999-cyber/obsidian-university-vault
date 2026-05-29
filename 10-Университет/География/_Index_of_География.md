---
cssclasses:
  - university-dashboard
---

# География

```dataviewjs
const FOLDER = "10-Университет/География";
const root = dv.container;
root.classList.add("university-dashboard", "ud-page");
const pages = dv.pages(`"${FOLDER}"`)
  .where(p => p.file.path !== this.file.path && !p.file.name.startsWith("_Index_of_"))
  .sort(p => p.file.name)
  .array();
const hero = root.createEl("div", { cls: "ud-hero" });
const left = hero.createEl("div");
left.createEl("h1", { text: "География" });
left.createEl("p", { text: "Служебный индекс предмета." });
const stats = hero.createEl("div", { cls: "ud-stat-grid" });
const item = stats.createEl("div", { cls: "ud-stat" });
item.style.setProperty("--ud-color", "var(--ud-teal)");
item.createEl("strong", { text: String(pages.length) });
item.createEl("span", { text: "заметок" });
const list = root.createEl("div", { cls: "ud-list" });
for (const page of pages) {
  const row = list.createEl("div", { cls: "ud-card" });
  row.style.setProperty("--ud-border-color", "var(--ud-teal)");
  row.addEventListener("dblclick", () => app.workspace.openLinkText(page.file.path, "", false));
  const main = row.createEl("div", { cls: "ud-card-main" });
  const link = main.createEl("a", { text: page.file.name, cls: "ud-card-link" });
  link.addEventListener("click", e => { e.stopPropagation(); app.workspace.openLinkText(page.file.path, "", false); });
}
if (!pages.length) root.createEl("div", { text: "Раздел пока пуст.", cls: "ud-empty" });
```

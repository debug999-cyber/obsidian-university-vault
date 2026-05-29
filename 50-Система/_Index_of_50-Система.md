---
cssclasses:
  - university-dashboard
---

# Система

```dataviewjs
const FOLDER = "50-Система";
const TITLE = "Система";
const root = dv.container;
root.classList.add("university-dashboard", "ud-page");
root.innerHTML = "";
function openPath(path) { app.workspace.openLinkText(path, "", false); }
function renderCard(parent, name, path, meta, count, active) {
  const row = parent.createEl("div", { cls: "ud-card" });
  row.style.setProperty("--ud-border-color", active ? "var(--ud-status-soon)" : "var(--ud-teal)");
  row.dataset.search = [name, meta, path].join(" ").toLowerCase();
  row.addEventListener("dblclick", () => openPath(path));
  const main = row.createEl("div", { cls: "ud-card-main" });
  const link = main.createEl("a", { text: name, cls: "ud-card-link" });
  link.addEventListener("click", e => { e.stopPropagation(); openPath(path); });
  const tags = main.createEl("div", { cls: "ud-card-meta" });
  tags.createEl("span", { text: meta, cls: "ud-card-tag" });
  tags.createEl("span", { text: `${count} заметок`, cls: "ud-card-tag" });
  if (active) tags.createEl("span", { text: `${active} активно`, cls: "ud-card-tag" });
}
const pages = dv.pages(`"${FOLDER}"`).where(p => !p.file.name.startsWith("_Index_of_") && !p.file.name.startsWith("MOC —") && p.file.name !== TITLE).array();
const hero = root.createEl("div", { cls: "ud-hero" });
const left = hero.createEl("div"); left.createEl("h1", { text: TITLE }); left.createEl("p", { text: `Навигация по разделу ${FOLDER}` });
const stats = hero.createEl("div", { cls: "ud-stat-grid" });
for (const s of [["Заметок", pages.length, "--ud-teal"], ["Активных", pages.filter(p => p.status && p.status !== "Готово").length, "--ud-status-soon"], ["Со сроком", pages.filter(p => p.due_date).length, "--ud-status-today"]]) {
  const item = stats.createEl("div", { cls: "ud-stat" }); item.style.setProperty("--ud-color", `var(${s[2]})`); item.createEl("strong", { text: String(s[1]) }); item.createEl("span", { text: s[0] });
}
const search = root.createEl("div", { cls: "ud-search" }); search.createEl("span", { text: "Поиск", cls: "ud-search-label" }); const input = search.createEl("input", { type: "search", placeholder: "Фильтр по разделу..." });
input.addEventListener("input", () => { const term = input.value.trim().toLowerCase(); root.querySelectorAll(".ud-card[data-search]").forEach(el => el.style.display = !term || el.dataset.search.includes(term) ? "" : "none"); });
const folder = app.vault.getAbstractFileByPath(FOLDER);
const list = root.createEl("div", { cls: "ud-list ud-grid-2" });
const dirs = (folder?.children || []).filter(f => f.children).map(f => f.name).sort((a,b) => a.localeCompare(b, "ru"));
for (const dir of dirs) {
  const subPath = `${FOLDER}/${dir}`;
  const subPages = dv.pages(`"${subPath}"`).where(p => !p.file.name.startsWith("_Index_of_") && !p.file.name.startsWith("MOC —")).array();
  const active = subPages.filter(p => p.status && p.status !== "Готово").length;
  const moc = `${subPath}/MOC — ${dir}.md`;
  const index = `${subPath}/_Index_of_${dir}.md`;
  const firstNote = (app.vault.getAbstractFileByPath(subPath)?.children || []).find(f => f.extension === "md");
  const target = app.vault.getAbstractFileByPath(moc) ? moc : app.vault.getAbstractFileByPath(index) ? index : firstNote ? firstNote.path : `${subPath}`;
  renderCard(list, dir, target, subPath, subPages.length, active);
}
if (!dirs.length) {
  for (const p of pages.sort((a,b) => a.file.name.localeCompare(b.file.name, "ru"))) renderCard(list, p.file.name, p.file.path, p.type || p.file.folder, 1, p.status && p.status !== "Готово" ? 1 : 0);
}
if (!pages.length && !dirs.length) root.createEl("div", { text: "Раздел пуст.", cls: "ud-empty" });
```

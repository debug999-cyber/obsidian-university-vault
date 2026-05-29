---
cssclasses:
  - university-dashboard
---

# MOC — География

```dataviewjs
const FOLDER = "10-Университет/География";
const TITLE = "География";
const root = dv.container;
root.classList.add("university-dashboard", "ud-page");
root.innerHTML = "";
const months = ["янв", "фев", "мар", "апр", "мая", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"];
const today = DateTime.now().startOf("day");
const typeColors = {"ДЗ":"--ud-blue", "Лекция":"--ud-green", "Конспект":"--ud-teal", "Проект":"--ud-orange", "Лаба":"--ud-purple", "Экзамен":"--ud-red", "Источник":"--ud-frost", "Разное":"--ud-frost"};
function toDate(v) { if (!v) return null; if (v.toISODate) return v.startOf ? v.startOf("day") : DateTime.fromISO(v.toISODate()).startOf("day"); const d = DateTime.fromISO(String(v).replaceAll('"','').trim()); return d.isValid ? d.startOf("day") : null; }
function openPath(path) { app.workspace.openLinkText(path, "", false); }
function section(title, count, color) { const h = root.createEl("div", { cls: "ud-section" }); h.style.setProperty("--ud-color", `var(${color})`); h.createEl("span", { cls: "ud-section-dot" }); h.createEl("span", { text: title, cls: "ud-section-title" }); h.createEl("span", { text: String(count), cls: "ud-section-count" }); }
function renderCard(parent, p, colorVar) {
  const row = parent.createEl("div", { cls: "ud-card" });
  row.style.setProperty("--ud-border-color", `var(${colorVar})`);
  row.dataset.search = [p.file.name, p.type, p.status, p.subject, p.project].filter(Boolean).join(" ").toLowerCase();
  row.addEventListener("dblclick", () => openPath(p.file.path));
  const main = row.createEl("div", { cls: "ud-card-main" });
  const link = main.createEl("a", { text: p.file.name, cls: "ud-card-link" });
  link.addEventListener("click", e => { e.stopPropagation(); openPath(p.file.path); });
  const meta = main.createEl("div", { cls: "ud-card-meta" });
  for (const x of [p.status, p.subject, p.project].filter(Boolean)) meta.createEl("span", { text: String(x), cls: "ud-card-tag" });
  const d = toDate(p.due_date);
  if (d) {
    const days = Math.ceil(d.diff(today, "days").days);
    const tag = meta.createEl("span", { text: `${d.day} ${months[d.month-1]}`, cls: "ud-card-tag" });
    if (p.status === "Готово") tag.style.color = "var(--ud-status-done)";
    else if (days < 0) tag.style.color = "var(--ud-status-overdue)";
    else if (days === 0) tag.style.color = "var(--ud-status-today)";
    else if (days <= 2) tag.style.color = "var(--ud-status-soon)";
  }
}

const pages = dv.pages(`"${FOLDER}"`).where(p =>
  p.file.name !== `MOC — ${TITLE}` &&
  !p.file.name.startsWith("_Index_of_") &&
  !p.file.name.startsWith("._Index_of_") &&
  !p.file.name.startsWith("MOC —")
).sort(p => p.file.name).array();
const active = pages.filter(p => p.status && p.status !== "Готово").length;
const withDue = pages.filter(p => p.due_date && p.status !== "Готово").length;
const hero = root.createEl("div", { cls: "ud-hero" });
const left = hero.createEl("div"); left.createEl("h1", { text: `MOC — ${TITLE}` }); left.createEl("p", { text: `Автоматическая карта материалов из папки: ${FOLDER}` });
const stats = hero.createEl("div", { cls: "ud-stat-grid" });
for (const s of [["Материалов", pages.length, "--ud-teal"], ["Активно", active, "--ud-status-soon"], ["Со сроком", withDue, "--ud-status-today"]]) {
  const item = stats.createEl("div", { cls: "ud-stat" }); item.style.setProperty("--ud-color", `var(${s[2]})`); item.createEl("strong", { text: String(s[1]) }); item.createEl("span", { text: s[0] });
}
const search = root.createEl("div", { cls: "ud-search" }); search.createEl("span", { text: "Поиск", cls: "ud-search-label" }); const input = search.createEl("input", { type: "search", placeholder: "Фильтр по материалам..." });
input.addEventListener("input", () => { const term = input.value.trim().toLowerCase(); root.querySelectorAll(".ud-card[data-search]").forEach(el => el.style.display = !term || el.dataset.search.includes(term) ? "" : "none"); });
const byType = {};
for (const p of pages) { const t = p.type || "Разное"; (byType[t] ??= []).push(p); }
for (const [type, items] of Object.entries(byType).sort((a,b) => a[0].localeCompare(b[0], "ru"))) {
  const c = typeColors[type] || "--ud-frost";
  section(type, items.length, c);
  const list = root.createEl("div", { cls: "ud-list" });
  for (const p of items) renderCard(list, p, c);
}
if (!pages.length) root.createEl("div", { text: "В этой папке пока нет материалов.", cls: "ud-empty" });
```

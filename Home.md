---
cssclasses:
  - university-dashboard
---

# Рабочий стол

```dataviewjs
const root = dv.container;
root.classList.add("university-dashboard", "ud-page");
root.innerHTML = "";

const SYSTEM = {
  today: DateTime.now().startOf("day"),
  soonDays: 2,
  months: ["янв", "фев", "мар", "апр", "мая", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"],
  colors: {
    "ДЗ": "--ud-blue", "Лекция": "--ud-green", "Конспект": "--ud-teal",
    "Проект": "--ud-orange", "Лаба": "--ud-purple", "Экзамен": "--ud-red",
    "Разное": "--ud-frost"
  }
};

function toDate(value) {
  if (!value) return null;
  if (value.toISODate) return value.startOf ? value.startOf("day") : DateTime.fromISO(value.toISODate()).startOf("day");
  const raw = String(value).replaceAll('"', '').trim();
  const d = DateTime.fromISO(raw);
  return d.isValid ? d.startOf("day") : null;
}
function dateText(d) { return d ? `${d.day} ${SYSTEM.months[d.month - 1]}` : "без даты"; }
function daysLeft(d) { return Math.ceil(d.diff(SYSTEM.today, "days").days); }
function colorByDays(days, done=false) {
  if (done) return "--ud-status-done";
  if (days < 0) return "--ud-status-overdue";
  if (days === 0) return "--ud-status-today";
  if (days <= SYSTEM.soonDays) return "--ud-status-soon";
  return "--ud-status-ok";
}
function statusText(days) {
  if (days < 0) return `просрочено ${Math.abs(days)} дн.`;
  if (days === 0) return "сегодня";
  if (days === 1) return "завтра";
  return `через ${days} дн.`;
}
function openPath(path) { app.workspace.openLinkText(path, "", false); }
async function setStatus(path, status) {
  const file = app.vault.getAbstractFileByPath(path);
  if (!file) return;
  await app.fileManager.processFrontMatter(file, fm => { fm.status = status; });
  app.commands.executeCommandById("dataview:dataview-force-refresh-views");
}
function button(parent, label, code, onClick, cls="") {
  const b = parent.createEl("button", { cls: `ud-btn ${cls}`.trim() });
  b.createEl("span", { text: code, cls: "ud-symbol" });
  b.createEl("span", { text: label, cls: "ud-btn-label" });
  b.addEventListener("click", onClick);
  return b;
}
function card(parent, p, opts={}) {
  const done = p.status === "Готово" || opts.done;
  const d = toDate(p.due_date);
  const days = d ? daysLeft(d) : 9999;
  const color = opts.color || colorByDays(days, done);
  const row = parent.createEl("div", { cls: "ud-card" });
  row.style.setProperty("--ud-border-color", `var(${color})`);
  row.dataset.search = [p.file?.name, p.subject, p.type, p.status, p.file?.folder].filter(Boolean).join(" ").toLowerCase();
  row.addEventListener("dblclick", e => { if (!e.target.closest("button")) openPath(p.file.path); });
  const main = row.createEl("div", { cls: "ud-card-main" });
  const link = main.createEl("a", { text: p.file.name, cls: "ud-card-link" });
  link.addEventListener("click", e => { e.stopPropagation(); openPath(p.file.path); });
  const meta = main.createEl("div", { cls: "ud-card-meta" });
  if (p.subject) meta.createEl("span", { text: p.subject, cls: "ud-card-tag" });
  if (p.type) meta.createEl("span", { text: p.type, cls: "ud-card-tag" });
  if (p.status) meta.createEl("span", { text: p.status, cls: "ud-card-tag" });
  if (p.file?.folder) meta.createEl("span", { text: p.file.folder.replace("10-Университет/", ""), cls: "ud-card-tag" });
  if (d) {
    const date = row.createEl("div", { cls: "ud-date-block" });
    date.createEl("div", { text: dateText(d), cls: "ud-date-main" });
    date.createEl("div", { text: statusText(days), cls: `ud-date-sub ${days < 0 ? "ud-urgent" : days === 0 ? "ud-today" : days <= 2 ? "ud-soon" : ""}` });
  }
  if (opts.canToggle) {
    const status = row.createEl("div", { cls: "ud-status-block" });
    const b = status.createEl("button", { text: done ? "Вернуть" : "Готово", cls: `ud-pill ${done ? "ud-pill-done" : "ud-pill-ok"}` });
    b.addEventListener("click", e => { e.stopPropagation(); setStatus(p.file.path, done ? "В работе" : "Готово"); });
  }
  return row;
}
function section(parent, title, count, color) {
  const h = parent.createEl("div", { cls: "ud-section" });
  h.style.setProperty("--ud-color", `var(${color})`);
  h.createEl("span", { cls: "ud-section-line" });
  h.createEl("span", { text: title, cls: "ud-section-title" });
  h.createEl("span", { text: String(count), cls: "ud-section-count" });
  return h;
}

const all = dv.pages().array();
const withDue = all.map(p => ({ p, d: toDate(p.due_date) })).filter(x => x.d);
const activeDue = withDue.filter(x => x.p.status !== "Готово").map(x => Object.assign(x.p, { _date: x.d, _days: daysLeft(x.d) })).sort((a,b) => a._date - b._date);
const overdue = activeDue.filter(p => p._days < 0).length;
const today = activeDue.filter(p => p._days === 0).length;
const soon = activeDue.filter(p => p._days > 0 && p._days <= SYSTEM.soonDays).length;

const hero = root.createEl("div", { cls: "ud-hero" });
const heroText = hero.createEl("div");
heroText.createEl("h1", { text: "Рабочий стол" });
heroText.createEl("p", { text: "Единая панель управления учёбой, сроками, проектами и расписанием." });
const stats = hero.createEl("div", { cls: "ud-stat-grid" });
for (const s of [
  ["Активных сроков", activeDue.length, "--ud-blue"],
  ["Просрочено", overdue, "--ud-status-overdue"],
  ["Сегодня", today, "--ud-status-today"],
  ["Скоро", soon, "--ud-status-soon"]
]) {
  const item = stats.createEl("div", { cls: "ud-stat" });
  item.style.setProperty("--ud-color", `var(${s[2]})`);
  item.createEl("strong", { text: String(s[1]) });
  item.createEl("span", { text: s[0] });
}

const actions = root.createEl("div", { cls: "ud-action-row" });
button(actions, "Новая заметка", "N", async () => {
  const templater = app.plugins.plugins["templater-obsidian"];
  const template = app.vault.getAbstractFileByPath("50-Система/Шаблоны/Новая заметка.md");
  if (!templater) return new Notice("Плагин Templater не найден");
  if (!template) return new Notice("Шаблон не найден");
  await templater.templater.create_new_note_from_template(template, app.vault.getRoot(), "Новая заметка", true);
}, "ud-btn-primary");
button(actions, "Скачать расписание", "S", async () => {
  try { app.commands.executeCommandById("sirius-schedule:sirius-update-from-site"); }
  catch(e) { new Notice("Команда автообновления недоступна: " + e.message); }
});
button(actions, "Проверка vault", "Q", () => openPath("50-Система/Отчёты/VAULT_HEALTH.md"));
button(actions, "Все дедлайны", "D", () => openPath("50-Система/Дашборды/Дедлайны.md"));

const quick = root.createEl("div", { cls: "ud-quick-grid" });
for (const q of [
  ["Дедлайны", "50-Система/Дашборды/Дедлайны.md", "DL", "ud-quick-deadlines"],
  ["Университет", "10-Университет/Университет.md", "UN", "ud-quick-uni"],
  ["Проекты", "20-Проекты/Проекты.md", "PR", "ud-quick-projects"],
  ["Личное", "30-Личное/Личное.md", "ME", "ud-quick-personal"]
]) {
  const c = quick.createEl("div", { cls: `ud-quick-card ${q[3]}` });
  c.addEventListener("click", () => openPath(q[1]));
  c.createEl("span", { text: q[2], cls: "ud-quick-code" });
  c.createEl("span", { text: q[0], cls: "ud-quick-label" });
}

const search = root.createEl("div", { cls: "ud-search" });
search.createEl("span", { text: "Поиск", cls: "ud-search-label" });
const input = search.createEl("input", { type: "search", placeholder: "Фильтр по названию, предмету, типу, статусу..." });
input.addEventListener("input", () => {
  const term = input.value.trim().toLowerCase();
  root.querySelectorAll(".ud-card[data-search]").forEach(el => el.style.display = !term || el.dataset.search.includes(term) ? "" : "none");
});

section(root, "Требуют внимания", activeDue.length, overdue ? "--ud-status-overdue" : soon ? "--ud-status-soon" : "--ud-status-ok");
const urgentList = root.createEl("div", { cls: "ud-list" });
for (const p of activeDue.slice(0, 12)) card(urgentList, p, { canToggle: true });
if (!activeDue.length) urgentList.createEl("div", { text: "Активных дедлайнов нет. Можно спокойно планировать дальше.", cls: "ud-empty" });

const uniFolder = app.vault.getAbstractFileByPath("10-Университет");
const subjects = (uniFolder?.children || []).filter(f => f.children).map(f => f.name).sort((a,b) => a.localeCompare(b, "ru"));
section(root, "Предметы", subjects.length, "--ud-teal");
const subList = root.createEl("div", { cls: "ud-list ud-grid-2" });
for (const sub of subjects) {
  const path = `10-Университет/${sub}`;
  const pages = dv.pages(`"${path}"`).where(p => !p.file.name.startsWith("MOC") && !p.file.name.startsWith("_Index")).array();
  const active = pages.filter(p => p.status && p.status !== "Готово").length;
  const due = pages.filter(p => p.due_date && p.status !== "Готово").length;
  const fake = { file: { name: sub, path: `${path}/MOC — ${sub}.md`, folder: path }, subject: `${pages.length} заметок`, type: active ? `${active} активно` : "спокойно", status: due ? `${due} сроков` : "" };
  card(subList, fake, { color: active ? "--ud-status-soon" : "--ud-teal" });
}
```

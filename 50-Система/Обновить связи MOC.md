---
cssclasses:
  - university-dashboard
---

# Обслуживание MOC

```dataviewjs
const root = dv.container;
root.classList.add("university-dashboard", "ud-page");
root.innerHTML = "";
function openPath(path) { app.workspace.openLinkText(path, "", false); }
const mocFiles = app.vault.getMarkdownFiles().filter(f => f.name.startsWith("MOC —"));
const pages = dv.pages().where(p => !p.file.name.startsWith("MOC —") && !p.file.name.startsWith("_Index_of_")).array();
const hero = root.createEl("div", { cls: "ud-hero" });
const left = hero.createEl("div");
left.createEl("h1", { text: "Обслуживание MOC" });
left.createEl("p", { text: "MOC теперь динамические: списки собираются через DataviewJS, поэтому ручное дописывание ссылок больше не нужно." });
const stats = hero.createEl("div", { cls: "ud-stat-grid" });
for (const s of [["MOC", mocFiles.length, "--ud-teal"], ["Заметок", pages.length, "--ud-blue"], ["Активных", pages.filter(p => p.status && p.status !== "Готово").length, "--ud-status-soon"], ["Со сроком", pages.filter(p => p.due_date).length, "--ud-status-today"]]) {
  const item = stats.createEl("div", { cls: "ud-stat" });
  item.style.setProperty("--ud-color", `var(${s[2]})`);
  item.createEl("strong", { text: String(s[1]) });
  item.createEl("span", { text: s[0] });
}
const actions = root.createEl("div", { cls: "ud-action-row" });
for (const a of [
  ["Открыть отчёт проверки", "50-Система/Отчёты/VAULT_HEALTH.md", "Q"],
  ["Рабочий стол", "Home.md", "H"],
  ["Дедлайны", "50-Система/Дашборды/Дедлайны.md", "D"]
]) {
  const btn = actions.createEl("button", { cls: "ud-btn" });
  btn.createEl("span", { text: a[2], cls: "ud-symbol" });
  btn.createEl("span", { text: a[0] });
  btn.addEventListener("click", () => openPath(a[1]));
}
const info = root.createEl("div", { cls: "ud-empty" });
info.innerHTML = "Для полной проверки запусти в терминале:<br><code>python 50-Система/Скрипты/vault-health-check.py</code>";
const section = root.createEl("div", { cls: "ud-section" });
section.style.setProperty("--ud-color", "var(--ud-teal)");
section.createEl("span", { cls: "ud-section-dot" });
section.createEl("span", { text: "MOC-файлы", cls: "ud-section-title" });
section.createEl("span", { text: String(mocFiles.length), cls: "ud-section-count" });
const list = root.createEl("div", { cls: "ud-list" });
for (const moc of mocFiles.sort((a,b) => a.path.localeCompare(b.path, "ru"))) {
  const row = list.createEl("div", { cls: "ud-card" });
  row.style.setProperty("--ud-border-color", "var(--ud-teal)");
  row.addEventListener("dblclick", () => openPath(moc.path));
  const main = row.createEl("div", { cls: "ud-card-main" });
  const link = main.createEl("a", { text: moc.basename, cls: "ud-card-link" });
  link.addEventListener("click", e => { e.stopPropagation(); openPath(moc.path); });
  const meta = main.createEl("div", { cls: "ud-card-meta" });
  meta.createEl("span", { text: moc.parent.path, cls: "ud-card-tag" });
  meta.createEl("span", { text: new Date(moc.stat.mtime).toLocaleDateString("ru-RU"), cls: "ud-card-tag" });
}
```

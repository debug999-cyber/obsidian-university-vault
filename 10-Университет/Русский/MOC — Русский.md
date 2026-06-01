---
cssclasses:
  - university-dashboard
---

```dataviewjs
const SUBJECT = "Русский";
const FOLDER = "10-Университет/Русский";
const MOC_NAME = `MOC — ${SUBJECT}`;
const root = dv.container;
root.classList.add("university-dashboard");

const MONTHS_FULL = [
  "января", "февраля", "марта", "апреля", "мая", "июня",
  "июля", "августа", "сентября", "октября", "ноября", "декабря"
];

function plural(number, forms) {
  const abs = Math.abs(number) % 100;
  const last = abs % 10;
  if (abs > 10 && abs < 20) return forms[2];
  if (last > 1 && last < 5) return forms[1];
  if (last === 1) return forms[0];
  return forms[2];
}

function toDate(value) {
  if (!value) return null;
  if (typeof value === "object" && typeof value.toFormat === "function") return value;
  const parsed = DateTime.fromISO(String(value));
  return parsed.isValid ? parsed : null;
}

function openPath(path) {
  if (!path) return;
  app.workspace.openLinkText(path, "", false);
}

function makeInteractive(element, handler, label) {
  element.setAttribute("role", "button");
  element.setAttribute("tabindex", "0");
  if (label) element.setAttribute("aria-label", label);
  element.addEventListener("click", handler);
  element.addEventListener("keydown", event => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      handler(event);
    }
  });
}

function sectionColor(name) {
  const key = String(name || "").toLowerCase();
  if (key.includes("дз") || key.includes("лабо")) return "var(--ud-accent-warning)";
  if (key.includes("экзам") || key.includes("контроль")) return "var(--ud-accent-urgent)";
  if (key.includes("проект")) return "var(--ud-accent-action)";
  if (key.includes("лекц") || key.includes("консп")) return "var(--ud-accent-success)";
  return "var(--ud-accent-action)";
}

function statePill(item) {
  if (item.status === "Готово") return { cls: "done", text: "Готово" };
  if (item._days !== null && item._days < 0) return { cls: "urgent", text: "Просрочено" };
  if (item._days === 0) return { cls: "warning", text: "Сегодня" };
  if (item._days !== null && item._days <= 3) return { cls: "warning", text: item._days === 1 ? "Завтра" : `Через ${item._days} дн.` };
  if (item.status) return { cls: "info", text: item.status };
  return null;
}

const page = root.createEl("div", { cls: "ud-page" });
const today = DateTime.now().startOf("day");
const items = dv.pages(`"${FOLDER}"`)
  .where(page => page.file.name !== MOC_NAME && !page.file.name.startsWith("_Index_of_") && !page.file.name.startsWith("._"))
  .array()
  .map(page => {
    const due = toDate(page.due_date);
    const created = toDate(page.created);
    const daysLeft = due ? Math.ceil(due.startOf("day").diff(today, "days").days) : null;
    const folderTail = (page.file.folder || "").replace(`${FOLDER}/`, "");
    const group = folderTail.split("/")[0] || "Общее";
    return {
      ...page,
      _group: group,
      _due: due,
      _created: created,
      _days: daysLeft,
      _dateShort: due ? `${due.day} ${MONTHS_FULL[due.month - 1]}` : "",
      _dateLong: due ? `${due.day} ${MONTHS_FULL[due.month - 1]} ${due.year}` : ""
    };
  })
  .sort((a, b) => a.file.name.localeCompare(b.file.name, "ru"));

const groupsMap = new Map();
for (const item of items) {
  if (!groupsMap.has(item._group)) groupsMap.set(item._group, []);
  groupsMap.get(item._group).push(item);
}
const groups = [...groupsMap.entries()].sort((a, b) => a[0].localeCompare(b[0], "ru"));

const activeCount = items.filter(item => item.status && item.status !== "Готово").length;
const deadlineItems = items.filter(item => item._due && item.status !== "Готово").sort((a, b) => a._due.toMillis() - b._due.toMillis());
const urgentItems = deadlineItems.filter(item => item._days <= 3).slice(0, 5);
const noteTypes = new Set(items.map(item => item.type).filter(Boolean));
const latestCreated = items
  .filter(item => item._created)
  .sort((a, b) => b._created.toMillis() - a._created.toMillis())[0] || null;

const hero = page.createEl("section", { cls: "ud-note-hero" });
hero.createEl("div", { cls: "ud-note-eyebrow", text: "Map of Content" });
hero.createEl("h1", { cls: "ud-note-title", text: SUBJECT });
hero.createEl("p", {
  cls: "ud-note-sub",
  text: items.length
    ? `Автоматический обзор предмета: ${items.length} ${plural(items.length, ["материал", "материала", "материалов"])} в ${groups.length} ${plural(groups.length, ["разделе", "разделах", "разделах"])}.`
    : "Пока нет заметок по этому предмету."
});

const statGrid = hero.createEl("div", { cls: "ud-stat-grid" });
[
  ["Материалы", items.length, `${groups.length} ${plural(groups.length, ["раздел", "раздела", "разделов"])}`],
  ["В работе", activeCount, activeCount ? "Есть активные заметки" : "Всё закрыто"],
  ["Сроки", deadlineItems.length, deadlineItems.length ? "Есть заметки с due_date" : "Без дедлайнов"],
  ["Типы", noteTypes.size, noteTypes.size ? "Разные форматы материалов" : "Тип не указан"]
].forEach(([label, value, meta]) => {
  const card = statGrid.createEl("div", { cls: "ud-stat-card" });
  card.createEl("div", { cls: "ud-stat-label", text: String(label) });
  card.createEl("div", { cls: "ud-stat-value", text: String(value) });
  card.createEl("div", { cls: "ud-stat-meta", text: String(meta) });
});

if (latestCreated) {
  const latestMeta = statGrid.createEl("div", { cls: "ud-stat-card" });
  latestMeta.style.gridColumn = items.length ? "span 2" : "span 1";
  latestMeta.createEl("div", { cls: "ud-stat-label", text: "Последняя заметка" });
  latestMeta.createEl("div", { cls: "ud-stat-value", text: latestCreated.file.name });
  latestMeta.createEl("div", {
    cls: "ud-stat-meta",
    text: latestCreated._created ? `Создана ${latestCreated._created.day} ${MONTHS_FULL[latestCreated._created.month - 1]}` : latestCreated.file.path
  });
}

const searchWrap = page.createEl("div", { cls: "ud-search-wrap" });
searchWrap.createEl("span", { cls: "ud-icon ud-search-icon", text: "search" });
const searchInput = searchWrap.createEl("input", {
  cls: "ud-search ud-focus-ring",
  attr: {
    type: "text",
    placeholder: `Поиск по предмету «${SUBJECT}»...`,
    "aria-label": `Поиск по предмету ${SUBJECT}`
  }
});

const renderedSections = [];

function renderCard(parent, item) {
  const card = parent.createEl("div", { cls: "ud-card ud-searchable ud-focus-ring" });
  card.style.setProperty("--ud-border-color", item._due && item._days !== null && item._days < 0 ? "var(--ud-accent-urgent)" : item._due ? "var(--ud-accent-warning)" : "var(--ud-accent-action)");
  makeInteractive(card, () => openPath(item.file.path), `Открыть ${item.file.name}`);

  const main = card.createEl("div", { cls: "ud-card-main" });
  main.createEl("div", { cls: "ud-card-link ud-static-title", text: item.file.name });
  const meta = main.createEl("div", { cls: "ud-card-meta" });
  if (item.type) meta.createEl("span", { cls: "ud-card-tag", text: item.type });
  if (item.priority) meta.createEl("span", { cls: "ud-card-tag", text: item.priority });
  if (item.status && item.status !== "Готово") meta.createEl("span", { cls: "ud-card-tag", text: item.status });

  if (item._due) {
    const dateBlock = card.createEl("div", { cls: "ud-date-block" });
    dateBlock.createEl("div", { cls: "ud-date-main", text: item._dateShort });
    const dateSub = item._days < 0
      ? `Просрочено на ${Math.abs(item._days)} дн.`
      : item._days === 0
        ? "Сегодня"
        : item._days === 1
          ? "Завтра"
          : `Через ${item._days} дн.`;
    dateBlock.createEl("div", { cls: `ud-date-sub ${item._days < 0 ? "ud-urgent" : item._days <= 3 ? "ud-soon" : ""}`.trim(), text: dateSub });
  }

  const pill = statePill(item);
  if (pill) {
    const statusBlock = card.createEl("div", { cls: "ud-status-block" });
    statusBlock.createEl("span", { cls: `ud-task-tag ${pill.cls}`, text: pill.text });
  }

  return {
    element: card,
    text: [item.file.name, item.type, item.status, item.priority, item._group, item._dateLong].filter(Boolean).join(" ").toLowerCase()
  };
}

if (urgentItems.length) {
  const urgentSection = page.createEl("section", { cls: "ud-note-section" });
  const header = urgentSection.createEl("div", { cls: "ud-section" });
  header.style.setProperty("--ud-color", "var(--ud-accent-urgent)");
  header.createEl("span", { cls: "ud-section-dot" });
  header.createEl("span", { cls: "ud-section-title", text: "Срочно" });
  const countEl = header.createEl("span", { cls: "ud-section-count", text: String(urgentItems.length) });
  const list = urgentSection.createEl("div", { cls: "ud-list" });
  const cards = urgentItems.map(item => renderCard(list, item));
  const emptyEl = list.createEl("div", { cls: "ud-empty", text: "Ничего не найдено." });
  emptyEl.hidden = true;
  renderedSections.push({ section: urgentSection, countEl, cards, defaultCount: urgentItems.length, emptyEl });
}

for (const [groupName, groupItems] of groups) {
  const section = page.createEl("section", { cls: "ud-note-section" });
  const header = section.createEl("div", { cls: "ud-section" });
  header.style.setProperty("--ud-color", sectionColor(groupName));
  header.createEl("span", { cls: "ud-section-dot" });
  header.createEl("span", { cls: "ud-section-title", text: groupName });
  const countEl = header.createEl("span", { cls: "ud-section-count", text: String(groupItems.length) });

  const list = section.createEl("div", { cls: "ud-list" });
  const cards = groupItems.map(item => renderCard(list, item));
  const emptyEl = list.createEl("div", { cls: "ud-empty", text: "Ничего не найдено." });
  emptyEl.hidden = true;

  renderedSections.push({ section, countEl, cards, defaultCount: groupItems.length, emptyEl });
}

if (renderedSections.length === 0) {
  page.createEl("div", { cls: "ud-empty", text: "Пока нет заметок по этому предмету." });
}

function applySearch() {
  const term = searchInput.value.trim().toLowerCase();

  for (const section of renderedSections) {
    let visibleCount = 0;
    for (const card of section.cards) {
      const visible = !term || card.text.includes(term);
      card.element.hidden = !visible;
      if (visible) visibleCount += 1;
    }
    section.countEl.textContent = String(term ? visibleCount : section.defaultCount);
    section.emptyEl.hidden = visibleCount > 0;
    section.section.hidden = term && visibleCount === 0;
  }
}

searchInput.addEventListener("input", applySearch);
searchInput.addEventListener("keydown", event => {
  if (event.key === "Escape") {
    searchInput.value = "";
    applySearch();
    searchInput.blur();
  }
});

applySearch();
```

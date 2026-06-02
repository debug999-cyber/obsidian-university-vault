---
cssclasses:
  - university-dashboard
sticker: lucide//home
banner:
---

```dataviewjs
const root = dv.container;
root.classList.add("university-dashboard");

const WEEKDAYS = [
  "Воскресенье", "Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"
];
const MONTHS_FULL = [
  "января", "февраля", "марта", "апреля", "мая", "июня",
  "июля", "августа", "сентября", "октября", "ноября", "декабря"
];
const SUBJECT_ICONS = {
  "Математика": "functions",
  "Информатика": "terminal",
  "Биология": "biotech",
  "Русский": "menu_book",
  "Английский": "language",
  "История": "history_edu",
  "География": "public",
  "Физика": "rocket_launch",
  "Физра": "sports_gymnastics",
  "Литература": "auto_stories",
  "Обществознание": "gavel",
  "ПИД": "design_services",
  "ОП": "psychology",
  "ВВС": "campaign",
  "Другое": "widgets"
};

const shell = root.createEl("div", { cls: "ud-shell" });
const themeStorageKey = "ud-shell-theme";
const OBSIDIAN_BASE_THEMES = {
  light: "moonstone",
  dark: "obsidian"
};
const THEME_TRANSITION_DURATION = 560;
const THEME_TRANSITION_STYLE_ID = "ud-global-theme-transition-style";
let themeToggle = null;
let isThemeSwitching = false;
let themeTransitionTimeout = null;

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

function createIcon(parent, icon, cls = "ud-icon") {
  return parent.createEl("span", { cls, text: icon });
}

function isContentPage(page, excludedNames = []) {
  const name = page.file?.name || "";
  return (
    name &&
    !name.startsWith("_Index_of_") &&
    !name.startsWith("._") &&
    !name.startsWith("MOC") &&
    !excludedNames.includes(name)
  );
}

function folderPages(folder, excludedNames = []) {
  return dv.pages(`"${folder}"`)
    .where(page => isContentPage(page, excludedNames))
    .array();
}

function openPath(path) {
  if (!path) return;
  app.workspace.openLinkText(path, "", false);
}

function makeInteractive(element, handler, ariaLabel = "Открыть") {
  element.setAttribute("role", "button");
  element.setAttribute("tabindex", "0");
  element.setAttribute("aria-label", ariaLabel);
  element.addEventListener("click", handler);
  element.addEventListener("keydown", event => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      handler(event);
    }
  });
}

function normalizeTheme(theme) {
  return theme === "dark" ? "dark" : "light";
}

function getWorkspaceTheme() {
  if (document.body.classList.contains("theme-dark")) return "dark";
  if (document.body.classList.contains("theme-light")) return "light";

  const appTheme = typeof app?.getTheme === "function" ? app.getTheme() : null;
  if (appTheme === OBSIDIAN_BASE_THEMES.dark) return "dark";
  if (appTheme === OBSIDIAN_BASE_THEMES.light) return "light";

  return window.matchMedia?.("(prefers-color-scheme: dark)")?.matches ? "dark" : "light";
}

function setShellTheme(theme) {
  const normalizedTheme = normalizeTheme(theme);
  const nextTheme = normalizedTheme === "dark" ? "light" : "dark";

  shell.setAttribute("data-ud-theme", normalizedTheme);
  localStorage.setItem(themeStorageKey, normalizedTheme);

  if (themeToggle) {
    themeToggle.setAttribute("aria-pressed", normalizedTheme === "dark" ? "true" : "false");
    themeToggle.setAttribute("aria-label", `Переключить весь Obsidian на ${nextTheme === "dark" ? "тёмную" : "светлую"} тему`);
    themeToggle.setAttribute("title", `Сейчас ${normalizedTheme === "dark" ? "тёмная" : "светлая"} тема. Нажмите, чтобы включить ${nextTheme === "dark" ? "тёмную" : "светлую"}.`);
  }
}

function ensureThemeTransitionStyle() {
  if (document.getElementById(THEME_TRANSITION_STYLE_ID)) return;

  const style = document.createElement("style");
  style.id = THEME_TRANSITION_STYLE_ID;
  style.textContent = `
    html.ud-theme-transitioning,
    body.ud-theme-transitioning,
    body.ud-theme-transitioning .app-container,
    body.ud-theme-transitioning .workspace,
    body.ud-theme-transitioning .workspace-ribbon,
    body.ud-theme-transitioning .workspace-tabs,
    body.ud-theme-transitioning .workspace-tab-header,
    body.ud-theme-transitioning .workspace-split,
    body.ud-theme-transitioning .workspace-leaf,
    body.ud-theme-transitioning .workspace-leaf-content,
    body.ud-theme-transitioning .view-header,
    body.ud-theme-transitioning .view-content,
    body.ud-theme-transitioning .markdown-preview-view,
    body.ud-theme-transitioning .markdown-source-view,
    body.ud-theme-transitioning .cm-editor,
    body.ud-theme-transitioning .cm-scroller,
    body.ud-theme-transitioning .modal,
    body.ud-theme-transitioning .prompt,
    body.ud-theme-transitioning .menu,
    body.ud-theme-transitioning .popover,
    body.ud-theme-transitioning .status-bar,
    body.ud-theme-transitioning .nav-folder-title,
    body.ud-theme-transitioning .nav-file-title,
    body.ud-theme-transitioning .tree-item-self,
    body.ud-theme-transitioning .setting-item,
    body.ud-theme-transitioning .titlebar,
    body.ud-theme-transitioning .ud-shell,
    body.ud-theme-transitioning .ud-shell *,
    body.ud-theme-transitioning *::before,
    body.ud-theme-transitioning *::after {
      transition-property: background-color, border-color, color, fill, stroke, box-shadow, text-shadow, opacity, filter !important;
      transition-duration: ${THEME_TRANSITION_DURATION}ms !important;
      transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    body.ud-theme-transitioning .cm-cursor,
    body.ud-theme-transitioning .cm-dropCursor,
    body.ud-theme-transitioning .workspace-leaf-resize-handle {
      transition: none !important;
    }
  `;
  document.head.appendChild(style);
}

function startGlobalThemeTransition() {
  ensureThemeTransitionStyle();
  window.clearTimeout(themeTransitionTimeout);

  document.documentElement.classList.add("ud-theme-transitioning");
  document.body.classList.add("ud-theme-transitioning");

  // Принудительно применяем transition-класс до смены CSS-переменных Obsidian.
  void document.body.offsetHeight;

  themeTransitionTimeout = window.setTimeout(() => {
    document.documentElement.classList.remove("ud-theme-transitioning");
    document.body.classList.remove("ud-theme-transitioning");
  }, THEME_TRANSITION_DURATION + 180);
}

async function setWorkspaceTheme(theme, { syncShell = true, smooth = true } = {}) {
  const normalizedTheme = normalizeTheme(theme);
  const obsidianTheme = OBSIDIAN_BASE_THEMES[normalizedTheme];

  if (syncShell) {
    setShellTheme(normalizedTheme);
  }

  if (smooth) {
    startGlobalThemeTransition();
    await new Promise(resolve => requestAnimationFrame(resolve));
  }

  try {
    if (typeof app?.changeTheme === "function") {
      await Promise.resolve(app.changeTheme(obsidianTheme));
    } else if (typeof app?.updateTheme === "function") {
      await Promise.resolve(app.updateTheme(obsidianTheme));
      if (typeof app?.vault?.setConfig === "function") {
        await Promise.resolve(app.vault.setConfig("theme", obsidianTheme));
      }
    } else {
      document.body.classList.toggle("theme-dark", normalizedTheme === "dark");
      document.body.classList.toggle("theme-light", normalizedTheme === "light");
      if (typeof Notice === "function") {
        new Notice("Тема переключена только визуально: API Obsidian changeTheme недоступен");
      }
    }

    requestAnimationFrame(() => setShellTheme(getWorkspaceTheme()));
  } catch (error) {
    console.error("UD theme toggle error", error);
    setShellTheme(getWorkspaceTheme());
    if (typeof Notice === "function") {
      new Notice("Не удалось переключить тему Obsidian");
    }
  }
}

function deadlineTone(item) {
  const priority = String(item.priority || "").toLowerCase();

  if (item._days < 0) {
    return {
      indicator: "red",
      tagClass: "urgent",
      tagText: `Просрочено`,
      metaDate: `на ${Math.abs(item._days)} дн.`
    };
  }

  if (item._days === 0 || priority === "high") {
    return {
      indicator: "red",
      tagClass: "urgent",
      tagText: "Сегодня",
      metaDate: "дедлайн"
    };
  }

  if (item._days === 1) {
    return {
      indicator: "orange",
      tagClass: "warning",
      tagText: "Завтра",
      metaDate: item._dateShort
    };
  }

  if (item._days <= 3) {
    return {
      indicator: "blue",
      tagClass: "info",
      tagText: `Через ${item._days} дн.`,
      metaDate: item._dateShort
    };
  }

  return {
    indicator: "blue",
    tagClass: "info",
    tagText: item._dateShort,
    metaDate: item._dateLong
  };
}

async function createNewNote(button) {
  const templaterPlugin = app.plugins.plugins["templater-obsidian"];
  if (!templaterPlugin) {
    new Notice("Плагин Templater не найден");
    return;
  }

  const templateFile = app.vault.getAbstractFileByPath("50-Система/Шаблоны/Новая заметка.md");
  if (!templateFile) {
    new Notice("Шаблон не найден: 50-Система/Шаблоны/Новая заметка.md");
    return;
  }

  if (button) {
    button.disabled = true;
    button.classList.add("is-loading");
  }

  try {
    await templaterPlugin.templater.create_new_note_from_template(
      templateFile,
      app.vault.getRoot(),
      "Новая заметка",
      true
    );
  } finally {
    if (button) {
      button.disabled = false;
      button.classList.remove("is-loading");
    }
  }
}

async function refreshSchedule(button) {
  if (button) {
    button.disabled = true;
    button.classList.add("is-loading");
  }

  try {
    app.commands.executeCommandById("sirius-schedule:sirius-reload");
    await new Promise(resolve => setTimeout(resolve, 800));
    new Notice("Расписание обновлено");
  } catch (error) {
    new Notice("Не удалось обновить расписание");
  } finally {
    if (button) {
      button.disabled = false;
      button.classList.remove("is-loading");
    }
  }
}

function createActionButton(parent, { icon, label, variant = "secondary", onClick }) {
  const button = parent.createEl("button", {
    cls: `ud-action-btn ${variant} ud-focus-ring`,
    attr: { type: "button" }
  });
  createIcon(button, icon);
  button.createEl("span", { text: label });
  button.addEventListener("click", () => onClick(button));
  return button;
}

function createBlock(parent, title, count) {
  const block = parent.createEl("section", { cls: "ud-block" });
  const header = block.createEl("div", { cls: "ud-block-header" });
  header.createEl("div", { cls: "ud-block-title", text: title });
  const countEl = header.createEl("div", { cls: "ud-block-count", text: String(count) });
  return { block, countEl };
}

const now = DateTime.now();
const today = now.startOf("day");
const greeting = now.hour < 6
  ? "Доброй ночи"
  : now.hour < 12
    ? "Доброе утро"
    : now.hour < 18
      ? "Добрый день"
      : "Добрый вечер";
const displayName = localStorage.getItem("ud-display-name") || "Студент";

const allDeadlinePages = dv.pages()
  .where(page => page.due_date)
  .array()
  .map(page => {
    const due = toDate(page.due_date);
    if (!due) return null;

    const normalizedDue = due.startOf("day");
    const daysLeft = Math.ceil(normalizedDue.diff(today, "days").days);

    return {
      ...page,
      _due: due,
      _days: daysLeft,
      _dateShort: `${due.day} ${MONTHS_FULL[due.month - 1]}`,
      _dateLong: `${due.day} ${MONTHS_FULL[due.month - 1]} ${due.year}`
    };
  })
  .filter(Boolean)
  .sort((a, b) => a._due.toMillis() - b._due.toMillis());

const activeDeadlines = allDeadlinePages.filter(page => page.status !== "Готово");
const urgentDeadlines = activeDeadlines.filter(page => page._days <= 3);
const urgentItems = urgentDeadlines.slice(0, 8);
const urgentTotal = urgentDeadlines.length;
const todayCount = activeDeadlines.filter(page => page._days === 0).length;
const overdueCount = activeDeadlines.filter(page => page._days < 0).length;
const nextDeadline = activeDeadlines[0] || null;

const universityPages = folderPages("10-Университет", ["Университет"]);
const projectPages = folderPages("20-Проекты", ["Проекты"]);
const personalPages = folderPages("30-Личное", ["Личное"]);
const activeProjects = projectPages.filter(page => page.status && page.status !== "Готово").length;

const subjectMap = new Map();
for (const page of universityPages) {
  const folder = (page.file.folder || "").replace("10-Университет/", "");
  const subject = folder.split("/")[0];
  if (!subject || subject.startsWith(".")) continue;
  if (!subjectMap.has(subject)) subjectMap.set(subject, []);
  subjectMap.get(subject).push(page);
}

const subjectRows = [...subjectMap.entries()]
  .map(([subject, pages]) => {
    const orderedPages = [...pages].sort((a, b) => a.file.name.localeCompare(b.file.name, "ru"));
    const active = orderedPages.filter(page => page.status && page.status !== "Готово").length;
    const total = orderedPages.length;
    const progress = total === 0 ? 0 : active === 0 ? 100 : Math.max(18, 100 - Math.round((active / total) * 100));
    const mocPath = `10-Университет/${subject}/MOC — ${subject}.md`;
    const mocFile = app.vault.getAbstractFileByPath(mocPath);

    return {
      subject,
      active,
      total,
      progress,
      icon: SUBJECT_ICONS[subject] || "school",
      progressClass: active === 0 ? "success" : progress < 50 ? "warning" : "info",
      path: mocFile ? mocPath : orderedPages[0]?.file?.path
    };
  })
  .filter(item => item.path)
  .sort((a, b) => b.active - a.active || a.subject.localeCompare(b.subject, "ru"));

const heroSummary = urgentTotal > 0
  ? `${urgentTotal} ${plural(urgentTotal, ["дедлайн", "дедлайна", "дедлайнов"])} в ближайшие 3 дня.${nextDeadline ? ` Самый близкий — ${nextDeadline.subject || "без предмета"}, ${deadlineTone(nextDeadline).tagText.toLowerCase()}.` : ""}`
  : `Срочных дел нет. В хранилище ${subjectRows.length} ${plural(subjectRows.length, ["предмет", "предмета", "предметов"])} и ${projectPages.length} ${plural(projectPages.length, ["проект", "проекта", "проектов"])}.`;

const quickCards = [
  {
    cls: "ud-quick-deadlines",
    featured: true,
    icon: "event",
    badge: urgentTotal > 0 ? String(urgentTotal) : null,
    badgeClass: "",
    label: "Дедлайны",
    meta: `${activeDeadlines.length} ${plural(activeDeadlines.length, ["задача", "задачи", "задач"])} • ${todayCount} сегодня`,
    path: "50-Система/Дашборды/Дедлайны.md"
  },
  {
    cls: "ud-quick-uni",
    featured: false,
    icon: "school",
    badge: null,
    badgeClass: "",
    label: "Университет",
    meta: `${subjectRows.length} ${plural(subjectRows.length, ["предмет", "предмета", "предметов"])}`,
    path: "10-Университет/Университет.md"
  },
  {
    cls: "ud-quick-projects",
    featured: false,
    icon: "code",
    badge: activeProjects > 0 ? String(activeProjects) : null,
    badgeClass: "blue",
    label: "Проекты",
    meta: `${projectPages.length} ${plural(projectPages.length, ["заметка", "заметки", "заметок"])}`,
    path: "20-Проекты/Проекты.md"
  },
  {
    cls: "ud-quick-personal",
    featured: false,
    icon: "person",
    badge: personalPages.length > 0 ? String(personalPages.length) : null,
    badgeClass: "green",
    label: "Личное",
    meta: `${personalPages.length} ${plural(personalPages.length, ["заметка", "заметки", "заметок"])}`,
    path: "30-Личное/Личное.md"
  }
];

const groups = {
  urgent: {
    items: [],
    countEl: null,
    emptyEl: null,
    defaultCount: urgentTotal,
    emptyText: "Срочных дел пока нет."
  },
  subjects: {
    items: [],
    countEl: null,
    emptyEl: null,
    defaultCount: subjectRows.length,
    emptyText: "Предметы пока не найдены."
  }
};

function registerSearch(groupName, element, text) {
  groups[groupName].items.push({
    element,
    text: String(text || "").toLowerCase()
  });
}

const savedTheme = getWorkspaceTheme();
setShellTheme(savedTheme);

const topBar = shell.createEl("div", { cls: "ud-top-bar" });
const topBarInner = topBar.createEl("div", { cls: "ud-top-bar-inner" });

const brand = topBarInner.createEl("div", { cls: "ud-brand" });
brand.createEl("span", { cls: "ud-brand-name", text: "Студпортал" });
brand.createEl("span", {
  cls: "ud-brand-meta",
  text: `${subjectRows.length} ${plural(subjectRows.length, ["предмет", "предмета", "предметов"])} • vault`
});

themeToggle = topBarInner.createEl("button", {
  cls: "ud-theme-toggle ud-focus-ring",
  attr: {
    type: "button",
    "aria-label": "Переключить тему Obsidian"
  }
});
themeToggle.createEl("span", { cls: "ud-theme-glow" });
createIcon(themeToggle, "wb_sunny", "ud-icon ud-track-icon ud-track-sun");
createIcon(themeToggle, "dark_mode", "ud-icon ud-track-icon ud-track-moon");
themeToggle.createEl("span", { cls: "ud-theme-knob" });
setShellTheme(savedTheme);

themeToggle.addEventListener("click", async () => {
  if (isThemeSwitching) return;

  const nextTheme = shell.getAttribute("data-ud-theme") === "dark" ? "light" : "dark";
  isThemeSwitching = true;

  // Кнопка анимируется как раньше, а весь интерфейс Obsidian получает временный
  // transition-класс перед сменой темы, поэтому цвета не прыгают резко.
  setShellTheme(nextTheme);
  themeToggle.classList.add("active");

  await setWorkspaceTheme(nextTheme, { syncShell: false, smooth: true });

  window.setTimeout(() => {
    themeToggle.classList.remove("active");
    isThemeSwitching = false;
  }, THEME_TRANSITION_DURATION);
});

const themeObserver = new MutationObserver(() => {
  if (isThemeSwitching) return;

  const workspaceTheme = getWorkspaceTheme();
  if (shell.getAttribute("data-ud-theme") !== workspaceTheme) {
    setShellTheme(workspaceTheme);
  }
});
themeObserver.observe(document.body, { attributes: true, attributeFilter: ["class"] });

const themeObserverCleanup = window.setInterval(() => {
  if (!root.isConnected) {
    themeObserver.disconnect();
    window.clearInterval(themeObserverCleanup);
  }
}, 1000);

const page = shell.createEl("div", { cls: "ud-page" });

const hero = page.createEl("section", { cls: "ud-hero" });
const heroCopy = hero.createEl("div", { cls: "ud-hero-copy" });
const heroGreeting = heroCopy.createEl("div", { cls: "ud-hero-greeting" });
heroGreeting.createEl("div", { text: `${greeting},` });
heroGreeting.createEl("div", { text: displayName });
heroCopy.createEl("p", { cls: "ud-hero-sub", text: heroSummary });

const heroActions = heroCopy.createEl("div", { cls: "ud-hero-actions" });
createActionButton(heroActions, {
  icon: "sync",
  label: "Обновить расписание",
  variant: "secondary",
  onClick: refreshSchedule
});
createActionButton(heroActions, {
  icon: "add_notes",
  label: "Новая заметка",
  variant: "primary",
  onClick: createNewNote
});

const heroDate = hero.createEl("div", { cls: "ud-hero-date" });
heroDate.createEl("div", { cls: "ud-hero-date-day", text: WEEKDAYS[now.weekday % 7] });
heroDate.createEl("div", { cls: "ud-hero-date-num", text: String(now.day) });
heroDate.createEl("div", { cls: "ud-hero-date-month", text: `${MONTHS_FULL[now.month - 1]} ${now.year}` });

const quickGrid = page.createEl("section", { cls: "ud-quick-grid" });
for (const item of quickCards) {
  const card = quickGrid.createEl("div", {
    cls: `ud-quick-card ${item.cls} ${item.featured ? "featured" : ""} ud-focus-ring`
  });
  makeInteractive(card, () => openPath(item.path), `Открыть раздел ${item.label}`);

  const iconWrap = card.createEl("div", { cls: "ud-quick-icon-wrap" });
  const icon = iconWrap.createEl("div", { cls: "ud-quick-icon" });
  createIcon(icon, item.icon);

  if (item.badge) {
    iconWrap.createEl("div", {
      cls: `ud-quick-badge ${item.badgeClass}`.trim(),
      text: item.badge
    });
  }

  const textWrap = card.createEl("div", { cls: "ud-quick-copy" });
  textWrap.createEl("div", { cls: "ud-quick-label", text: item.label });
  textWrap.createEl("div", { cls: "ud-quick-meta", text: item.meta });
}

const searchWrap = page.createEl("div", { cls: "ud-search-wrap" });
createIcon(searchWrap, "search", "ud-icon ud-search-icon");
const searchInput = searchWrap.createEl("input", {
  cls: "ud-search ud-focus-ring",
  attr: {
    type: "text",
    placeholder: "Поиск по заметкам, задачам и предметам...",
    "aria-label": "Поиск по заметкам, задачам и предметам"
  }
});

const urgentBlock = createBlock(page, "Требуют внимания", urgentTotal);
groups.urgent.countEl = urgentBlock.countEl;
const urgentList = urgentBlock.block.createEl("div", { cls: "ud-task-list" });

if (urgentItems.length === 0) {
  groups.urgent.emptyEl = urgentList.createEl("div", { cls: "ud-empty", text: groups.urgent.emptyText });
} else {
  for (const item of urgentItems) {
    const tone = deadlineTone(item);
    const card = urgentList.createEl("div", { cls: "ud-task-card ud-searchable ud-focus-ring" });
    makeInteractive(card, () => openPath(item.file.path), `Открыть заметку ${item.file.name}`);

    const main = card.createEl("div", { cls: "ud-task-main" });
    main.createEl("div", { cls: `ud-task-indicator ${tone.indicator}` });

    const textWrap = main.createEl("div", { cls: "ud-task-copy" });
    textWrap.createEl("div", { cls: "ud-task-text", text: item.file.name });
    textWrap.createEl("div", {
      cls: "ud-task-meta",
      text: [item.subject || "Без предмета", item.type || "Заметка", tone.metaDate].filter(Boolean).join(" • ")
    });

    card.createEl("div", { cls: `ud-task-tag ${tone.tagClass}`, text: tone.tagText });

    registerSearch(
      "urgent",
      card,
      [item.file.name, item.subject, item.type, item.status, tone.tagText, tone.metaDate].filter(Boolean).join(" ")
    );
  }

  groups.urgent.emptyEl = urgentList.createEl("div", { cls: "ud-empty", text: "Ничего не найдено." });
  groups.urgent.emptyEl.hidden = true;
}

const subjectsBlock = createBlock(page, "Предметы", subjectRows.length);
groups.subjects.countEl = subjectsBlock.countEl;
const subjectList = subjectsBlock.block.createEl("div", { cls: "ud-subject-list" });

if (subjectRows.length === 0) {
  groups.subjects.emptyEl = subjectList.createEl("div", { cls: "ud-empty", text: groups.subjects.emptyText });
} else {
  for (const subject of subjectRows) {
    const card = subjectList.createEl("div", { cls: "ud-subject-card ud-searchable ud-focus-ring" });
    makeInteractive(card, () => openPath(subject.path), `Открыть предмет ${subject.subject}`);

    const main = card.createEl("div", { cls: "ud-subject-main" });
    const iconWrap = main.createEl("div", { cls: "ud-subject-icon" });
    createIcon(iconWrap, subject.icon);

    const info = main.createEl("div", { cls: "ud-subject-info" });
    info.createEl("div", { cls: "ud-subject-name", text: subject.subject });
    info.createEl("div", {
      cls: "ud-subject-meta",
      text: `${subject.total} ${plural(subject.total, ["заметка", "заметки", "заметок"])} • ${subject.active > 0 ? `${subject.active} в работе` : "Всё сдано"}`
    });

    const progressWrap = info.createEl("div", { cls: "ud-progress-wrap" });
    const progressTrack = progressWrap.createEl("div", { cls: "ud-progress-track" });
    const progressFill = progressTrack.createEl("div", { cls: `ud-progress-fill ${subject.progressClass}`.trim() });
    progressFill.style.width = `${subject.progress}%`;
    progressWrap.createEl("div", { cls: "ud-progress-text", text: `${subject.progress}%` });

    const circleWrap = card.createEl("div", { cls: "ud-circle-wrap" });
    circleWrap.createEl("div", { cls: "ud-circle-bg" });
    const circleFill = circleWrap.createEl("div", { cls: `ud-circle-fill ${subject.progressClass}`.trim() });
    circleFill.style.setProperty("--ud-progress", `${subject.progress}%`);
    const circleInner = circleFill.createEl("div", { cls: "ud-circle-inner" });
    circleInner.textContent = subject.progress >= 100 ? "✓" : String(subject.progress);

    registerSearch(
      "subjects",
      card,
      [subject.subject, subject.total, subject.active, subject.progress].join(" ")
    );
  }

  groups.subjects.emptyEl = subjectList.createEl("div", { cls: "ud-empty", text: "Ничего не найдено." });
  groups.subjects.emptyEl.hidden = true;
}

const footer = page.createEl("footer", { cls: "ud-footer" });
footer.createEl("div", { cls: "ud-footer-divider" });
footer.createEl("div", {
  cls: "ud-footer-text",
  text: `Obsidian University Vault • ${overdueCount} ${plural(overdueCount, ["просрочка", "просрочки", "просрочек"])} • стабильный layout`
});

const fabWrap = shell.createEl("div", { cls: "ud-fab-wrap" });
const fab = fabWrap.createEl("button", {
  cls: "ud-fab ud-focus-ring",
  attr: {
    type: "button",
    "aria-label": "Создать новую заметку"
  }
});
createIcon(fab, "add");
fab.addEventListener("click", () => createNewNote(fab));

function applySearch() {
  const term = searchInput.value.trim().toLowerCase();

  for (const group of Object.values(groups)) {
    let visibleCount = 0;

    for (const item of group.items) {
      const visible = !term || item.text.includes(term);
      item.element.hidden = !visible;
      if (visible) visibleCount += 1;
    }

    if (group.countEl) {
      group.countEl.textContent = String(term ? visibleCount : group.defaultCount);
    }

    if (group.emptyEl) {
      if (group.defaultCount === 0) {
        group.emptyEl.hidden = false;
        group.emptyEl.textContent = group.emptyText;
      } else {
        group.emptyEl.hidden = visibleCount > 0;
        group.emptyEl.textContent = term ? "Ничего не найдено." : group.emptyText;
      }
    }
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
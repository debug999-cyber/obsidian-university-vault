---
cssclasses:
  - university-dashboard
---

# Рабочий стол

---

## Быстрые ссылки

```dataviewjs
const container = dv.container; container.classList.add("university-dashboard"); const grid = container.createEl("div", { cls: "ud-quick-grid" }); const links = [ { icon: "event_note", label: "Дедлайны", path: "Дедлайны", cls: "ud-quick-deadlines", isNote: true }, { icon: "school", label: "Университет", folder: "10-Университет", cls: "ud-quick-uni", isNote: false }, { icon: "code", label: "Проекты", folder: "20-Проекты", cls: "ud-quick-projects", isNote: false }, { icon: "person", label: "Личное", folder: "30-Личное", cls: "ud-quick-personal", isNote: false } ]; async function openFolderNote(folder, label) { const path = folder + "/" + label + ".md"; let file = app.vault.getAbstractFileByPath(path); const lines = [ "---", "cssclasses:", " - university-dashboard", "---", "", "# " + label, "", "> Автоматическая навигация", "", "```dataviewjs", "const container = dv.container;", "container.classList.add(\"university-dashboard\");", "", "const pages = dv.pages(\"" + folder + "\")", " .where(p => !p.file.name.startsWith(\"_Index_of_\") && !p.file.name.startsWith(\"MOC\") && p.file.name != \"" + label + "\")", " .sort(p => p.file.name);", "", "const byFolder = {};", "for (const p of pages) {", " const key = p.file.folder.replace(\"" + folder + "/\", \"\").split(\"/\")[0] || \"Разное\";", " if (!byFolder[key]) byFolder[key] = [];", " byFolder[key].push(p);", "}", "", "for (const [key, items] of Object.entries(byFolder)) {", " const header = container.createEl(\"div\", { cls: \"ud-section\" });", " header.style.setProperty(\"--ud-color\", \"var(--ud-teal)\");", " header.createEl(\"span\", { cls: \"ud-section-dot\" });", " header.createEl(\"span\", { text: key, cls: \"ud-section-title\" });", " header.createEl(\"span\", { text: String(items.length), cls: \"ud-section-count\" });", " ", " const list = container.createEl(\"div\", { cls: \"ud-list\" });", " for (const p of items.slice(0, 20)) {", " const card = list.createEl(\"div\", { cls: \"ud-card\" });", " card.style.setProperty(\"--ud-border-color\", \"var(--ud-teal)\");", " card.addEventListener(\"dblclick\", () => app.workspace.openLinkText(p.file.path, \"\", false));", " ", " const main = card.createEl(\"div\", { cls: \"ud-card-main\" });", " const link = main.createEl(\"a\", { text: p.file.name, cls: \"ud-card-link\" });", " link.addEventListener(\"click\", (e) => {", " e.stopPropagation();", " app.workspace.openLinkText(p.file.path, \"\", false);", " });", " ", " const meta = main.createEl(\"div\", { cls: \"ud-card-meta\" });", " if (p.type) meta.createEl(\"span\", { text: p.type, cls: \"ud-card-tag\" });", " if (p.status && p.status !== \"Готово\") meta.createEl(\"span\", { text: p.status, cls: \"ud-card-tag\" });", " }", "}", "", "if (pages.length === 0) {", " container.createEl(\"div\", { text: \"Пока нет заметок\", cls: \"ud-empty\" });", "}", "` ``", "" ]; const content = lines.join("\n"); if (file) { await app.vault.modify(file, content); } else { file = await app.vault.create(path, content); } app.workspace.openLinkText(file.path, "", false); } for (const l of links) { const card = grid.createEl("div", { cls: "ud-quick-card " + l.cls }); if (l.isNote) { card.addEventListener("click", () => app.workspace.openLinkText(l.path, "", false)); } else { card.addEventListener("click", async () => await openFolderNote(l.folder, l.label)); } const icon = card.createEl("span", { text: l.icon, cls: "ud-icon" }); card.createEl("span", { text: l.label, cls: "ud-quick-label" }); }
```

---

## Создать заметку

```dataviewjs
const container = dv.container;
container.classList.add("university-dashboard");

const btnWrap = container.createEl("div");
btnWrap.style.cssText = "margin-bottom: 16px;";

const btn = btnWrap.createEl("button", { cls: "ud-btn" });
btn.innerHTML = '<span class="ud-icon" style="font-size: 1.2em; margin-right: 6px;">add_circle</span> Новая заметка';
btn.style.cssText = "padding: 10px 18px; border-radius: var(--ud-radius-md); border: 1px solid var(--background-modifier-border); background: var(--background-modifier-form-field); color: var(--text-normal); cursor: pointer; transition: var(--ud-transition); font-family: var(--ud-font-sans); font-weight: 600; font-size: var(--ud-text-base); display: flex; align-items: center;";

btn.addEventListener("mouseenter", () => {
    btn.style.background = "var(--background-modifier-hover)";
    btn.style.borderColor = "var(--text-muted)";
});
btn.addEventListener("mouseleave", () => {
    btn.style.background = "var(--background-modifier-form-field)";
    btn.style.borderColor = "var(--background-modifier-border)";
});

btn.addEventListener("click", async () => {
    const templateFile = app.vault.getAbstractFileByPath("50-Система/Шаблоны/Новая заметка.md");
    if (!templateFile) {
        new Notice("Шаблон не найден: 50-Система/Шаблоны/Новая заметка.md");
        return;
    }
    
    const newFile = await app.fileManager.createNewMarkdownFile(app.vault.getRoot(), "Untitled");
    if (!newFile) {
        new Notice("Не удалось создать заметку");
        return;
    }
    
    app.workspace.openLinkText(newFile.path, "", false);
    
    await new Promise(r => setTimeout(r, 500));
    
    app.commands.executeCommandById("templater-obsidian:replace-in-file");
    
    setTimeout(async () => {
        const note = dv.page(newFile.path);
        if (!note || !note.subject) return;
        
        const subject = note.subject;
        const noteName = note.file.name;
        const basePath = (subject === "IT") ? "20-Проекты/IT" : (subject === "Личное") ? "30-Личное" : "10-Университет/" + subject;
        const mocPath = basePath + "/MOC — " + subject + ".md";
        const mocFile = app.vault.getAbstractFileByPath(mocPath);
        
        if (mocFile) {
            let mocContent = await app.vault.read(mocFile);
            const linkLine = "- [[" + noteName + "]]";
            const marker = "## Связанные заметки";
            
            if (mocContent.includes(marker)) {
                const idx = mocContent.indexOf(marker);
                let insertPos = idx + marker.length;
                while (insertPos < mocContent.length && mocContent[insertPos] !== '\n') insertPos++;
                insertPos++;
                
                if (!mocContent.includes(linkLine)) {
                    mocContent = mocContent.slice(0, insertPos) + linkLine + "\n" + mocContent.slice(insertPos);
                    await app.vault.modify(mocFile, mocContent);
                }
            } else {
                mocContent = mocContent + "\n" + marker + "\n" + linkLine + "\n";
                await app.vault.modify(mocFile, mocContent);
            }
        }
    }, 8000);
});
```

---

```dataviewjs
const container = dv.container;
container.classList.add("university-dashboard");

const searchWrap = container.createEl("div");
searchWrap.style.cssText = "position: relative; margin-bottom: 16px; display: flex; gap: 8px; align-items: center;";

const inputWrap = searchWrap.createEl("div");
inputWrap.style.cssText = "position: relative; flex: 1;";

const searchIcon = inputWrap.createEl("span", { text: "search", cls: "ud-icon" });
searchIcon.style.cssText = "position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: var(--text-muted); font-size: 1.2em; pointer-events: none; z-index: 2;";

const input = inputWrap.createEl("div");
input.contentEditable = "true";
input.setAttribute("role", "textbox");
input.setAttribute("aria-label", "Поиск по заметкам");
input.style.cssText = `
    width: 100%;
    padding: 10px 12px 10px 40px;
    border-radius: var(--ud-radius-md);
    border: 1px solid var(--background-modifier-border);
    background: var(--background-modifier-form-field);
    color: var(--text-normal);
    font-family: var(--ud-font-sans);
    font-size: var(--ud-text-base);
    outline: none;
    transition: var(--ud-transition);
    min-height: 20px;
    line-height: 1.4;
    cursor: text;
`;
input.addEventListener("focus", () => {
    input.style.borderColor = "var(--text-accent)";
    input.style.boxShadow = "0 0 0 3px rgba(136,192,208,0.1)";
});
input.addEventListener("blur", () => {
    input.style.borderColor = "var(--background-modifier-border)";
    input.style.boxShadow = "none";
});

const btn = searchWrap.createEl("button");
btn.innerHTML = '<span class="ud-icon" style="font-size: 1.2em;">search</span>';
btn.style.cssText = `
    padding: 10px 14px;
    border-radius: var(--ud-radius-md);
    border: 1px solid var(--background-modifier-border);
    background: var(--background-modifier-form-field);
    color: var(--text-muted);
    cursor: pointer;
    transition: var(--ud-transition);
    display: flex;
    align-items: center;
    justify-content: center;
`;
btn.addEventListener("mouseenter", () => {
    btn.style.background = "var(--background-modifier-hover)";
    btn.style.color = "var(--text-normal)";
});
btn.addEventListener("mouseleave", () => {
    btn.style.background = "var(--background-modifier-form-field)";
    btn.style.color = "var(--text-muted)";
});

function doFilter() {
    const term = input.textContent.toLowerCase().trim();

    const urgentCards = document.querySelectorAll('.ud-list[data-section="urgent"] .ud-card');
    let urgentVisible = 0;
    urgentCards.forEach(card => {
        const text = card.textContent.toLowerCase();
        const show = !term || text.includes(term);
        card.style.display = show ? "" : "none";
        if (show) urgentVisible++;
    });

    const urgentCount = document.querySelector('[data-toggle="urgent"] .ud-done-count');
    if (urgentCount) urgentCount.textContent = String(urgentVisible);

    const subjectCards = document.querySelectorAll('.ud-list[data-section="subjects"] .ud-card');
    let subjectVisible = 0;
    subjectCards.forEach(card => {
        const text = card.textContent.toLowerCase();
        const show = !term || text.includes(term);
        card.style.display = show ? "" : "none";
        if (show) subjectVisible++;
    });

    const subjectCount = document.querySelector('[data-toggle="subjects"] .ud-done-count');
    if (subjectCount) subjectCount.textContent = String(subjectVisible);

    if (term) {
        const urgentList = document.querySelector('[data-section="urgent"].ud-done-list');
        const urgentToggle = document.querySelector('[data-toggle="urgent"]');
        if (urgentVisible > 0 && urgentList && !urgentList.classList.contains("open")) {
            urgentList.classList.add("open");
            urgentToggle.classList.add("open");
        }

        const subjectList = document.querySelector('[data-section="subjects"].ud-done-list');
        const subjectToggle = document.querySelector('[data-toggle="subjects"]');
        if (subjectVisible > 0 && subjectList && !subjectList.classList.contains("open")) {
            subjectList.classList.add("open");
            subjectToggle.classList.add("open");
        }
    } else {
        const urgentList = document.querySelector('[data-section="urgent"].ud-done-list');
        const urgentToggle = document.querySelector('[data-toggle="urgent"]');
        if (urgentList && urgentList.classList.contains("open")) {
            urgentList.classList.remove("open");
            urgentToggle.classList.remove("open");
        }

        const subjectList = document.querySelector('[data-section="subjects"].ud-done-list');
        const subjectToggle = document.querySelector('[data-toggle="subjects"]');
        if (subjectList && subjectList.classList.contains("open")) {
            subjectList.classList.remove("open");
            subjectToggle.classList.remove("open");
        }
    }
}

input.addEventListener("input", doFilter);
input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        e.preventDefault();
        doFilter();
        input.blur();
    }
});
btn.addEventListener("click", doFilter);

const placeholder = inputWrap.createEl("div");
placeholder.textContent = "Поиск по заметкам...";
placeholder.style.cssText = `
    position: absolute;
    left: 40px;
    top: 50%;
    transform: translateY(-50%);
    color: var(--text-muted);
    font-family: var(--ud-font-sans);
    font-size: var(--ud-text-base);
    pointer-events: none;
    opacity: 1;
    transition: opacity 0.2s;
`;
function updatePlaceholder() {
    placeholder.style.opacity = input.textContent.trim() ? "0" : "1";
}
input.addEventListener("input", updatePlaceholder);
input.addEventListener("focus", updatePlaceholder);
input.addEventListener("blur", updatePlaceholder);
```

---

```dataviewjs
const сегодня = DateTime.now().startOf("day");
const месяцы = ["янв","фев","мар","апр","мая","июн","июл","авг","сен","окт","ноя","дек"];

const urgent = dv.pages()
    .where(p => p.due_date && p.status !== "Готово")
    .map(p => {
        const д = DateTime.fromISO(p.due_date);
        const дней = Math.ceil(д.diff(сегодня, "days").days);
        return { ...p, _дней: дней, _дата: `${д.day} ${месяцы[д.month-1]}` };
    })
    .where(p => p._дней <= 2)
    .sort(p => p.due_date)
    .array();

const container = dv.container;
container.classList.add("university-dashboard");

const toggle = container.createEl("div", { cls: "ud-done-toggle" });
toggle.setAttribute("data-toggle", "urgent");
toggle.style.marginTop = "0";
toggle.style.cursor = "pointer";
const arrow = toggle.createEl("span", { text: "▶", cls: "ud-done-arrow" });
toggle.createEl("span", { text: "Требуют внимания", cls: "ud-done-label" });
const count = toggle.createEl("span", { text: String(urgent.length), cls: "ud-done-count" });

const content = container.createEl("div", { cls: "ud-done-list" });
content.setAttribute("data-section", "urgent");

toggle.addEventListener("click", () => {
    const открыто = content.classList.contains("open");
    content.classList.toggle("open");
    toggle.classList.toggle("open");
});

if (urgent.length === 0) {
    content.createEl("div", { text: "Нет срочных дел", cls: "ud-empty" });
} else {
    const list = content.createEl("div", { cls: "ud-list" });
    list.setAttribute("data-section", "urgent");
    for (const p of urgent.slice(0, 8)) {
        const дней = p._дней;
        let colorVar = дней < 0 ? "--ud-status-overdue" : дней === 0 ? "--ud-status-today" : "--ud-status-soon";

        const card = list.createEl("div", { cls: "ud-card" });
        card.style.setProperty("--ud-border-color", `var(${colorVar})`);
        card.addEventListener("dblclick", () => app.workspace.openLinkText(p.file.path, "", false));

        const main = card.createEl("div", { cls: "ud-card-main" });
        const link = main.createEl("a", { text: p.file.name, cls: "ud-card-link" });
        link.addEventListener("click", (e) => {
            e.stopPropagation();
            app.workspace.openLinkText(p.file.path, "", false);
        });

        const meta = main.createEl("div", { cls: "ud-card-meta" });
        if (p.subject) meta.createEl("span", { text: p.subject, cls: "ud-card-tag" });
        if (p.type) meta.createEl("span", { text: p.type, cls: "ud-card-tag" });

        const dateBlock = card.createEl("div", { cls: "ud-date-block" });
        dateBlock.createEl("div", { text: p._дата, cls: "ud-date-main" });
        const subText = дней < 0 ? `Просрочено на ${Math.abs(дней)} дн.` : дней === 0 ? "Сегодня" : `Через ${дней} дн.`;
        const subClass = дней < 0 ? "ud-urgent" : дней === 0 ? "ud-today" : "ud-soon";
        dateBlock.createEl("div", { text: subText, cls: `ud-date-sub ${subClass}` });
    }
}
```

---

```dataviewjs
const container = dv.container;
container.classList.add("university-dashboard");

const toggle = container.createEl("div", { cls: "ud-done-toggle" });
toggle.setAttribute("data-toggle", "subjects");
toggle.style.marginTop = "0";
toggle.style.cursor = "pointer";
const arrow = toggle.createEl("span", { text: "▶", cls: "ud-done-arrow" });
toggle.createEl("span", { text: "Предметы", cls: "ud-done-label" });
const count = toggle.createEl("span", { text: "0", cls: "ud-done-count" });

const content = container.createEl("div", { cls: "ud-done-list" });
content.setAttribute("data-section", "subjects");

toggle.addEventListener("click", () => {
    const открыто = content.classList.contains("open");
    content.classList.toggle("open");
    toggle.classList.toggle("open");
});

const subjects = ["ВВС","ОП","Физика","Информатика","Математика","Английский","Физра","ПИД","Биология","Русский","УНПАО","Литература","История","Обществознание","География"];
const subList = content.createEl("div", { cls: "ud-list" });
subList.setAttribute("data-section", "subjects");

let visibleCount = 0;
for (const sub of subjects) {
    const path = "10-Университет/" + sub;
    const active = dv.pages(`"${path}"`).where(p => p.status && p.status !== "Готово").length;
    const total = dv.pages(`"${path}"`).length;
    if (total === 0) continue;

    visibleCount++;

    const card = subList.createEl("div", { cls: "ud-card" });
    card.style.setProperty("--ud-border-color", "var(--ud-teal)");
    const mocPath = path + "/MOC — " + sub + ".md";
    card.addEventListener("dblclick", () => app.workspace.openLinkText(mocPath, "", false));

    const main = card.createEl("div", { cls: "ud-card-main" });
    const link = main.createEl("a", { text: sub, cls: "ud-card-link" });
    link.addEventListener("click", (e) => {
        e.stopPropagation();
        app.workspace.openLinkText(mocPath, "", false);
    });

    const meta = main.createEl("div", { cls: "ud-card-meta" });
    meta.createEl("span", { text: active > 0 ? `${active} в работе` : "Всё сдано", cls: "ud-card-tag" });
    meta.createEl("span", { text: `${total} заметок`, cls: "ud-card-tag" });
}

count.textContent = String(visibleCount);

if (visibleCount === 0) {
    subList.createEl("div", { text: "Ничего не найдено", cls: "ud-empty" });
}
```
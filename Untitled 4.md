<%*
function isValidDate(dateString) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(dateString)) return false;
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return false;
    const [y, m, d] = dateString.split('-').map(Number);
    return date.getFullYear() === y && (date.getMonth() + 1) === m && date.getDate() === d;
}

const предметы = ["ВВС","ОП","Физика","Информатика","Математика","Английский","Физра","ПИД","Биология","Русский","УНПАО","Литература","История","Обществознание","География","IT","Личное","Другое"];
const предмет = await tp.system.suggester(предметы, предметы, false, "Выбери предмет:");
if (!предмет) return;

const типы = ["Проект","ДЗ","Лекция","Конспект","Лаба","Экзамен","Источник","Разное"];
const тип = await tp.system.suggester(типы, типы, false, "Выбери тип:");
if (!тип) return;

const тема = await tp.system.prompt("Введи тему:", "");
if (!тема) return;

const типыСДедлайном = ["Проект", "ДЗ", "Лаба", "Экзамен"];
const нуженДедлайн = типыСДедлайном.includes(тип);

let дедлайн = "";
let статус = "";
let приоритет = "";

if (нуженДедлайн) {
    let promptText = "Дедлайн (ГГГГ-ММ-ДД):";
    while (true) {
        дедлайн = await tp.system.prompt(promptText, tp.date.now("YYYY-MM-DD"));
        if (!дедлайн) return;
        if (isValidDate(дедлайн)) break;
        promptText = "Неверная дата! Дедлайн (ГГГГ-ММ-ДД):";
    }

    const статусы = ["Идея","В работе","На проверке","Готово"];
    статус = await tp.system.suggester(статусы, статусы, false, "Выбери статус:");
    if (!статус) return;

    const приоритетыТекст = ["Высокий", "Средний", "Низкий"];
    const приоритетыЗнач = ["high", "medium", "low"];
    приоритет = await tp.system.suggester(приоритетыТекст, приоритетыЗнач, false, "Приоритет:");
    if (!приоритет) приоритет = "medium";
} else {
    статус = "Готово";
}

let базовыйПуть = (предмет === "IT") ? "20-Проекты/IT" : (предмет === "Личное") ? "30-Личное" : "10-Университет/" + предмет;

let папкаТипа = "";
if (тип === "Проект") папкаТипа = "Проекты/Проект " + тема;
else if (тип === "ДЗ") папкаТипа = "ДЗ";
else if (тип === "Лекция") папкаТипа = "Лекции";
else if (тип === "Конспект") папкаТипа = "Конспекты";
else if (тип === "Лаба") папкаТипа = "Лабораторные";
else if (тип === "Экзамен") папкаТипа = "Экзамены";
else if (тип === "Источник") папкаТипа = "Источники";
else папкаТипа = "Разное";

const итоговыйПуть = базовыйПуть + "/" + папкаТипа;

try { await app.vault.createFolder(базовыйПуть); } catch(e) {}
try { await app.vault.createFolder(итоговыйПуть); } catch(e) {}

// --- АВТО-MOC ---
const mocPath = базовыйПуть + "/MOC — " + предмет + ".md";
const mocExists = app.vault.getAbstractFileByPath(mocPath);

if (!mocExists) {
    const mocLines = [
        "---",
        "cssclasses:",
        "  - university-dashboard",
        "---",
        "",
        "> Map of Content для предмета «" + предмет + "»",
        "",
        "```dataviewjs",
        'const pages = dv.pages("\\"' + базовыйПуть + '\\"")',
        '    .where(p => p.file.name != dv.current().file.name)',
        '    .sort(p => p.file.name)',
        '    .array();',
        '',
        'const container = dv.container;',
        'container.classList.add("university-dashboard");',
        '',
        'const typeColors = {',
        '    "ДЗ": "--ud-blue",',
        '    "Лекция": "--ud-green",',
        '    "Конспект": "--ud-teal",',
        '    "Проект": "--ud-orange",',
        '    "Лаба": "--ud-purple",',
        '    "Экзамен": "--ud-red",',
        '    "Источник": "--ud-frost",',
        '    "Разное": "--ud-frost"',
        '};',
        '',
        'const byType = {};',
        'for (const p of pages) {',
        '    const t = p.type || "Разное";',
        '    if (!byType[t]) byType[t] = [];',
        '    byType[t].push(p);',
        '}',
        '',
        'for (const [type, items] of Object.entries(byType)) {',
        '    const colorVar = typeColors[type] || "--ud-frost";',
        '    ',
        '    const section = container.createEl("div", { cls: "ud-moc-section" });',
        '    const header = section.createEl("div", { cls: "ud-moc-header ud-section" });',
        '    header.style.setProperty("--ud-color", "var(" + colorVar + ")");',
        '    header.createEl("span", { cls: "ud-section-dot" });',
        '    const title = header.createEl("span", { text: type, cls: "ud-section-title" });',
        '    title.style.textTransform = "uppercase";',
        '    header.createEl("span", { text: String(items.length), cls: "ud-section-count" });',
        '    ',
        '    const list = section.createEl("div", { cls: "ud-moc-list ud-list" });',
        '    ',
        '    for (const p of items) {',
        '        const card = list.createEl("div", { cls: "ud-card" });',
        '        card.style.setProperty("--ud-border-color", "var(" + colorVar + ")");',
        '        ',
        '        card.addEventListener("dblclick", () => app.workspace.openLinkText(p.file.path, "", false));',
        '        ',
        '        const link = card.createEl("a", { text: p.file.name, cls: "ud-card-link" });',
        '        link.addEventListener("click", (e) => {',
        '            e.stopPropagation();',
        '            app.workspace.openLinkText(p.file.path, "", false);',
        '        });',
        '        ',
        '        const meta = card.createEl("div", { cls: "ud-card-meta" });',
        '        ',
        '        if (p.status && p.status !== "Готово") {',
        '            meta.createEl("span", { text: p.status, cls: "ud-card-tag" });',
        '        }',
        '        if (p.due_date) {',
        '            meta.createEl("span", { text: p.due_date, cls: "ud-card-tag" });',
        '        }',
        '    }',
        '}',
        '',
        'if (pages.length === 0) {',
        '    container.createEl("div", { text: "Пока нет заметок", cls: "ud-empty" });',
        '}',
        "```",
        ""
    ];

    await app.vault.create(mocPath, mocLines.join("
"));
}

const имяФайла = tp.date.now("YYYY-MM-DD") + " — " + тема;

let предыдущаяСсылка = "";
if (["Лекция", "Конспект"].includes(тип)) {
    const всеФайлы = app.vault.getMarkdownFiles();
    const файлыПредмета = всеФайлы
        .filter(f => f.path.startsWith(базовыйПуть + "/") 
            && !f.name.startsWith("_") 
            && !f.name.startsWith("MOC")
            && !f.name.startsWith("Index"))
        .sort((a, b) => b.name.localeCompare(a.name));

    if (файлыПредмета.length > 0) {
        предыдущаяСсылка = "[[" + файлыПредмета[0].basename + "]]";
    }
}

let теги = [];
if (предмет === "IT") {
    теги = ["проекты/it/" + тип.toLowerCase(), "проекты/it", тип.toLowerCase()];
} else if (предмет === "Личное") {
    теги = ["личное/" + тип.toLowerCase(), "личное", тип.toLowerCase()];
} else {
    теги = ["университет/" + предмет.toLowerCase() + "/" + тип.toLowerCase(), "университет/" + предмет.toLowerCase(), "университет", предмет.toLowerCase(), тип.toLowerCase()];
}

const tagsYaml = теги.map(t => "  - " + t).join("
");

await tp.file.move(итоговыйПуть + "/" + имяФайла);

// --- АВТО-ОБНОВЛЕНИЕ СВЯЗЕЙ MOC ---
// Используем Obsidian API напрямую, не генерируем DataviewJS-строки
const mocFile = app.vault.getAbstractFileByPath(mocPath);
if (mocFile) {
    let mocContent = await app.vault.read(mocFile);
    const linkLine = "- [[" + имяФайла + "]]";
    const marker = "## Связанные заметки";

    if (mocContent.includes(marker)) {
        const idx = mocContent.indexOf(marker);
        const afterMarker = idx + marker.length;
        let insertPos = afterMarker;
        while (insertPos < mocContent.length && mocContent[insertPos] !== '\n') {
            insertPos++;
        }
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

const dueLine = нуженДедлайн ? 'due_date: "' + дедлайн + '"\n' : "";
const priorityLine = приоритет ? 'priority: "' + приоритет + '"\n' : "";

const notesPrefix = [];
if (предыдущаяСсылка) notesPrefix.push("**Предыдущий материал:** " + предыдущаяСсылка);
const notesText = notesPrefix.join("\n\n");

const relatedList = [];
if (предыдущаяСсылка) relatedList.push("- " + предыдущаяСсылка);
const relatedText = relatedList.join("\n");
-%>
---
title: "<% тема %>"
type: "<% тип %>"
subject: "<% предмет %>"
project: "<% тип === 'Проект' ? 'Проект ' + тема : '' %>"
tags:
<% tagsYaml %>
AutoNoteMover: disable
created: <% tp.date.now("YYYY-MM-DD") %>
<% dueLine %><% priorityLine %>status: "<% статус %>"
cssclasses:
  - university-dashboard
---

# <% тема %>

## Заметки
<% notesText %>

## Связанные заметки
<% relatedText %>

## Итоги
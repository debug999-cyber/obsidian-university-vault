---
cssclasses:
  - university-dashboard
---
Обновить связи MOC

```dataviewjs
const container = dv.container;
container.classList.add("university-dashboard");

const mocFiles = app.vault.getMarkdownFiles().filter(f => f.name.startsWith("MOC —"));
const totalNotes = dv.pages().where(p => !p.file.name.startsWith("MOC") && !p.file.name.startsWith("_Index")).length;
const totalLinks = mocFiles.reduce((sum, moc) => {
    const content = app.vault.cachedRead(moc);
    const matches = (typeof content === "string") ? content.match(/- \[\[/g) : null;
    return sum + (matches ? matches.length : 0);
}, 0);

const statsWrap = container.createEl("div", { cls: "ud-quick-grid" });
statsWrap.style.cssText = "grid-template-columns: repeat(3, 1fr); margin-bottom: 24px;";

const stats = [
    { icon: "folder_special", label: "MOC файлов", value: String(mocFiles.length), cls: "ud-quick-uni" },
    { icon: "description", label: "Заметок всего", value: String(totalNotes), cls: "ud-quick-projects" },
    { icon: "link", label: "Связей", value: String(totalLinks), cls: "ud-quick-deadlines" }
];

for (const s of stats) {
    const card = statsWrap.createEl("div", { cls: "ud-quick-card " + s.cls });
    card.style.cursor = "default";
    card.createEl("span", { text: s.icon, cls: "ud-icon" });
    const val = card.createEl("div", { text: s.value, cls: "ud-quick-label" });
    val.style.cssText = "font-size: 1.8em; font-weight: 700; margin: 4px 0;";
    card.createEl("div", { text: s.label, cls: "ud-quick-label" });
}

const btnWrap = container.createEl("div");
btnWrap.style.cssText = "margin: 24px 0; text-align: center;";

const btn = btnWrap.createEl("button", { cls: "ud-btn" });
btn.innerHTML = '<span class="ud-icon" style="font-size: 1.3em; margin-right: 8px;">sync</span> Обновить все связи MOC';
btn.style.cssText = "padding: 12px 28px; border-radius: var(--ud-radius-lg); border: 1px solid var(--background-modifier-border); background: var(--background-modifier-form-field); color: var(--text-normal); cursor: pointer; transition: var(--ud-transition); font-family: var(--ud-font-sans); font-weight: 600; font-size: var(--ud-text-base); display: inline-flex; align-items: center; backdrop-filter: blur(8px);";

btn.addEventListener("mouseenter", () => {
    btn.style.background = "var(--background-modifier-hover)";
    btn.style.borderColor = "var(--text-muted)";
    btn.style.transform = "translateY(-2px)";
    btn.style.boxShadow = "var(--ud-shadow-md)";
});
btn.addEventListener("mouseleave", () => {
    btn.style.background = "var(--background-modifier-form-field)";
    btn.style.borderColor = "var(--background-modifier-border)";
    btn.style.transform = "translateY(0)";
    btn.style.boxShadow = "none";
});

const progressWrap = container.createEl("div");
progressWrap.style.cssText = "display: none; margin: 16px 0;";

const progressBar = progressWrap.createEl("div");
progressBar.style.cssText = "width: 100%; height: 6px; background: var(--background-modifier-border); border-radius: 3px; overflow: hidden;";

const progressFill = progressBar.createEl("div");
progressFill.style.cssText = "width: 0%; height: 100%; background: var(--ud-teal); border-radius: 3px; transition: width 0.3s ease;";

const progressText = progressWrap.createEl("div", { text: "0 / 0" });
progressText.style.cssText = "text-align: center; margin-top: 8px; font-size: var(--ud-text-sm); color: var(--text-muted);";

const section = container.createEl("div", { cls: "ud-section" });
section.style.setProperty("--ud-color", "var(--ud-teal)");
section.createEl("span", { cls: "ud-section-dot" });
section.createEl("span", { text: "MOC файлы", cls: "ud-section-title" });
section.createEl("span", { text: String(mocFiles.length), cls: "ud-section-count" });

const list = container.createEl("div", { cls: "ud-list" });

for (const moc of mocFiles.sort((a, b) => a.name.localeCompare(b.name))) {
    const folder = moc.parent.path;
    const pages = dv.pages('"' + folder + '"')
        .where(p => p.file.name !== moc.basename
            && !p.file.name.startsWith("_Index_of_")
            && !p.file.name.startsWith("Университет")
            && !p.file.name.startsWith("Проекты")
            && !p.file.name.startsWith("Личное"))
        .sort(p => p.file.name);

    const linkCount = pages.length;
    const lastModified = new Date(moc.stat.mtime).toLocaleDateString("ru-RU", { day: "numeric", month: "short" });

    const card = list.createEl("div", { cls: "ud-card" });
    card.style.setProperty("--ud-border-color", linkCount > 0 ? "var(--ud-teal)" : "var(--text-muted)");
    card.style.cursor = "default";

    const main = card.createEl("div", { cls: "ud-card-main" });
    const link = main.createEl("a", { text: moc.basename.replace("MOC — ", ""), cls: "ud-card-link" });
    link.addEventListener("click", (e) => {
        e.stopPropagation();
        app.workspace.openLinkText(moc.path, "", false);
    });

    const meta = main.createEl("div", { cls: "ud-card-meta" });
    meta.createEl("span", { text: folder, cls: "ud-card-tag" });
    meta.createEl("span", { text: linkCount + " связей", cls: "ud-card-tag" });

    const dateBlock = card.createEl("div", { cls: "ud-date-block" });
    dateBlock.createEl("div", { text: lastModified, cls: "ud-date-main" });
    dateBlock.createEl("div", { text: linkCount > 0 ? "Актуально" : "Нет связей", cls: "ud-date-sub " + (linkCount > 0 ? "ud-ok" : "ud-urgent") });
}

btn.addEventListener("click", async () => {
    btn.disabled = true;
    btn.innerHTML = '<span class="ud-icon" style="font-size: 1.3em; margin-right: 8px;">sync</span> Обновляю...';
    btn.style.opacity = "0.7";
    btn.style.cursor = "not-allowed";

    progressWrap.style.display = "block";
    progressText.textContent = "0 / " + mocFiles.length;

    for (let i = 0; i < mocFiles.length; i++) {
        const moc = mocFiles[i];
        const folder = moc.parent.path;
        const pages = dv.pages('"' + folder + '"')
            .where(p => p.file.name !== moc.basename
                && !p.file.name.startsWith("_Index_of_")
                && !p.file.name.startsWith("Университет")
                && !p.file.name.startsWith("Проекты")
                && !p.file.name.startsWith("Личное"))
            .sort(p => p.file.name);

        const links = pages.map(p => "- [[" + p.file.name + "]]").array().join("\n");

        let content = await app.vault.read(moc);

        const marker = "\n\n## Связанные заметки\n";
        const idx = content.indexOf(marker);
        if (idx !== -1) {
            content = content.substring(0, idx);
        }

        content = content + marker + links + "\n";

        await app.vault.modify(moc, content);

        const pct = ((i + 1) / mocFiles.length) * 100;
        progressFill.style.width = pct + "%";
        progressText.textContent = (i + 1) + " / " + mocFiles.length;
    }

    btn.innerHTML = '<span class="ud-icon" style="font-size: 1.3em; margin-right: 8px;">check_circle</span> Готово!';
    btn.style.opacity = "1";
    btn.style.background = "rgba(48, 209, 88, 0.15)";
    btn.style.borderColor = "var(--ud-status-ok)";
    btn.style.color = "var(--ud-status-ok)";

    setTimeout(() => {
        btn.disabled = false;
        btn.innerHTML = '<span class="ud-icon" style="font-size: 1.3em; margin-right: 8px;">sync</span> Обновить все связи MOC';
        btn.style.background = "var(--background-modifier-form-field)";
        btn.style.borderColor = "var(--background-modifier-border)";
        btn.style.color = "var(--text-normal)";
        btn.style.cursor = "pointer";
        progressWrap.style.display = "none";
        progressFill.style.width = "0%";
    }, 3000);

    app.commands.executeCommandById("dataview:dataview-force-refresh-views");
});
```


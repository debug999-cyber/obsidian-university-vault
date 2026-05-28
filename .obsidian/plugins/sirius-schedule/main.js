const { Plugin, Notice, moment, Setting, PluginSettingTab, Modal, MarkdownView } = require('obsidian');

const DEFAULT_SETTINGS = {
    jsonPath: 'sirius-schedule.json',
    groupName: '',
    autoUpdateOnStart: true,
    showNotifications: true,
    cachePath: 'sirius-schedule-cache.json'
};

// ═══════════════════════════════════════════════════════════════
// ГЛАВНЫЙ ПЛАГИН
// ═══════════════════════════════════════════════════════════════

class SiriusSchedulePlugin extends Plugin {
    async onload() {
        await this.loadSettings();
        this.cache = new Map();

        await this.loadFromJson();

        this.registerCommands();
        this.registerRibbon();
        this.registerSettings();

        // Ждём загрузки workspace, потом патчим calendar
        this.app.workspace.onLayoutReady(() => {
            this.patchCalendar();
        });

        // Если calendar загрузится позже — перепатчим
        this.registerEvent(
            this.app.workspace.on('layout-change', () => {
                this.patchCalendar();
            })
        );
    }

    onunload() {
        // Убираем патч при выгрузке плагина
        this.unpatchCalendar();
    }

    // ─── Настройки ───────────────────────────────────────────

    async loadSettings() {
        this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
    }

    async saveSettings() {
        await this.saveData(this.settings);
    }

    // ─── Команды ─────────────────────────────────────────────

    registerCommands() {
        this.addCommand({
            id: 'sirius-reload',
            name: 'Перечитать JSON расписания',
            callback: () => this.loadFromJson(true)
        });

        this.addCommand({
            id: 'sirius-today',
            name: 'Расписание на сегодня',
            callback: () => this.showForDate(moment().format('DD.MM.YYYY'), 'Сегодня')
        });

        this.addCommand({
            id: 'sirius-tomorrow',
            name: 'Расписание на завтра',
            callback: () => this.showForDate(moment().add(1, 'day').format('DD.MM.YYYY'), 'Завтра')
        });

        this.addCommand({
            id: 'sirius-week',
            name: 'Расписание на неделю',
            callback: () => this.showWeek()
        });
    }

    registerRibbon() {
        this.addRibbonIcon('calendar-clock', 'Sirius: расписание на сегодня', () => {
            this.showForDate(moment().format('DD.MM.YYYY'), 'Сегодня');
        });
    }

    registerSettings() {
        this.addSettingTab(new SiriusSettingTab(this.app, this));
    }

    // ─── Загрузка JSON ───────────────────────────────────────

    async loadFromJson(showNotice = false) {
        try {
            const file = this.app.vault.getAbstractFileByPath(this.settings.jsonPath);
            if (!file) {
                if (showNotice) new Notice('JSON не найден. Запусти python sirius-update.py', 5000);
                return false;
            }

            const content = await this.app.vault.read(file);
            const data = JSON.parse(content);

            this.cache.clear();
            for (const [date, lessons] of Object.entries(data.by_date || {})) {
                this.cache.set(date, lessons);
            }

            this.settings.groupName = data.group || '';
            await this.saveSettings();

            if (showNotice) {
                new Notice(`✅ Расписание: ${data.total_lessons} пар загружено`, 4000);
            }

            // Перерисовать calendar после загрузки
            this.refreshCalendarView();
            return true;

        } catch (e) {
            if (showNotice) new Notice('❌ Ошибка: ' + e.message, 3000);
            return false;
        }
    }

    // ─── Интеграция с Calendar ───────────────────────────────
    // Плагин calendar не имеет публичного API для кастомных событий.
    // Единственный надёжный способ — monkey-patch рендера дней
    // и обработчика кликов.

    patchCalendar() {
        if (this._calendarPatched) return;

        const calendarLeaves = this.app.workspace.getLeavesOfType('calendar');
        if (!calendarLeaves.length) return;

        const calendarView = calendarLeaves[0].view;
        if (!calendarView) return;

        // Наблюдаем за DOM календаря через MutationObserver
        this._observer = new MutationObserver(() => {
            this.decorateCalendarDays();
        });

        const calendarEl = calendarView.containerEl;
        this._calendarContainerEl = calendarEl;

        this._observer.observe(calendarEl, {
            childList: true,
            subtree: true
        });

        // Первичная декорация
        this.decorateCalendarDays();

        // Перехватываем клики по дням
        this._clickHandler = (e) => {
            const dayEl = e.target.closest('.day');
            if (!dayEl) return;

            // Извлекаем дату из data-атрибутов или aria-label
            const dateStr = this.extractDateFromDayEl(dayEl);
            if (!dateStr) return;

            const lessons = this.cache.get(dateStr);
            if (lessons && lessons.length > 0) {
                e.preventDefault();
                e.stopPropagation();
                this.showForDate(dateStr, this.formatDateLabel(dateStr));
            }
        };

        calendarEl.addEventListener('click', this._clickHandler, true);
        this._calendarPatched = true;
    }

    unpatchCalendar() {
        if (this._observer) {
            this._observer.disconnect();
            this._observer = null;
        }
        if (this._clickHandler && this._calendarContainerEl) {
            this._calendarContainerEl.removeEventListener('click', this._clickHandler, true);
            this._clickHandler = null;
        }
        // Убираем все наши точки
        document.querySelectorAll('.sirius-dot, .sirius-count').forEach(el => el.remove());
        this._calendarPatched = false;
    }

    decorateCalendarDays() {
        if (!this._calendarContainerEl) return;

        // Убираем старые точки перед перерисовкой
        this._calendarContainerEl.querySelectorAll('.sirius-dot, .sirius-count').forEach(el => el.remove());

        const dayEls = this._calendarContainerEl.querySelectorAll('.day');

        dayEls.forEach(dayEl => {
            const dateStr = this.extractDateFromDayEl(dayEl);
            if (!dateStr) return;

            const lessons = this.cache.get(dateStr);
            if (!lessons || !lessons.length) return;

            // Определяем цвет точки
            let color = '#5e81ac'; // обычный — синий
            if (lessons.some(l => l.type?.includes('Экзамен'))) {
                color = '#bf616a'; // экзамен — красный
            } else if (lessons.some(l => l.type?.includes('Практич'))) {
                color = '#d08770'; // практика — оранжевый
            }

            // Добавляем точку
            const dot = document.createElement('div');
            dot.className = 'sirius-dot';
            dot.style.cssText = `
                width: 6px;
                height: 6px;
                border-radius: 50%;
                background: ${color};
                position: absolute;
                bottom: 2px;
                left: 50%;
                transform: translateX(-50%);
                box-shadow: 0 0 4px ${color}80;
                pointer-events: none;
                z-index: 10;
            `;
            dot.title = lessons.map(l => `${l.start} ${l.subject}`).join('\n');

            // Убеждаемся что .day имеет position:relative
            if (getComputedStyle(dayEl).position === 'static') {
                dayEl.style.position = 'relative';
            }

            dayEl.appendChild(dot);

            // Добавляем счётчик пар (маленькая цифра)
            const count = document.createElement('div');
            count.className = 'sirius-count';
            count.textContent = lessons.length;
            count.style.cssText = `
                position: absolute;
                top: 1px;
                right: 2px;
                font-size: 9px;
                color: ${color};
                font-weight: 700;
                pointer-events: none;
                z-index: 10;
                line-height: 1;
            `;
            dayEl.appendChild(count);
        });
    }

    extractDateFromDayEl(dayEl) {
        // Способ 1: dataset
        if (dayEl.dataset.date) {
            return this.toRuDate(dayEl.dataset.date);
        }

        // Способ 2: aria-label (формат "May 25, 2026" или "2026-05-25")
        const ariaLabel = dayEl.getAttribute('aria-label');

        // Способ 3: вычислить из позиции в сетке + заголовка месяца
        // Calendar plugin рендерит дни как <td class="day"> с текстом = число дня.
        // Месяц/год берём из заголовка.
        const dayNum = dayEl.textContent?.trim();
        if (!dayNum || isNaN(parseInt(dayNum))) return null;

        const calendarEl = this._calendarContainerEl;
        if (!calendarEl) return null;

        // Ищем заголовок с месяцем/годом
        const titleEl = calendarEl.querySelector('.title, h3, [class*="title"], [class*="month"]');
        if (!titleEl) return null;

        const titleText = titleEl.textContent?.trim();
        if (!titleText) return null;

        // Парсим заголовок — может быть "May 2026", "Май 2026", "2026-05" и т.д.
        const parsed = this.parseMonthTitle(titleText);
        if (!parsed) return null;

        const day = dayNum.padStart(2, '0');
        const month = String(parsed.month).padStart(2, '0');
        return `${day}.${month}.${parsed.year}`;
    }

    parseMonthTitle(title) {
        // Англ: "May 2026", "January 2026"
        const enMonths = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        };

        // Рус: "Май 2026", "Январь 2026"
        const ruMonths = {
            'январь': 1, 'февраль': 2, 'март': 3, 'апрель': 4,
            'май': 5, 'июнь': 6, 'июль': 7, 'август': 8,
            'сентябрь': 9, 'октябрь': 10, 'ноябрь': 11, 'декабрь': 12
        };

        const lower = title.toLowerCase().trim();

        for (const [name, num] of Object.entries({...enMonths, ...ruMonths})) {
            if (lower.includes(name)) {
                const yearMatch = lower.match(/(\d{4})/);
                if (yearMatch) {
                    return { month: num, year: parseInt(yearMatch[1]) };
                }
            }
        }

        // Формат "2026-05"
        const isoMatch = lower.match(/(\d{4})-(\d{2})/);
        if (isoMatch) {
            return { month: parseInt(isoMatch[2]), year: parseInt(isoMatch[1]) };
        }

        return null;
    }

    toRuDate(isoDate) {
        // "2026-05-25" → "25.05.2026"
        const m = moment(isoDate);
        return m.isValid() ? m.format('DD.MM.YYYY') : null;
    }

    formatDateLabel(dateStr) {
        const m = moment(dateStr, 'DD.MM.YYYY');
        if (!m.isValid()) return dateStr;

        const days = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'];
        const months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
                        'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'];

        return `${days[m.day()]}, ${m.date()} ${months[m.month()]}`;
    }

    refreshCalendarView() {
        // Пересоздаём патч после обновления данных
        this.unpatchCalendar();
        setTimeout(() => this.patchCalendar(), 300);
    }

    // ─── Модалка расписания ──────────────────────────────────

    showForDate(dateStr, label) {
        const lessons = this.cache.get(dateStr) || [];
        if (!lessons.length) {
            new Notice(`${label}: пар нет 🎉`, 3000);
            return;
        }
        new ScheduleModal(this.app, `${label} — ${dateStr}`, lessons).open();
    }

    showWeek() {
        const today = moment();
        const startOfWeek = today.clone().startOf('isoWeek'); // Понедельник

        let allLessons = [];
        for (let i = 0; i < 7; i++) {
            const day = startOfWeek.clone().add(i, 'days');
            const dateStr = day.format('DD.MM.YYYY');
            const lessons = this.cache.get(dateStr) || [];
            if (lessons.length) {
                allLessons.push({ dateStr, day: day.clone(), lessons });
            }
        }

        if (!allLessons.length) {
            new Notice('На этой неделе пар нет 🎉', 3000);
            return;
        }

        new WeekModal(this.app, allLessons, this).open();
    }
}

// ═══════════════════════════════════════════════════════════════
// МОДАЛКА: расписание на день
// ═══════════════════════════════════════════════════════════════

class ScheduleModal extends Modal {
    constructor(app, title, lessons) {
        super(app);
        this.title = title;
        this.lessons = lessons;
    }

    onOpen() {
        const { contentEl } = this;
        contentEl.empty();
        contentEl.addClass('sirius-modal');

        contentEl.createEl('h2', { text: this.title });

        const info = contentEl.createEl('div', {
            text: `📚 ${this.lessons.length} ${this.pluralPairs(this.lessons.length)}`,
            cls: 'sirius-modal-info'
        });
        info.style.cssText = 'color:var(--text-muted);margin-bottom:12px;font-size:0.9em;';

        const container = contentEl.createEl('div');
        container.style.cssText = 'display:flex;flex-direction:column;gap:8px;';

        for (const l of this.lessons) {
            const row = container.createEl('div');
            row.style.cssText = 'padding:12px 16px;border-radius:10px;background:var(--background-modifier-form-field);border-left:3px solid ' + this.getTypeColor(l.type) + ';';

            const header = row.createEl('div');
            header.style.cssText = 'display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;';

            const time = header.createEl('span');
            time.style.cssText = 'font-weight:700;color:var(--text-accent);font-size:1.05em;';
            time.textContent = `${l.start} – ${l.end}`;

            const typeBadge = header.createEl('span');
            typeBadge.style.cssText = 'font-size:0.78em;padding:2px 10px;border-radius:12px;background:var(--background-modifier-hover);color:var(--text-muted);';
            typeBadge.textContent = l.type || '';

            const subject = row.createEl('div');
            subject.style.cssText = 'font-weight:600;font-size:1.05em;margin:2px 0 6px;';
            subject.textContent = l.subject;

            if (l.room || l.teacher) {
                const meta = row.createEl('div');
                meta.style.cssText = 'display:flex;gap:16px;font-size:0.85em;color:var(--text-muted);flex-wrap:wrap;';
                if (l.room) meta.createEl('span', { text: '🏫 ' + l.room });
                if (l.teacher) meta.createEl('span', { text: '👤 ' + l.teacher });
            }
        }
    }

    getTypeColor(type) {
        if (!type) return '#5e81ac';
        if (type.includes('Лекц')) return '#a3be8c';
        if (type.includes('Семинар')) return '#5e81ac';
        if (type.includes('Практич')) return '#d08770';
        if (type.includes('Экзамен')) return '#bf616a';
        if (type.includes('Внеуч')) return '#b48ead';
        return '#5e81ac';
    }

    pluralPairs(n) {
        const mod10 = n % 10;
        const mod100 = n % 100;
        if (mod100 >= 11 && mod100 <= 14) return 'пар';
        if (mod10 === 1) return 'пара';
        if (mod10 >= 2 && mod10 <= 4) return 'пары';
        return 'пар';
    }

    onClose() { this.contentEl.empty(); }
}

// ═══════════════════════════════════════════════════════════════
// МОДАЛКА: расписание на неделю
// ═══════════════════════════════════════════════════════════════

class WeekModal extends Modal {
    constructor(app, weekData, plugin) {
        super(app);
        this.weekData = weekData;
        this.plugin = plugin;
    }

    onOpen() {
        const { contentEl } = this;
        contentEl.empty();
        contentEl.addClass('sirius-modal');

        const today = moment();
        const weekStart = today.clone().startOf('isoWeek');
        const weekEnd = weekStart.clone().add(6, 'days');

        contentEl.createEl('h2', {
            text: `Неделя: ${weekStart.format('DD.MM')} – ${weekEnd.format('DD.MM.YYYY')}`
        });

        const days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

        for (const { dateStr, day, lessons } of this.weekData) {
            const dayName = days[day.isoWeekday() - 1];
            const isToday = day.isSame(today, 'day');

            const section = contentEl.createEl('div');
            section.style.cssText = 'margin-top:16px;';

            const header = section.createEl('div');
            header.style.cssText = 'display:flex;align-items:center;gap:8px;margin-bottom:8px;padding-bottom:4px;border-bottom:1px solid var(--background-modifier-border);';

            const dayLabel = header.createEl('span', {
                text: `${dayName}, ${dateStr}`
            });
            dayLabel.style.cssText = 'font-weight:700;font-size:1.05em;' + (isToday ? 'color:var(--text-accent);' : '');

            if (isToday) {
                const badge = header.createEl('span', { text: 'сегодня' });
                badge.style.cssText = 'font-size:0.75em;padding:1px 8px;border-radius:8px;background:var(--text-accent);color:var(--background-primary);';
            }

            header.createEl('span', {
                text: `${lessons.length} пар`,
                cls: 'sirius-day-count'
            }).style.cssText = 'font-size:0.85em;color:var(--text-muted);margin-left:auto;';

            for (const l of lessons) {
                const row = section.createEl('div');
                row.style.cssText = 'padding:8px 12px;margin:4px 0;border-radius:8px;background:var(--background-modifier-form-field);display:flex;gap:12px;align-items:center;';

                const time = row.createEl('span');
                time.style.cssText = 'font-weight:600;color:var(--text-accent);min-width:100px;';
                time.textContent = `${l.start}–${l.end}`;

                row.createEl('span', { text: l.subject }).style.fontWeight = '500';
            }
        }
    }

    onClose() { this.contentEl.empty(); }
}

// ═══════════════════════════════════════════════════════════════
// НАСТРОЙКИ
// ═══════════════════════════════════════════════════════════════

class SiriusSettingTab extends PluginSettingTab {
    constructor(app, plugin) {
        super(app, plugin);
        this.plugin = plugin;
    }

    display() {
        const { containerEl } = this;
        containerEl.empty();
        containerEl.createEl('h2', { text: 'Sirius Schedule' });

        new Setting(containerEl)
            .setName('Путь к JSON файлу расписания')
            .setDesc('Относительный путь внутри хранилища')
            .addText(text => text
                .setPlaceholder('sirius-schedule.json')
                .setValue(this.plugin.settings.jsonPath)
                .onChange(async (v) => {
                    this.plugin.settings.jsonPath = v;
                    await this.plugin.saveSettings();
                }));

        new Setting(containerEl)
            .setName('Перечитать расписание')
            .setDesc('Загрузить данные из JSON')
            .addButton(btn => btn
                .setButtonText('🔄 Обновить')
                .setCta()
                .onClick(() => this.plugin.loadFromJson(true)));

        // Статус
        const status = containerEl.createEl('div');
        status.style.cssText = 'margin-top:16px;padding:14px;border-radius:10px;background:var(--background-modifier-form-field);';

        const file = this.plugin.app.vault.getAbstractFileByPath(this.plugin.settings.jsonPath);
        const cacheSize = this.plugin.cache.size;

        if (file) {
            status.innerHTML = [
                '✅ <strong>JSON найден</strong>',
                `📋 Группа: <strong>${this.plugin.settings.groupName || '—'}</strong>`,
                `📅 Дней в расписании: <strong>${cacheSize}</strong>`,
                '',
                '<em style="font-size:0.85em;color:var(--text-muted)">Для обновления расписания запусти: python sirius-update.py</em>'
            ].join('<br>');
            status.style.color = 'var(--text-normal)';
        } else {
            status.innerHTML = '❌ JSON не найден<br><br>Запусти <code>python sirius-update.py</code> в папке хранилища';
            status.style.color = 'var(--text-error)';
        }
    }
}

module.exports = SiriusSchedulePlugin;

# Студпортал Vault

**Project name:** `Студпортал Vault`  
**Current version:** `v1.1.2`  
**Previous name:** `Obsidian University Vault`

Production-ready Obsidian vault for study management, dashboards, structured notes, and maintainable customization.

Built for people who want an academic vault that is not just a folder of notes, but a working system with:
- a polished home dashboard;
- deadline tracking;
- subject MOC pages;
- note templates;
- unified styling;
- plugin-based automation;
- clear documentation for future editing.

---

## Why this project exists

Most Obsidian study vaults become hard to maintain after the first customization wave.
This vault is organized so that a new person can quickly understand:
- what the system does;
- where the UI lives;
- where note logic lives;
- where plugin settings live;
- what is safe to edit;
- what should stay untouched.

---

## What you get

### Interface
- `Home.md` as the central workspace
- deadline dashboard
- overview pages for university / projects / personal notes
- subject-level MOC pages
- unified visual language across dashboards, notes, and documents

### Content system
- structured note creation via template
- frontmatter-driven dashboards
- subject folders and type folders
- consistent note layout
- archive for legacy and intermediate files

### Automation
- Dataview-powered dashboards
- Templater-based note generation
- MOC integration
- Sirius schedule integration
- plugin configuration already included in the vault

### Documentation
- onboarding for first-time users
- vault structure explanation
- change map for quick edits
- troubleshooting docs
- changelog

---

## First-time opening flow

If you are opening the project for the first time, follow this order:

1. `docs/01-START-HERE.md`
2. `Home.md`
3. `docs/03-CHANGE-MAP.md`
4. `CHANGELOG.md`

This gives you:
- a quick launch checklist;
- a visual overview;
- a working entry point;
- a map of editable files;
- project history.

---

## Core entry points

| File | Purpose |
|---|---|
| `docs/01-START-HERE.md` | fast onboarding and first checks |
| `Home.md` | main dashboard |
| `50-Система/Дашборды/Дедлайны.md` | deadline dashboard |
| `10-Университет/Университет.md` | academic overview |
| `20-Проекты/Проекты.md` | projects overview |
| `30-Личное/Личное.md` | personal overview |
| `50-Система/Шаблоны/Новая заметка.md` | note creation template |
| `.obsidian/snippets/university-dashboard-v5.css` | main UI system |
| `CHANGELOG.md` | project evolution |
| `99-Архив/README.md` | archive policy |

---

## Project structure at a glance

| Path | Role |
|---|---|
| `00-Inbox/` | inbox and raw capture |
| `10-Университет/` | subject-based study notes |
| `20-Проекты/` | project notes |
| `30-Личное/` | personal notes |
| `40-Знания/` | knowledge base |
| `50-Система/` | dashboards, templates, system notes |
| `99-Архив/` | archive and legacy materials |
| `.obsidian/` | plugin, appearance, and vault configuration |
| `docs/` | human-readable project documentation |

---

## Documentation map

| Document | Use it when you want to... |
|---|---|
| `docs/01-START-HERE.md` | launch the vault quickly |
| `docs/02-VAULT-STRUCTURE.md` | understand the full structure |
| `docs/03-CHANGE-MAP.md` | know exactly where to edit things |
| `docs/04-DASHBOARDS-AND-STYLES.md` | change UI or dashboard behavior |
| `docs/05-TEMPLATES-AND-CONTENT.md` | change templates and note model |
| `docs/06-PLUGINS.md` | understand plugin responsibilities |
| `docs/07-SIRIUS-SCHEDULE.md` | change group or schedule integration |
| `docs/08-TROUBLESHOOTING.md` | fix common problems |

---

## Safe customization zones

These are the files most people will want to edit:

- `Home.md`
- `50-Система/Дашборды/Дедлайны.md`
- `10-Университет/Университет.md`
- `20-Проекты/Проекты.md`
- `30-Личное/Личное.md`
- `50-Система/Шаблоны/Новая заметка.md`
- `.obsidian/snippets/university-dashboard-v5.css`
- `.obsidian/plugins/sirius-schedule/data.json`
- `sirius-update.py`

If you are unsure where to begin, open:
- `docs/03-CHANGE-MAP.md`

---

## Files you usually should not edit

| Path | Why |
|---|---|
| `.obsidian/plugins/*/main.js` | third-party plugin source |
| `.makemd/*` | Make.md internal files |
| `_Index_of_*.md` | system index files |
| `sirius-schedule.json` | data output, not source logic |
| `.git/*` | repository internals |

---

## Plugin requirements

The vault depends on community plugins, especially:
- Dataview
- Templater
- Sirius Schedule

Other configured plugins are documented in:
- `docs/06-PLUGINS.md`

---

## Design system

Main style file:
- `.obsidian/snippets/university-dashboard-v5.css`

This file controls:
- tokens;
- cards;
- dashboards;
- note callouts;
- document styling;
- shared UI language.

---

## Release philosophy

This repository is organized around two layers:

1. **Content layer** — notes, subjects, projects, deadlines, documents.
2. **System layer** — templates, snippets, dashboards, plugin configs, schedule logic.

That separation is intentional: it keeps the vault understandable, extensible, and maintainable.

---

## Maintenance policy

Starting with `v1.1.0`, every meaningful system change should update:
- `VERSION` — current project version;
- `CHANGELOG.md` — what changed and why;
- relevant files in `docs/` — where the behavior is explained.

Obvious junk files are ignored by `.gitignore`:
- macOS sidecars `._*` / `.DS_Store`;
- `Untitled*.md` and `Без названия*.md` scratch notes;
- temporary backup files such as `*.backup`, `*.bak`, `*.tmp`.

---

## Recommended next step

Open `docs/01-START-HERE.md`, then `Home.md` inside Obsidian.

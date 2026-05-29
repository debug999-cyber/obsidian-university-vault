# Style Guide

## Общий принцип

Функциональные страницы должны выглядеть как части одной системы. Нельзя делать каждый dashboard отдельным стилем.

## Frontmatter функциональной страницы

```yaml
---
cssclasses:
  - university-dashboard
---
```

## Структура функциональной страницы

Рекомендуемый порядок:

1. H1-заголовок.
2. Один `dataviewjs` блок.
3. Внутри блока:
   - `root.classList.add("university-dashboard", "ud-page")`
   - hero-блок;
   - статистика;
   - поиск, если есть списки;
   - секции;
   - карточки.

Пример:

```markdown
---
cssclasses:
  - university-dashboard
---

# Название

```dataviewjs
const root = dv.container;
root.classList.add("university-dashboard", "ud-page");
root.innerHTML = "";
// render UI
```
```

## Правила DataviewJS

- Не использовать глобальные `document.querySelector`, если можно искать внутри `root`.
- Не создавать много отдельных dataviewjs-блоков на одной странице без необходимости.
- Не дублировать большие куски логики между страницами, если можно упростить.
- Использовать `app.workspace.openLinkText(path, "", false)` для открытия заметок.
- Для изменения frontmatter использовать `app.fileManager.processFrontMatter`.

## Правила карточек

Карточка должна использовать:

```js
const row = root.createEl("div", { cls: "ud-card" });
row.style.setProperty("--ud-border-color", "var(--ud-teal)");
```

Внутри:

```js
const main = row.createEl("div", { cls: "ud-card-main" });
const link = main.createEl("a", { text: name, cls: "ud-card-link" });
const meta = main.createEl("div", { cls: "ud-card-meta" });
meta.createEl("span", { text: "метка", cls: "ud-card-tag" });
```

## Цвета

Использовать CSS-переменные:

```css
--ud-red
--ud-orange
--ud-yellow
--ud-green
--ud-teal
--ud-blue
--ud-purple
--ud-frost
--ud-status-overdue
--ud-status-today
--ud-status-soon
--ud-status-ok
--ud-status-done
--ud-status-work
```

Не вставлять случайные hex-цвета в DataviewJS.

## Визуальные маркеры

Emoji в функциональном интерфейсе не используются. Для actions и быстрых карточек применяются нейтральные буквенные коды и CSS-индикаторы.

Допустимо:

```js
button.createEl("span", { text: "S", cls: "ud-symbol" });
search.createEl("span", { text: "Поиск", cls: "ud-search-label" });
```

Не использовать декоративные emoji или внешние иконочные шрифты для базовой навигации.

## Мобильная адаптация

Новые сетки должны нормально схлопываться на мобильных. Если добавляешь новый grid-класс — добавь `@media` в CSS.

## Чего избегать

- Больших inline-style строк в JS.
- Нескольких разных кнопочных стилей.
- Ручных списков ссылок в MOC.
- Внешних картинок/CDN на функциональных страницах.
- Смешивания обычных учебных заметок и системной логики.

# Lite Planner App — UX Design Spec

## User Story
As a project manager, I want a Kanban-style dashboard where I can create tasks, assign them to agents, move tasks through status columns, and see live summary stats — all from a single, polished dark-theme page.

---

## User Flow

```
App Load
  └─► fetch GET /dashboard → populate stats bar
  └─► fetch GET /tasks     → render cards into columns
  └─► fetch GET /agents    → cache agent list for dropdowns

[+ New Task] click
  └─► Create Task modal opens
        └─► fill title, description, priority → [Create]
              └─► POST /tasks → card appears in "Todo" column
              └─► stats bar refreshes
        └─► [Cancel] / overlay click → modal closes, no change

[+ Add Agent] click
  └─► Add Agent modal opens
        └─► fill name, role → [Add Agent]
              └─► POST /agents → agent list refreshes in all dropdowns
        └─► [Cancel] → modal closes

Card: status dropdown change
  └─► PATCH /tasks/{id}/status → card moves to new column
  └─► stats bar refreshes

Card: assign agent dropdown change
  └─► PATCH /tasks/{id}/assign → card label updates to agent name
```

---

## Screens & Wireframes

### Screen: Full Dashboard (Desktop ≥1025px)

```
┌──────────────────────────────────────────────────────────────────────────┐
│  ◈ Lite Planner                             [+ Add Agent] [+ New Task]   │  ← header, 64px tall
├──────────────────────────────────────────────────────────────────────────┤
│  TOTAL  │   TODO   │  IN PROGRESS  │   REVIEW   │    DONE    │           │  ← stats bar, 72px tall
│   12    │    4     │      3        │     2      │     3      │           │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │ TODO      4  │ │ IN PROGRESS  │ │  REVIEW   2  │ │  DONE     3  │   │
│  ├──────────────┤ ├──────────────┤ ├──────────────┤ ├──────────────┤   │
│  │ ┌──────────┐ │ │ ┌──────────┐ │ │ ┌──────────┐ │ │ ┌──────────┐ │   │
│  │ │ HIGH     │ │ │ │ MED      │ │ │ │ LOW      │ │ │ │ HIGH     │ │   │
│  │ │ Fix bug  │ │ │ │ Write    │ │ │ │ Update   │ │ │ │ Deploy   │ │   │
│  │ │          │ │ │ │ docs     │ │ │ │ deps     │ │ │ │ v2.0     │ │   │
│  │ │ 👤 Alice │ │ │ │ 👤 Bob  │ │ │ │ Unassign.│ │ │ │ 👤 Alice │ │   │
│  │ │ [Status▾]│ │ │ │ [Status▾]│ │ │ │ [Status▾]│ │ │ │ [Status▾]│ │   │
│  │ │ [Agent▾] │ │ │ │ [Agent▾] │ │ │ │ [Agent▾] │ │ │ │ [Agent▾] │ │   │
│  │ └──────────┘ │ │ └──────────┘ │ │ └──────────┘ │ │ └──────────┘ │   │
│  │              │ │              │ │              │ │              │   │
│  │  (scroll ↓)  │ │  (scroll ↓)  │ │  (scroll ↓)  │ │  (scroll ↓)  │   │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### Screen: Dashboard — Mobile (≤768px)

```
┌──────────────────────────┐
│ ◈ Lite Planner  [+Agent] │  ← header 56px
│                 [+Task]  │
├──────────────────────────┤
│ TOTAL 12  TODO 4  IP 3   │  ← stats bar scrolls horizontally; 60px
│ REVIEW 2  DONE 3         │
├──────────────────────────┤
│ [TODO] [IN PROG] [REV] [DONE]  │  ← tab strip, full width
├──────────────────────────┤
│  ┌────────────────────┐  │
│  │ HIGH               │  │
│  │ Fix login bug      │  │
│  │ 👤 Alice           │  │
│  │ [Status ▾][Agent ▾]│  │
│  └────────────────────┘  │
│  ┌────────────────────┐  │
│  │ LOW                │  │
│  │ Update deps        │  │
│  │ 👤 Unassigned      │  │
│  │ [Status ▾][Agent ▾]│  │
│  └────────────────────┘  │
└──────────────────────────┘
```

### Screen: Create Task Modal

```
┌──────────────────────────────────────┐
│  ✕                    Create Task    │
├──────────────────────────────────────┤
│  Title *                             │
│  ┌────────────────────────────────┐  │
│  │ e.g. Fix login bug             │  │
│  └────────────────────────────────┘  │
│                                      │
│  Description                         │
│  ┌────────────────────────────────┐  │
│  │                                │  │
│  │  (4 rows tall)                 │  │
│  └────────────────────────────────┘  │
│                                      │
│  Priority                            │
│  ┌────────────────────────────────┐  │
│  │ Medium                       ▾ │  │
│  └────────────────────────────────┘  │
│                                      │
│  [Cancel]              [Create Task] │
└──────────────────────────────────────┘
```

### Screen: Add Agent Modal

```
┌──────────────────────────────────────┐
│  ✕                     Add Agent    │
├──────────────────────────────────────┤
│  Name *                              │
│  ┌────────────────────────────────┐  │
│  │ e.g. Alice                     │  │
│  └────────────────────────────────┘  │
│                                      │
│  Role *                              │
│  ┌────────────────────────────────┐  │
│  │ e.g. Senior Dev                │  │
│  └────────────────────────────────┘  │
│                                      │
│  [Cancel]               [Add Agent]  │
└──────────────────────────────────────┘
```

---

## Color Palette

| Token                  | Hex       | Usage                                          |
|------------------------|-----------|------------------------------------------------|
| `--bg`                 | `#0f1117` | Page background                                |
| `--surface`            | `#1a1d27` | Kanban column background                       |
| `--card`               | `#22263a` | Task card background                           |
| `--card-hover`         | `#2a2f47` | Task card on hover                             |
| `--header-bg`          | `#13161f` | Header & stats bar background                  |
| `--border`             | `#2e3350` | Column borders, card borders, input borders    |
| `--border-focus`       | `#5b6af0` | Input/select focus ring                        |
| `--text-primary`       | `#e8eaf6` | Body text, card titles                         |
| `--text-secondary`     | `#8892b0` | Muted labels (agent name, column count)        |
| `--text-heading`       | `#ffffff` | Page title, column headers                     |
| `--accent`             | `#5b6af0` | Primary CTA buttons, active tab, focus ring    |
| `--accent-hover`       | `#4a57d4` | Primary button hover                           |
| `--btn-ghost`          | `#2e3350` | Ghost/secondary button background              |
| `--btn-ghost-hover`    | `#3a4060` | Ghost button hover                             |
| `--priority-high`      | `#e05252` | High priority badge background                 |
| `--priority-high-text` | `#ffffff` | High priority badge text                       |
| `--priority-med`       | `#d4a017` | Medium priority badge background               |
| `--priority-med-text`  | `#1a1a1a` | Medium priority badge text (dark for contrast) |
| `--priority-low`       | `#27ae60` | Low priority badge background                  |
| `--priority-low-text`  | `#ffffff` | Low priority badge text                        |
| `--col-todo`           | `#8892b0` | Todo column header accent line                 |
| `--col-inprogress`     | `#5b6af0` | In Progress column header accent line          |
| `--col-review`         | `#d4a017` | Review column header accent line               |
| `--col-done`           | `#27ae60` | Done column header accent line                 |
| `--shadow`             | `rgba(0,0,0,0.4)` | Card box-shadow                         |
| `--overlay`            | `rgba(0,0,0,0.65)` | Modal backdrop                         |
| `--success-toast`      | `#27ae60` | Success toast background                       |
| `--error-toast`        | `#e05252` | Error toast background                         |

---

## Typography

- **Font family:** `'Inter', system-ui, -apple-system, sans-serif`
  - Import from Google Fonts: `Inter` weights 400, 500, 600, 700
- **Base size:** 16px (1rem)

| Role              | Size      | Weight | Line-height |
|-------------------|-----------|--------|-------------|
| Page title (h1)   | 1.25rem   | 700    | 1.3         |
| Column header (h2)| 0.75rem   | 700    | 1           |
| Card title        | 0.9rem    | 600    | 1.4         |
| Body / description| 0.85rem   | 400    | 1.5         |
| Badge / label     | 0.65rem   | 700    | 1           |
| Stats number      | 1.5rem    | 700    | 1           |
| Stats label       | 0.65rem   | 500    | 1           |
| Button            | 0.875rem  | 600    | 1           |
| Input             | 0.875rem  | 400    | 1.5         |
| Muted (agent name)| 0.75rem   | 400    | 1           |

---

## Layout & Spacing

- **Spacing unit:** 8px
- **Page padding:** 0 24px (desktop), 0 16px (mobile)
- **Header height:** 64px (desktop), 56px (mobile)
- **Stats bar height:** 72px (desktop), 60px (mobile — horizontal scroll)
- **Kanban board:** CSS Grid, `grid-template-columns: repeat(4, 1fr)`, `gap: 16px`
- **Column:** min-width 220px, `max-height: calc(100vh - 64px - 72px - 32px)`, `overflow-y: auto`
- **Column header:** 40px tall, 12px padding horizontal
- **Column padding:** 12px
- **Card:** padding 12px, `border-radius: 8px`, `margin-bottom: 10px`
- **Card min-height:** 100px
- **Modal width:** 480px (centered), max-width 95vw on mobile
- **Modal padding:** 24px
- **Input height:** 40px, `border-radius: 6px`, padding 0 12px
- **Textarea rows:** 4
- **Button height:** 40px, `border-radius: 6px`, padding 0 16px
- **Badge:** 4px 8px padding, `border-radius: 4px`
- **Priority badge position:** top-left corner of card, displayed as first element

### Responsive Breakpoints

| Breakpoint           | Columns layout                                   |
|----------------------|--------------------------------------------------|
| Mobile ≤ 768px       | Tab strip — single column shown per tab          |
| Tablet 769–1024px    | 2-column grid (`grid-template-columns: 1fr 1fr`) |
| Desktop ≥ 1025px     | 4-column grid (`grid-template-columns: repeat(4, 1fr)`) |

On mobile the Kanban becomes a **tab strip** (4 tabs: Todo / In Progress / Review / Done). Only one column's cards are visible at a time. The active tab has the column's accent-color underline.

---

## Component Specs

### Stats Bar

| Element         | Detail                                                              |
|-----------------|---------------------------------------------------------------------|
| Container       | Full-width, 72px tall (desktop), horizontal flex, `gap: 8px`      |
| Stat block      | Flex column, centered; number on top (1.5rem bold), label below (0.65rem, `--text-secondary`) |
| Divider         | 1px `--border` between each stat block                             |
| Counts          | Total · Todo · In Progress · Review · Done                         |
| Data source     | `GET /dashboard` on load and after every status change             |
| Loading state   | Each number shows `—` until data arrives                           |

### Kanban Column

| Element         | Detail                                                              |
|-----------------|---------------------------------------------------------------------|
| Container       | `background: --surface`, `border-radius: 10px`, `border: 1px solid --border` |
| Header          | 40px; column name uppercase 0.75rem 700 weight; count badge (muted); 3px top border in column accent color |
| Scroll          | `overflow-y: auto`; custom scrollbar: 4px wide, `--border` track, `--accent` thumb |
| Empty state     | Centered text "No tasks" in `--text-secondary`, 0.8rem, italics, 40px vertical padding |

### Task Card

| Element         | Detail                                                              |
|-----------------|---------------------------------------------------------------------|
| Container       | `background: --card`, `border-radius: 8px`, `border: 1px solid --border`, `box-shadow: 0 2px 8px --shadow` |
| Priority badge  | Pill shape, 4px 8px padding, 4px radius, uppercase 0.65rem bold; colors per `--priority-*` tokens |
| Title           | 0.9rem 600 weight, `--text-primary`, 6px below badge               |
| Agent line      | 👤 icon + name; 0.75rem `--text-secondary`; "Unassigned" in italics when null |
| Status dropdown | `<select>` styled as pill; `background: --btn-ghost`, `--text-primary`, no system arrow — custom caret via `appearance:none` + background SVG |
| Agent dropdown  | Same style as status dropdown; lists all agents + "Unassigned" option at top |
| Card hover      | `background` transitions to `--card-hover`, `transform: translateY(-2px)`, `box-shadow` deepens; 150ms ease |
| Card appear     | New cards animate in: `opacity 0→1` + `transform: translateY(8px)→0`, 200ms ease |

### Create Task Modal

| Element         | Detail                                                              |
|-----------------|---------------------------------------------------------------------|
| Overlay         | Fixed full-screen, `background: --overlay`; click outside = close  |
| Container       | White (use `--card`), centered, 480px wide, `border-radius: 12px`, `box-shadow: 0 16px 48px rgba(0,0,0,0.6)` |
| Title input     | Required; shows inline validation error "Title is required" in `--priority-high` below input if submitted empty |
| Description     | Optional textarea, 4 rows                                           |
| Priority select | Dropdown with options: Low / Medium (default) / High                |
| [Create Task]   | Primary button, `background: --accent`, `--text-heading`; disabled + 0.5 opacity while submitting |
| [Cancel]        | Ghost button, `background: --btn-ghost`                            |
| Success         | Modal closes; card slides into Todo column; stats bar refreshes     |
| Error           | Toast appears (bottom-right, 3s auto-dismiss): "Failed to create task" on `--error-toast` |
| Open animation  | Modal scales from 0.95→1 + `opacity 0→1`, 180ms ease-out           |
| Close animation | Reverses: 0.95 + opacity 0, 150ms ease-in                          |

### Add Agent Modal

| Element         | Detail                                                              |
|-----------------|---------------------------------------------------------------------|
| Layout          | Same overlay/container pattern as Create Task modal                 |
| Name input      | Required; inline validation "Name is required"                      |
| Role input      | Required; inline validation "Role is required"                      |
| [Add Agent]     | Primary button; disabled while submitting                           |
| Success         | Modal closes; agent list in all open dropdowns refreshes            |
| Error           | Toast: "Failed to add agent"                                        |

---

## Interaction Notes

- **Loading (initial):** Board area shows 4 skeleton columns, each with 2 skeleton cards (gray animated shimmer rectangles — `background: linear-gradient(90deg, --surface, --card, --surface)`, `background-size: 200%`, `animation: shimmer 1.4s infinite`). Stats bar numbers show `—`.
- **Empty state (no tasks):** Each column shows the "No tasks" placeholder. Board still renders all 4 columns.
- **Empty state (no agents):** Agent dropdowns on cards show only "Unassigned". The Add Agent button is visually promoted (pulsing glow: `box-shadow: 0 0 0 0 --accent`, keyframe expanding).
- **Status change feedback:** The card briefly flashes a `--accent` left border (200ms) then slides/fades out of its old column and appears in the new column with the card-appear animation.
- **Error state (fetch failure):** A persistent inline banner below the stats bar: `⚠ Could not load tasks. Retry` — link re-triggers `GET /tasks`. Color: `--error-toast` background at 15% opacity, `--error-toast` text.
- **Success toast:** Bottom-right, 320px wide, 48px tall, `border-radius: 8px`, white text, auto-dismiss 3s with a slide-up-in / slide-down-out animation (translateY 20px → 0, 200ms).
- **Hover/focus on inputs:** `border-color` transitions to `--border-focus`, 150ms; `box-shadow: 0 0 0 3px rgba(91,106,240,0.25)`.
- **Disabled buttons:** `opacity: 0.5`, `cursor: not-allowed`.
- **Scrollbar (columns):** Thin custom: `::-webkit-scrollbar { width: 4px }`, `::-webkit-scrollbar-thumb { background: --accent; border-radius: 2px }`.

---

## CSS Class Naming Convention

All classes follow **BEM-inspired kebab-case** with a `planner-` prefix.

### Layout

| Class                    | Element                                      |
|--------------------------|----------------------------------------------|
| `.planner-app`           | Root wrapper `<div>`                         |
| `.planner-header`        | Top header bar                               |
| `.planner-header__logo`  | App name / logo text                         |
| `.planner-header__actions` | Button group (Add Agent, New Task)         |
| `.planner-stats`         | Stats bar container                          |
| `.planner-stats__item`   | Individual stat block                        |
| `.planner-stats__number` | Large stat count                             |
| `.planner-stats__label`  | Stat label text                              |
| `.planner-stats__divider`| Vertical divider between stat items          |
| `.planner-board`         | Kanban 4-column CSS Grid container           |
| `.planner-tabs`          | Mobile tab strip (hidden on desktop)         |
| `.planner-tab`           | Individual tab button                        |
| `.planner-tab--active`   | Currently selected tab                       |

### Columns

| Class                       | Element                                   |
|-----------------------------|-------------------------------------------|
| `.planner-column`           | Column container                          |
| `.planner-column--todo`     | Todo column modifier                      |
| `.planner-column--inprogress` | In Progress column modifier             |
| `.planner-column--review`   | Review column modifier                    |
| `.planner-column--done`     | Done column modifier                      |
| `.planner-column__header`   | Column title row                          |
| `.planner-column__title`    | Column name text                          |
| `.planner-column__count`    | Card count badge                          |
| `.planner-column__body`     | Scrollable card list area                 |
| `.planner-column__empty`    | Empty state message                       |

### Task Cards

| Class                       | Element                                   |
|-----------------------------|-------------------------------------------|
| `.planner-card`             | Card container                            |
| `.planner-card--appear`     | Applied on insert, removed after animation|
| `.planner-card__badge`      | Priority badge                            |
| `.planner-card__badge--high`  | High priority modifier                  |
| `.planner-card__badge--medium`| Medium priority modifier                |
| `.planner-card__badge--low`   | Low priority modifier                   |
| `.planner-card__title`      | Task title                               |
| `.planner-card__agent`      | Agent line (icon + name)                 |
| `.planner-card__agent--unassigned` | Italic unassigned state            |
| `.planner-card__controls`   | Row holding status + agent dropdowns     |
| `.planner-card__select`     | Shared style for both dropdowns          |
| `.planner-card__select--status` | Status dropdown modifier             |
| `.planner-card__select--agent`  | Agent dropdown modifier              |

### Modals

| Class                       | Element                                   |
|-----------------------------|-------------------------------------------|
| `.planner-overlay`          | Full-screen backdrop                      |
| `.planner-modal`            | Modal container box                       |
| `.planner-modal--open`      | Trigger open animation                    |
| `.planner-modal__header`    | Modal title row                           |
| `.planner-modal__title`     | Modal heading text                        |
| `.planner-modal__close`     | ✕ close button                            |
| `.planner-modal__body`      | Form content area                         |
| `.planner-modal__footer`    | Button row                                |

### Forms

| Class                       | Element                                   |
|-----------------------------|-------------------------------------------|
| `.planner-form__group`      | Label + input wrapper                     |
| `.planner-form__label`      | `<label>` element                         |
| `.planner-form__input`      | Text `<input>`                            |
| `.planner-form__textarea`   | `<textarea>`                              |
| `.planner-form__select`     | `<select>` in modal form                  |
| `.planner-form__error`      | Inline validation error message           |

### Buttons

| Class                       | Element                                   |
|-----------------------------|-------------------------------------------|
| `.planner-btn`              | Base button                               |
| `.planner-btn--primary`     | Accent CTA (Create Task, Add Agent)       |
| `.planner-btn--ghost`       | Secondary / cancel                        |
| `.planner-btn--sm`          | Small button variant (header actions)     |
| `.planner-btn--loading`     | Disabled + spinner state                  |

### Feedback

| Class                       | Element                                   |
|-----------------------------|-------------------------------------------|
| `.planner-toast`            | Toast notification container              |
| `.planner-toast--success`   | Green success variant                     |
| `.planner-toast--error`     | Red error variant                         |
| `.planner-toast--show`      | Slide-in visible state                    |
| `.planner-banner`           | Persistent inline error banner            |
| `.planner-skeleton`         | Shimmer skeleton block                    |
| `.planner-skeleton--card`   | Card-shaped skeleton                      |

---

## Open Questions

- [x] **RESOLVED** Should completed tasks in the **Done** column be visually de-emphasised? → **Keep full-contrast.** Green column accent is sufficient signal. No opacity or strikethrough needed.
- [x] **RESOLVED** Is there a task detail/expand view needed? → **No, not in v1.** Card-face-only is accepted; description field is not surfaced on the card.

# UniAsk — RAG Admin Dashboard

A frontend-only dashboard for a RAG (Retrieval-Augmented Generation) system.
No build tool, no bundler — just open `index.html` in a browser.

---

## ▶ How to run in VS Code (easiest)

1. Install the **Live Server** extension by *Ritwick Dey*
2. Right-click `index.html` → **"Open with Live Server"**
3. Browser opens at `http://127.0.0.1:5500`

> ⚠️ You must use a local server (Live Server or `npx live-server`).
> Opening `index.html` directly as `file://` will block the `<script src="…">` loads.

### Alternative — terminal
```bash
npm install      # installs live-server locally
npm start        # opens http://localhost:3000
```

---

## 📁 Full project structure

```
uniask-dashboard/
│
├── index.html              ← Entry point. Loads scripts in order.
│
├── package.json            ← Optional: only needed for `npm start`
│
├── css/
│   └── main.css            ← ALL styles (CSS variables, layout, components)
│
└── js/
    │
    ├── icons.js            ← Icon.Dashboard, Icon.Trash, Icon.Bell … (SVG)
    ├── i18n.js             ← TRANSLATIONS object + makeT(lang) helper
    ├── data.js             ← INIT_DOCS, INIT_ADMINS, TYPE_COLORS (mock data)
    ├── charts.js           ← <Sparkline> <BarChart> <DonutChart>
    │
    ├── Sidebar.js          ← Fixed left nav + user card
    ├── Topbar.js           ← Sticky header: title, dark mode, lang switch
    ├── App.js              ← Root component: routing, dark/RTL, ReactDOM mount
    │
    └── pages/
        ├── Dashboard.js    ← Stats grid, weekly chart, activity feed
        ├── Knowledge.js    ← Document upload, search, table
        ├── Analysis.js     ← Topic coverage bars + unanswered queries
        ├── Inbox.js        ← Query log with confidence scores
        ├── Admins.js       ← Admin table + invite modal
        └── Settings.js     ← LLM config, chunking, feature flags, vector DB
```

---

## 🔧 No package.json / no build tool needed

This project deliberately has **no bundler** (no webpack, vite, parcel etc.).
React, ReactDOM, and Babel are loaded from CDN in `index.html`:

```html
<script src="https://unpkg.com/react@18/umd/react.development.js"></script>
<script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
<script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
```

Scripts are loaded as `type="text/babel"` so JSX is transpiled in the browser at runtime.

---

## 🌐 Assets

There are **no image assets** in this project. All visuals are:
- SVG icons defined inline in `js/icons.js`
- CSS-drawn UI (gradients, borders, shadows) in `css/main.css`
- SVG charts rendered by React components in `js/charts.js`
- Google Fonts loaded from CDN (DM Sans + Space Grotesk)

---

## 🌍 i18n (English / Arabic)

- All UI strings live in `js/i18n.js` under `TRANSLATIONS.en` and `TRANSLATIONS.ar`
- Switch language with the **AR / EN** button in the top-right
- Arabic mode automatically sets `dir="rtl"` on `<html>` via `App.js`

---

## 🔌 Connecting to a real backend

Every API call is stubbed with mock data. Search for `// BACKEND:` comments
throughout the `js/` files — each one shows the exact endpoint to implement.

Key endpoints:
| File            | Endpoints needed                                      |
|-----------------|-------------------------------------------------------|
| `data.js`       | `GET /api/documents`, `GET /api/admins`              |
| `Dashboard.js`  | `GET /api/stats`, `GET /api/queries/daily`           |
| `Knowledge.js`  | `POST /api/documents/upload`, `DELETE /api/documents/:id` |
| `Analysis.js`   | `GET /api/analysis/gaps`, `GET /api/analysis/unanswered` |
| `Inbox.js`      | `GET /api/queries`, `POST /api/queries/:id/feedback` |
| `Admins.js`     | `GET /api/admins`, `POST /api/admins`, `DELETE /api/admins/:id` |
| `Settings.js`   | `GET/PUT /api/settings/*`                            |

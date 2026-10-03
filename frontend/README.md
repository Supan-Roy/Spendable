# Spendable Frontend — React 19 + TypeScript + Vite

A high-performance, dark glassmorphism web application built with **React 19**, **TypeScript**, **Vite**, and **Vanilla CSS**.

---

## ⚡ Navigation Tabs & Features

The application features 5 main pages accessible from the persistent top navigation header:

1. **Overview (`OverviewPage.tsx`)**:
   - Live Spendable Capacity progress bar, safe daily spending limit, upcoming 30-day bill timeline cards, and recommendation widgets.

2. **Activity (`ActivityPage.tsx`)**:
   - Ingested multi-channel financial transaction activity stream with pagination, search, category filters, and ISO 8601 UTC timestamp formatting.

3. **Forecast (`ForecastPage.tsx`)**:
   - 30-day cash flow runway trajectory chart, HistGradientBoosting projected minimum balance drawdowns, and recurring commitment dates.

4. **Simulate (`SimulatePage.tsx`)**:
   - What-If Scenario Engine supporting 5 scenario types (`ONE_TIME_EXPENSE`, `ADDITIONAL_INCOME`, `ADDITIONAL_COMMITMENT`, `SPENDING_REDUCTION`, `INCOME_DELAY`).
   - Multi-Metric Impact Dashboard comparing Spendable Shift, Current Balance Shift, 30-Day Minimum Runway, and Protected Buffer.
   - Collapsible **Spendable AI** chat assistant with formatted markdown rendering and context attachment.

5. **Inspect ⚡ (`InspectPage.tsx`)**:
   - Hackathon system visualizer showing the end-to-end 5-stage processing pipeline in a connected 2-row rounded flow layout.
   - Deep-dive cards detailing HistGradientBoostingRegressor parameters, point-in-time regularity scoring, and code-enforced financial math boundaries (0 Gemini API calls consumed).

---

## 🛠️ Key Components

- **`Header.tsx`**: Navigation menu, mobile drawer, account badge, and demo persona selector (`acc_supan`, `acc_meraj`, `acc_sohana`, `acc_noman`, `acc_refat`).
- **`CalculationModal.tsx`**: Mathematical formula modal detailing the non-double-counting Spendable equation.
- **`LoginModal.tsx`**: Custom account creation, login, and instant demo account quick-selector.
- **`ConfirmModal.tsx`**: Reusable confirmation modal for account deletions and critical actions.

---

## 🚀 Development & Build

```bash
# Run local dev server (port 5173 with proxy to backend port 8000)
pnpm run dev

# Build production bundle & check TypeScript compilation
pnpm --prefix frontend build
```

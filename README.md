# SPENDABLE 💡

> **"Know what you can safely spend."**

Spendable is an AI-powered personal financial runway and liquidity intelligence product designed for **Upay** customers. 

While a traditional mobile financial service (MFS) balance tells customers how much money they currently have, **Spendable** calculates and predicts how much of that balance is realistically and safely spendable after accounting for expected short-term outflows, recurring commitments, behavioral patterns, and safety buffers.

---

## 🏆 Hackathon Context

- **Event:** AI DEV FEST 2026 AI Hackathon
- **Organizer:** DIU Computer and Programming Club (DIU-CPC), Department of CSE, Daffodil International University
- **Ecosystem:** Upay Ecosystem
- **Track:** **Track 03 — Customer Innovation & Financial Independence**
- **Status:** Initial Skeleton / Foundation Phase Initialized

---

## ⚡ Single Command Development (`pnpm run dev`)

To launch the **entire project** (PostgreSQL Docker container, FastAPI backend, and React Vite frontend concurrently):

```bash
pnpm run dev
```

This single command automatically:
1. Starts the PostgreSQL container via Docker Compose (`docker compose up -d postgres`).
2. Launches the FastAPI backend API server via the root Python virtual environment (`venv`).
3. Launches the Vite React frontend server.

---

## 🏗️ Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend** | React 19, TypeScript, Vite, Vanilla CSS Design System |
| **Backend** | Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy |
| **Database** | PostgreSQL (supported via SQLAlchemy & psycopg2-binary) |
| **ML & Analytics** | Python Ecosystem (`pandas`, `numpy`, `scikit-learn` - planned) |
| **AI / LLM** | Google Gemini API (planned for natural-language explanations) |
| **Testing** | `pytest`, `httpx`, `FastAPI TestClient` |
| **Containerization** | Docker, Multi-stage Dockerfiles, Docker Compose |
| **Deployment Target** | Railway (Monorepo Dockerfile deployment ready) |

---

## 📁 Repository Structure

```
Spendable/
├── .env.example              # Root environment template
├── .gitignore                # Global git ignore configuration
├── docker-compose.yml        # Local multi-container development environment
├── package.json              # Monorepo root developer commands
├── pnpm-workspace.yaml       # pnpm workspace configuration
├── README.md                 # Project documentation
├── venv/                     # Root Python virtual environment
├── backend/
│   ├── .env.example          # Backend environment template
│   ├── Dockerfile            # Container configuration for backend API
│   ├── requirements.txt      # Python dependencies
│   ├── app/
│   │   ├── main.py           # FastAPI application entry point
│   │   ├── config.py         # Pydantic configuration settings
│   │   ├── database.py       # SQLAlchemy PostgreSQL connection management
│   │   └── api/
│   │       └── health.py     # System health check endpoint
│   └── tests/
│       ├── test_health.py    # Health endpoint pytest suite
│       └── test_config.py    # Configuration pytest suite
└── frontend/
    ├── .env.example          # Frontend environment template
    ├── Dockerfile            # Multi-stage production container configuration
    ├── nginx.conf            # Nginx SPA fallback configuration
    ├── package.json          # Frontend scripts & dependencies
    ├── vite.config.ts        # Vite build configuration
    └── src/
        ├── App.tsx           # Initial Spendable React landing component
        ├── index.css         # Custom dark glassmorphism design system
        └── main.tsx          # React application mount
```

---

## 💻 Manual Setup & Environment Activation

### Virtual Environment Activation
The root Python virtual environment is located at `d:\Programs and Codes\Spendable\venv`.

- **On Windows PowerShell:**
  ```powershell
  .\venv\Scripts\activate
  ```
- **On Linux/macOS:**
  ```bash
  source venv/bin/activate
  ```

---

## 🧪 Testing

Backend testing is enforced via `pytest` using the root virtual environment:

```bash
pnpm test
```
*(Or manually: `.\venv\Scripts\pytest.exe backend\tests`)*

---

## 🚀 Deployment (Railway Target)

The project is structured for seamless monorepo deployment on **Railway**:
- **Backend:** Deployed via `backend/Dockerfile`. Configured to dynamically bind to `$PORT` provided by Railway environment.
- **Frontend:** Deployed via `frontend/Dockerfile` as an Nginx static SPA container or web service.
- **Database:** PostgreSQL service attached via Railway `DATABASE_URL`.

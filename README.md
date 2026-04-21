# 🤖 AI-Native Hardware Hub

Internal app for Booksy employees to manage, rent, and maintain company hardware, built as part of the recruitment assessment.

---

## 📌 Project Context

- **Management Engine** (Admin + Users)
- **Rental Engine** (rent/return business logic with guards)
- **AI-Native Layer** (LLM assistant for inventory support)

---

## 🧱 Tech Stack

- **Backend:** Python + Flask + SQLAlchemy
- **Frontend:** React + TypeScript
- **Database:** SQLite
- **AI Providers:** Ollama / OpenAI / Gemini (configurable)
- **Testing:** pytest

---

## ✨ What This App Does

- Admin can add/update/delete hardware and create user accounts.
- Users can log in and see hardware inventory.
- Hardware list supports filtering and sorting.
- Users can rent and return devices with state guards.
- AI assistant supports:
  - hardware creation from text/images,
  - stock lookup in natural language,
  - recommendation-style questions using inventory tool calls.

**Documentation:** **[User guide](./docs/USER_GUIDE.md)** (login, renting, filters) · **[Hardware & status reference](./docs/USER_GUIDE_REFERENCE.md)** (fields & statuses)

---

## ✅ Fully Implemented (Stable)

- Authentication flow with account-based access.
- Admin command center:
  - hardware CRUD,
  - account creation.
- Rental logic with protections.
- Dashboard with filtering/sorting by key fields.
- Assistant chat API + UI integration.
- Tool-based inventory queries (`inventory_search`, `inventory_stats`) wired into assistant flow.
- Ordered/pre-arrival semantics supported in assistant tooling (`Ordered` handling aligned with pre-arrival logic).
- Test coverage for critical backend flows and assistant tooling behavior.

---

## ⚠ Partial / Missing

- No advanced recommendation scoring model (still largely LLM-driven).
- Response quality/hallucination risk remains model-dependent; self-hosted models are more prone to errors with complex prompts/tool flows.
- Limited observability (basic logs exist, but no full tracing/metrics dashboard).
- No deployment recipe included here (local-first implementation).

---

## 🔮 Next Steps (24h Roadmap)

If I had one more focused day, top priorities:

1. **Stabilize Assistant Pipeline**
   - add structured retries and parser recovery for malformed model outputs,
   - add automatic fallback model/provider strategy.

2. **Recommendation Quality Upgrade**
   - introduce explicit inventory metadata (`category`, `performance_tier`, `estimated_value`),
   - deterministic ranking for “cheapest/basic/suitable for X”.

3. **Production Readiness**
   - add richer monitoring + error analytics,
   - instead of coding around self-hosted model, test the paid LLMs.

---

## 🚀 Local setup

### Prerequisites

- **Python** 3.10+ (with `python` / `py` on `PATH`)
- **Node.js** 18+ and **npm** (for the Vite frontend)

### 1. Backend virtualenv and dependencies

From the repo root:

**Windows (PowerShell)**

```powershell
python -m venv backend\.venv
.\backend\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
```

**macOS / Linux**

```bash
python3 -m venv backend/.venv
source backend/.venv/bin/activate
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
```

Keep the venv activated for all backend commands below (or call the interpreter explicitly: `backend\.venv\Scripts\python.exe` on Windows).

### 2. Environment file

```powershell
copy .env.example .env
```

Edit **`.env`** at the repo root (Flask loads it from there via `backend/run.py`). Minimum for a quick run: `FLASK_SECRET_KEY`, `DATABASE_URL` (default SQLite path is fine), and optional LLM settings if you use the assistant.

### 3. Database location and seeding

- **SQLite file (default):** `backend/instance/hardwarehub.db` when `DATABASE_URL` is `sqlite:///backend/instance/hardwarehub.db` (see `.env.example`).
- **Seed file for hardware:** `backend/app/seed/seed_data.json` (imported only when the `hardware` table is empty).

From repo root, with the venv active:

```powershell
python backend\scripts\init_db.py
python backend\scripts\seed_db.py
python backend\scripts\seed_users.py
```

- `init_db.py` — creates tables.
- `seed_db.py` — imports seed hardware from JSON if the inventory is empty.
- `seed_users.py` — creates default users **only if no users exist** (skips if you already have accounts).

### 4. Seeded login accounts

Created by `seed_users.py` (when the users table was empty):

| Email              | Password    | Role  |
| ------------------ | ----------- | ----- |
| `admin@booksy.com` | `Admin123!` | admin |
| `user@booksy.com`  | `User123!`  | user  |

Login emails must use the **`@booksy.com`** domain (enforced in the UI). Change passwords after first use in a real deployment.

### 5. Start the backend

From repo root, venv active, default port **5000**:

**Windows**

```powershell
$env:PORT = "5000"
python backend\run.py
```

**macOS / Linux**

```bash
export PORT=5000
python backend/run.py
```

API base: `http://127.0.0.1:5000/` (health: `GET /` → JSON). CORS for the SPA is configured for `http://localhost:5173` by default.

### 6. Start the frontend

New terminal, from repo root:

```powershell
cd frontend
npm install
npm run dev
```

App URL: **http://localhost:5173** (Vite dev server; `VITE_API_BASE_URL` in `.env` should point at the backend, usually `http://localhost:5000`).

### 7. Run backend tests (optional)

```powershell
cd backend
pytest -q
```

---

## 🤖 AI Development Log

👉 **[Full document](./docs/AI_LOG.md)**

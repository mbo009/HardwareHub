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

## 🚀 Local Setup (Quick)

1. Create backend venv and install dependencies.
2. Configure `.env` (provider keys / Ollama URL / model).
3. Start backend.
4. Start frontend.
5. Log in with seeded/admin credentials and test flows.

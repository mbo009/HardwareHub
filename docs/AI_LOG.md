# 🤖 AI Development Log

This document outlines the synergy between human engineering and AI assistance during the development of the Hardware Hub.

---

## 🛠 Tooling & Models Used

- **Chatbot as a consultant**: Gemini 2.5 Pro.
- **Primary IDE**: Cursor.
- **LLM Orchestrator**: Ollama (Self-hosted).
- **Models**:
  - **Qwen2.5-Coder**: Used for core backend logic and architectural planning.
  - **Llava-v1.5**: Utilized for vision-based hardware identification tasks.
- **Reason for Self-Hosting**: Transitioned to local LLMs due to API quota limitations and the lack of free tier availability for certain providers in the EU. This ensured a private, high-performance environment.

---

## 🔍 Data Strategy & Audit

I leveraged AI to audit the initial `seed_data.json`, which revealed several inconsistencies that were manually corrected:

- **Duplicate IDs**: Identified and resolved a conflict where ID #4 was assigned to two different devices.
- **Invalid Dates**: Detected a purchase date set in 2027, which was corrected to reflect a realistic timeline.
- **Data Normalization**: Typos in brand names (e.g., "Appel" vs "Apple") and standardized missing serial numbers.

---

## ⚡ The "Correction": Human-in-the-Loop

Below are specific instances where I intervened to correct suboptimal AI suggestions:

### 1. Data Integrity: Deleting Rented Hardware

- **The AI Mistake**: The AI initially generated a simple `DELETE` endpoint that allowed an admin to remove hardware from the database regardless of its status.
- **The Correction**: I identified a risk where deleting a device currently marked as "In Use" would "orphan" active rental records and cause logic errors.
- **The Fix**: I forced the implementation of a business guard that returns a `409 Conflict` if the hardware is not in an `Available` or `Repair` state.

### 2. Scalability: Client-Side vs Server-Side Logic

- **The AI Mistake**: For the "Smart Dashboard," the AI proposed fetching the entire hardware list and performing filtering/sorting on the client side.
- **The Correction**: While acceptable for the seed dataset, this approach is not production-ready for a real company inventory.
- **The Fix**: I rejected the code and guided the AI to implement **Server-Side Pagination and Filtering** directly in the SQLAlchemy queries to ensure high performance.

### 3. AI Hallucinations: Domain Enforcement

- **The AI Mistake**: During tool-calling implementation, the model occasionally defaulted to general training data, providing answers unrelated to hardware (e.g., cooking recipes).
- **The Correction**: I identified that the general-purpose prompt was too broad for a specialized internal tool.
- **The Fix**: Narrowed the **System Prompt** to strictly enforce the "Hardware Hub" domain and implemented a **2-stage AI Pipeline** (Planner → Executor) to ensure answers are strictly database-driven.

### 4. Code Bloat & Reusability

- **The AI Pattern**: The assistant kept growing logic in a single file and paid little attention to reuse, shared helpers, or clear module boundaries.
- **The Correction**: I flagged this as **maintainability debt** early and steered refactors toward smaller units, shared utilities, and separation of concerns so changes do not require editing one oversized module.

### 5. Future Purchase Dates & the **Ordered** Status

- **The Gap**: A purchase date **after today** was easy to treat only as a hard validation error.
- **The Fix**: I introduced a dedicated **`Ordered`** state so “not yet delivered / pre-arrival” becomes **valid business information** instead of only a failing constraint—turning a rigid error into a workflow the domain actually uses.

### 6. Assistant Design: Heuristic Bot vs Two-LLM Delegation

- **The AI Proposal**: A **heuristic** chatbot (rules and shortcuts layered on a single model).
- **My Counter-Proposal**: Extend to **two LLMs** with explicit **delegation of responsibilities** (split roles, clearer contracts between steps) rather than one opaque pipeline.

### 7. Admin Onboarding: User Creation & Password Flow

- **The AI Proposal**: Tendency toward **another full panel** or parallel flow for provisioning accounts.
- **My Counter-Proposal**: A **first-class user-creation path** inside the existing admin experience (no unnecessary new surface), plus a **two-step registration** model with a **temporary password** so the first login forces a secure change—balancing ops speed with security.

---

## 📈 Process & Trade-offs

- **Time budget**: The brief targeted roughly **6–7 hours** of focused work. I deliberately **avoided crossing that bar** so the solution would stay proportionate to the assignment—not slipping into **overengineering** or “resume-driven development” under time pressure.
- Prioritized a **rock-solid core** over feature bloat within that window.
- **Next steps** (explicitly out of scope for the timebox, but natural follow-ups): deeper refactors, richer assistant behavior, and moving from basic LLM answers to a **RAG**-style inventory-aware flow (**semantic search**, stronger retrieval)—left for a later iteration when there is room to invest.

---

> **Raw Prompt Trail**: Provided in a mail to recruiters, to keep repository clean.

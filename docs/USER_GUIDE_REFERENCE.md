# Hardware Hub — Data reference (hardware & statuses)

Companion to **[USER_GUIDE.md](./USER_GUIDE.md)**. This file describes **what is stored for each device** and **what each status means**, including UI labels.

---

## What counts as “hardware”

A **hardware** row is one tracked asset (laptop, phone, dock, etc.) with inventory and rental fields.

### Core fields (API / database)

| Field                         | Meaning                                                                                                                                    |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| **id**                        | Internal numeric identifier.                                                                                                               |
| **name**                      | Human-readable device name (e.g. “MacBook Pro 14”). **Required.**                                                                          |
| **brand**                     | Manufacturer or brand string. **Required.**                                                                                                |
| **serialNumber**              | Optional serial / asset tag.                                                                                                               |
| **purchaseDate**              | Date the purchase is recorded (`YYYY-MM-DD`). Used for sorting, filters, and **pre-arrival** detection.                                    |
| **status**                    | Lifecycle state — one of the allowed values below (stored in DB). **Required.**                                                            |
| **assignedTo**                | Email of the employee the device is assigned to when **In use**; otherwise usually empty.                                                  |
| **notes**                     | Free-form notes (condition, location hints, etc.).                                                                                         |
| **history** / **historyText** | Text log line(s) for audit trail (e.g. “Created via AI assistant”).                                                                        |
| **preArrival**                | **Computed in the API**, not a separate DB column: `true` when `purchaseDate` is **in the future** — meaning “not yet on site” / on order. |

Seeded imports may also expose **seedId** for traceability; normal UI flows focus on the fields above.

---

## Status values (database)

Stored values are **fixed strings** (see check constraint in the app). The UI may **rename** some for clarity.

| Stored value  | Meaning                                                            |
| ------------- | ------------------------------------------------------------------ |
| **Available** | On site and free to rent (subject to **pre-arrival** — see below). |
| **In Use**    | Currently checked out; `assignedTo` holds the renter’s email.      |
| **Repair**    | Not available for normal rental (service / broken workflow).       |
| **Unknown**   | Placeholder state when classification is unclear.                  |

### “Ordered” (filter + chip)

**Ordered** is **not** a separate value in the database. It is a **view**:

- A row is shown as **Ordered** when **`purchaseDate` is after today** and status is **Available** or **Unknown** — i.e. **pre-arrival / on order**.
- Filters that select **Ordered** apply this rule on the server.
- You **cannot rent** a device until it is on site (pre-arrival blocks rent with a clear error).

So: **future purchase date + Available/Unknown ⇒ UI “Ordered”**; once the date is today or past (and still Available), it behaves like normal stock.

**Why not persist “Ordered” in the DB?** Keeping **Available** (or **Unknown**) plus **purchase date** means **on-site availability follows the calendar automatically**: you can see that the device is already **on-site stock** **from the date alone**. A dedicated stored label would need **a manual or scheduled update on arrival day** to flip from “ordered” to “available” without changing anything else.

---

## API list: filtering & sorting (reference)

`GET /api/hardware` supports query parameters such as:

- **status** — `Available`, `In Use`, `Repair`, `Unknown`, or the virtual filter **`Ordered`** (see above).
- **brand** — exact match.
- **dateFrom** / **dateTo** — purchase date range (`YYYY-MM-DD`).
- **sortBy** — e.g. `name`, `brand`, `serialNumber`, `purchaseDate`, `status`.
- **order** — `asc` or `desc`.
- **page** / **limit** — pagination.

The main Dashboard UI uses a subset of these; integrations can use the full set.

---

## Creating hardware (admin API shape)

`POST /api/admin/hardware` expects JSON with at least **name** and **brand**. Typical body:

- `name`, `brand` (required)
- `status` — one of **`Available`**, **`In Use`**, **`Repair`**, **`Unknown`**
- `purchaseDate` — optional ISO date; if omitted, server may default to today
- `serialNumber`, `assignedTo`, `notes`, `history` — optional

Invalid status or dates return `400` with an error code.

---

## Users & roles

| Role      | Capabilities (high level)                                |
| --------- | -------------------------------------------------------- |
| **user**  | Dashboard, rentals, assistant (as configured).           |
| **admin** | Above + hardware CRUD, user creation, admin-only routes. |

User records include **`mustChangePassword`** so the first login can require a password change after admin provisioning.

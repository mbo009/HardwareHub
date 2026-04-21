# Hardware Hub — User Guide

This guide covers day-to-day use of the web app. For **field definitions and status meanings**, see **[USER_GUIDE_REFERENCE.md](./USER_GUIDE_REFERENCE.md)**.

---

## Who this is for

- **All employees** (@booksy.com) can sign in, browse inventory, rent and return devices, and use the assistant (where enabled).
- **Admins** can additionally manage hardware and create user accounts.

---

## Login

1. Open the app and go to the **Login** page.
2. Enter your **work email** and **password**.
   - Email must be on the **`@booksy.com`** domain (the UI validates this).
3. After a successful login you are taken to the **Dashboard** (hardware list).

If credentials are wrong, you will see a generic “Invalid email or password” message.

---

## “Register” / getting an account

There is **no public self-registration**. New accounts are created by an **administrator**:

1. An admin opens **Admin** and uses **Create user** (or equivalent).
2. They enter the new person’s **`@booksy.com`** email and choose **user** or **admin** role.
3. The system generates a **temporary password** and shows it once to the admin (to pass to the new user securely).
4. On **first login**, the new user may be forced to **change the password** before continuing (password policy applies).

So “registration” here means **admin-created account + first login with a temp password**, not a signup form on the login page.

---

## Hardware list (Dashboard)

The main table shows company devices: name, brand, purchase date (shown as “Date added” in the UI), status, and actions.

- Use **Prev** / **Next** at the bottom to move between **pages** (fixed page size).
- Default ordering is **by device name (A→Z)**; server-side filtering keeps performance predictable on large catalogs.

### Filtering

Use the filter row above the table:

| Control       | What it does                                                                                               |
| ------------- | ---------------------------------------------------------------------------------------------------------- |
| **Status**    | Narrow by availability / lifecycle (includes **Ordered** and **Rented** as UI labels — see reference doc). |
| **Brand**     | Exact match on manufacturer / brand string.                                                                |
| **From / To** | Filter by **purchase date** range (inclusive).                                                             |
| **Reset**     | Clears filters and returns to page 1.                                                                      |

Changing a filter resets pagination to page 1 where applicable.

### Sorting

The dashboard list is loaded with a **fixed sort** (by name ascending) in the current UI. The API also supports other `sortBy` / `order` values for integrations; the reference doc lists sortable fields.

---

## Renting and returning

### Rent

- **Rent** is available when the device is **on site and available**: status in the UI allows it, and the item is **not** treated as **pre-arrival / ordered** (future purchase date).
- Click **Rent** on that row. The device moves to **In use** (shown as **Rented** in the UI) and is tied to your account.

If rent fails:

| Situation                    | Typical message / cause                     |
| ---------------------------- | ------------------------------------------- |
| Not available                | “This device is not available to rent.”     |
| Still on order / not arrived | “This device is not on site yet (ordered).” |

### Return

- **Return** appears when **you** are the one who rented it (your email matches the assignment) and status is **In use**.
- Click **Return** to set the device back to **Available** (when allowed by business rules).

If return fails (e.g. not your rental), you may see “You can only return your own rentals.”

### My rentals

Use **My rentals** in the app shell to see hardware **assigned to you**, with similar filters (status, brand, dates) focused on your items.

---

## Adding and editing devices (admins)

Admins manage inventory from the **Admin** area:

- **Add** new hardware with required **name** and **brand**, optional **serial number**, **purchase date**, **status**, **notes**, **history**, etc.
- **Edit** or **remove** rows according to permissions; deletes may be blocked if the device is not in a deletable state (e.g. still **In use**).

Exact JSON fields and valid status **values** are listed in **[USER_GUIDE_REFERENCE.md](./USER_GUIDE_REFERENCE.md)**.

---

## AI assistant (optional)

If enabled in your deployment, the floating assistant can help with inventory questions and suggest actions. It uses the same login session as the rest of the app. Behavior depends on configured LLM backend (local Ollama, cloud APIs, etc.).

---

## Related documents

- **[USER_GUIDE_REFERENCE.md](./USER_GUIDE_REFERENCE.md)** — Hardware fields & status reference
- **[README.md](../README.md)** — Setup and architecture overview
- **[AI_LOG.md](./AI_LOG.md)** — Development notes

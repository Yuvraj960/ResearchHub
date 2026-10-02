# ResearchHub

> A collaborative platform for academic research teams — manage projects, papers, tasks, milestones, references, and team members with real-time notifications.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
  - [Docker (Full Stack)](#docker-full-stack)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Database Models](#database-models)
- [Architecture Notes](#architecture-notes)
- [Background Jobs (Celery)](#background-jobs-celery)
- [Real-time (WebSockets)](#real-time-websockets)
- [Known Limitations](#known-limitations)

---

## Overview

ResearchHub is a full-stack web application that helps academic research teams collaborate on projects. Each project has its own workspace containing:

- A **Kanban task board** (TODO → IN_PROGRESS → REVIEW → COMPLETED)
- **Paper management** with version history (content stored as base64-encoded text)
- **Members** with role-based access (Owner / Researcher)
- **Milestones** to track goals and deadlines
- **References / Bibliography** per project
- **Real-time push notifications** via WebSockets
- **Automated email reminders** via Celery background jobs (deadline alerts, weekly digests)

---

## Features

| Feature | Description |
|---------|-------------|
| **Authentication** | Token-based auth (Flask-Security-Too). No sessions — stateless JWT-style tokens. |
| **Projects** | Create, manage, and archive research projects. Stats (tasks, papers, members, progress %) on the detail page. |
| **Tasks** | Full Kanban board with drag-and-drop. Priority levels: LOW / MEDIUM / HIGH / CRITICAL. |
| **Papers** | Create papers (DRAFT → REVIEW → SUBMITTED → PUBLISHED) with versioned text content. |
| **Version History** | Each paper version stores a full copy of the content (base64-encoded) with a change summary. |
| **Members** | Invite collaborators by email. Two roles: OWNER (full access) and RESEARCHER. |
| **Milestones** | Set goals with deadlines, toggle PENDING / ACHIEVED. |
| **References** | Add bibliography entries with title, authors, year, DOI/URL, and notes. |
| **Notifications** | Real-time push via WebSocket + paginated history list. Mark individual or all as read. |
| **Email** | SMTP emails via Flask-Mail: deadline reminders (daily), weekly project digests, report-ready alerts. |
| **Reports** | Trigger async text-based project reports. Download when ready. |
| **Admin** | Admin panel showing system-wide user and project statistics. |

---

## Tech Stack

### Backend

| Library | Version | Purpose |
|---------|---------|---------|
| Flask | 3.0.3 | Web framework |
| Flask-SQLAlchemy | 3.1.1 | ORM |
| Flask-Migrate | 4.0.7 | Database migrations |
| Flask-Security-Too | 5.4.3 | Token authentication & password hashing |
| Flask-SocketIO | 5.3.6 | WebSocket server |
| Flask-Mail | 0.10.0 | SMTP email delivery |
| Flask-CORS | 4.0.1 | Cross-origin resource sharing |
| Celery | 5.4.0 | Async background task queue |
| Redis | 5.0.7 | Celery broker + result backend |
| Eventlet | 0.36.1 | Async worker for Flask-SocketIO |
| SQLAlchemy | 2.0.31 | SQL toolkit |
| Bcrypt | 4.1.3 | Password hashing |
| Passlib | 1.7.4 | Password utilities (with Python 3.12 shim) |
| Psycopg2-binary | 2.9.9 | PostgreSQL driver |
| python-dotenv | 1.0.1 | `.env` file loading |

### Frontend

| Library | Version | Purpose |
|---------|---------|---------|
| Vue 3 | ^3.4.0 | UI framework (Composition API + `<script setup>`) |
| Vue Router | ^4.3.0 | Client-side routing with navigation guards |
| Pinia | ^2.1.7 | State management |
| Axios | ^1.7.2 | HTTP client with request/response interceptors |
| Socket.io-client | ^4.7.5 | WebSocket client |
| Lucide-vue-next | ^0.378.0 | Icon library |
| Tailwind CSS | ^3.4.4 | Utility-first CSS |
| Vite | ^5.3.1 | Build tool and dev server |

---

## Project Structure

```
ResearchHub/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # App factory — registers blueprints, CORS, SocketIO
│   │   ├── config.py            # All configuration (DB, security, mail, Celery)
│   │   ├── extensions.py        # Flask extension instances (db, socketio, mail, etc.)
│   │   │
│   │   ├── models/              # SQLAlchemy ORM models
│   │   │   ├── user.py          # User + Role (Flask-Security-Too compatible)
│   │   │   ├── project.py       # ResearchProject + ProjectMember
│   │   │   ├── paper.py         # ResearchPaper + PaperVersion
│   │   │   ├── task.py          # Task (Kanban)
│   │   │   ├── milestone.py     # Milestone
│   │   │   ├── reference.py     # Reference / Bibliography entry
│   │   │   ├── comment.py       # Comment (on tasks or papers)
│   │   │   └── notification.py  # Notification
│   │   │
│   │   ├── api/                 # REST API blueprints
│   │   │   ├── auth.py          # /api/auth — register, login, logout, me
│   │   │   ├── projects.py      # /api/projects
│   │   │   ├── members.py       # /api/projects/<id>/members
│   │   │   ├── tasks.py         # /api/projects/<id>/tasks + /api/tasks/<id>
│   │   │   ├── papers.py        # /api/projects/<id>/papers + /api/papers/<id>
│   │   │   ├── versions.py      # /api/papers/<id>/versions + /api/versions/<id>
│   │   │   ├── milestones.py    # /api/projects/<id>/milestones + /api/milestones/<id>
│   │   │   ├── references.py    # /api/projects/<id>/references + /api/references/<id>
│   │   │   ├── comments.py      # /api/tasks/<id>/comments + /api/papers/<id>/comments
│   │   │   ├── notifications.py # /api/notifications
│   │   │   ├── reports.py       # /api/projects/<id>/report
│   │   │   └── admin.py         # /api/admin
│   │   │
│   │   ├── sockets/
│   │   │   └── events.py        # WebSocket event handlers (join_user_room, etc.)
│   │   │
│   │   ├── tasks_celery/        # Celery background tasks
│   │   │   ├── deadline.py      # Daily: check tasks/milestones near deadline → email + notify
│   │   │   ├── weekly.py        # Monday: send weekly project digest emails
│   │   │   └── reports.py       # On-demand: generate text report, cache in Redis
│   │   │
│   │   └── utils/
│   │       ├── decorators.py    # @project_member_required, @project_owner_required
│   │       └── helpers.py       # Shared helper functions
│   │
│   ├── compat.py                # Python 3.12 passlib/pkg_resources shim (MUST load first)
│   ├── run.py                   # Dev server entry point (imports compat first)
│   ├── celery_worker.py         # Celery worker + Beat schedule configuration
│   ├── Dockerfile               # Backend Docker image
│   ├── requirements.txt         # Python dependencies
│   └── .env.example             # Environment variable template
│
├── frontend/
│   └── src/
│       ├── App.vue              # Root component — session restore, toast overlay
│       ├── main.js              # Vue app bootstrap
│       │
│       ├── api/
│       │   ├── axios.js         # Axios instance: base URL, auth interceptor, 401 handler
│       │   └── index.js         # All API call functions grouped by resource
│       │
│       ├── router/
│       │   └── index.js         # Routes + navigation guards (requiresAuth, guest, adminOnly)
│       │
│       ├── stores/              # Pinia state stores
│       │   ├── auth.js          # User session, login, register, logout, fetchMe
│       │   ├── projects.js      # Project list + current project
│       │   ├── tasks.js         # Task list + CRUD
│       │   ├── papers.js        # Paper list + CRUD + versions
│       │   └── notifications.js # Notification list, unread count, WebSocket listener
│       │
│       ├── socket/
│       │   └── index.js         # socket.io-client connect/disconnect helpers
│       │
│       ├── composables/
│       │   └── useToast.js      # Global toast notification composable
│       │
│       ├── components/
│       │   ├── layout/
│       │   │   ├── AppLayout.vue    # Page shell: sidebar + navbar + <slot>
│       │   │   ├── AppSidebar.vue   # Left navigation sidebar
│       │   │   └── AppNavbar.vue    # Top bar: breadcrumb, bell, avatar dropdown
│       │   └── common/
│       │       ├── BaseModal.vue        # Reusable modal dialog (ESC to close)
│       │       └── ToastNotification.vue # Bottom-right toast stack
│       │
│       └── views/               # One Vue component per route
│           ├── LandingView.vue
│           ├── LoginView.vue
│           ├── RegisterView.vue
│           ├── DashboardView.vue
│           ├── ProjectsView.vue
│           ├── ProjectDetailView.vue
│           ├── TasksView.vue         # Kanban board with drag-and-drop
│           ├── PapersView.vue
│           ├── PaperDetailView.vue   # Versions history + add version
│           ├── MembersView.vue
│           ├── MilestonesView.vue
│           ├── ReferencesView.vue
│           ├── NotificationsView.vue
│           ├── ProfileView.vue
│           └── AdminView.vue
│
├── docker-compose.yml           # 6-service stack: redis, postgres, backend, celery-worker, celery-beat, frontend
└── .env.example                 # Root environment variable template
```

---

## Getting Started

### Prerequisites

- **Python 3.12** (tested; other 3.x versions may need the compat shim adjustment)
- **Node.js 18+** and **npm**
- **Redis** (required for Celery background jobs; optional for basic REST API use)
- **Git**

### Backend Setup

```bash
cd backend

# 1. Create and activate a virtual environment
python -m venv venv

# Windows
.\venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env       # Linux/macOS
copy .env.example .env     # Windows

# Edit .env — at minimum set MAIL_USERNAME and MAIL_PASSWORD
# All other defaults work for local development

# 4. Start the development server
# The database (SQLite) is auto-created on first run
python run.py
```

Backend runs at **http://localhost:5000**

> **Note:** `compat.py` is automatically imported by `run.py` before all other imports. This is required on Python 3.12 because `passlib` depends on `pkg_resources` which was removed from the standard library.

### Frontend Setup

```bash
cd frontend

# 1. Install dependencies
npm install

# 2. Start the development server
npm run dev
```

Frontend runs at **http://localhost:3000**

> **No `.env` file needed for local development.** Vite's dev server proxy automatically forwards `/api` and `/socket.io` requests to the backend at `http://localhost:5000`, so there are no CORS issues.

### Docker (Full Stack)

Runs the complete stack with PostgreSQL, Redis, Celery worker, Celery beat scheduler, and an Nginx-served frontend.

```bash
# From the project root
cp .env.example .env     # then fill in credentials
docker compose up --build
```

| Service | URL |
|---------|-----|
| Frontend (Nginx) | http://localhost:80 |
| Backend API | http://localhost:5000 |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

### Running Celery (Local)

Open two extra terminals (with the venv activated):

```bash
# Worker — processes background tasks
celery -A celery_worker.celery worker --loglevel=info

# Beat scheduler — fires scheduled tasks (deadline check, weekly digest)
celery -A celery_worker.celery beat --loglevel=info
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in the values below.

### Backend (`backend/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `dev-secret-change-in-production` | Flask secret key — **change in production** |
| `SECURITY_PASSWORD_SALT` | `super-secret-salt` | Salt for password hashing — **change in production** |
| `DATABASE_URL` | `sqlite:///researchhub.db` | SQLAlchemy connection string. Use `postgresql://user:pass@host/db` for Postgres |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis URL for Celery broker and result backend |
| `MAIL_SERVER` | `smtp.gmail.com` | SMTP server hostname |
| `MAIL_PORT` | `587` | SMTP port |
| `MAIL_USERNAME` | *(required for email)* | Your SMTP email address |
| `MAIL_PASSWORD` | *(required for email)* | SMTP password or app password |
| `MAIL_DEFAULT_SENDER` | *(required for email)* | From address in outgoing emails |
| `FRONTEND_URL` | `*` | Allowed CORS origin. Set to `https://yourdomain.com` in production |

> **Gmail tip:** Use a [Google App Password](https://support.google.com/accounts/answer/185833) — not your main Google account password. Enable 2-step verification first, then generate an app-specific password under Security → App passwords.

### Frontend (no `.env` needed in development)

Only needed for production deployments:

| Variable | Description |
|----------|-------------|
| `VITE_API_URL` | Backend API base URL, e.g. `https://api.yourdomain.com/api` |
| `VITE_SOCKET_URL` | Backend socket URL, e.g. `https://api.yourdomain.com` |

---

## API Reference

All endpoints return JSON in the format:
```json
{ "message": "Human-readable status", "data": { ... } }
```
Error responses:
```json
{ "error": "Error description" }
```

Authentication is via the `Authorization` header with the raw token (no `Bearer` prefix):
```
Authorization: <your-token>
```

### Auth — `/api/auth`

| Method | Path | Auth | Body | Description |
|--------|------|------|------|-------------|
| `POST` | `/register` | ❌ | `{email, username, password, first_name, last_name}` | Create account. Returns `{user, token}`. |
| `POST` | `/login` | ❌ | `{email, password}` | Sign in. Returns `{user, token}`. |
| `POST` | `/logout` | ✅ | — | Invalidate session. |
| `GET` | `/me` | ✅ | — | Get current user profile. |
| `PUT` | `/me` | ✅ | `{first_name?, last_name?, username?}` | Update profile. |

### Projects — `/api/projects`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/` | ✅ | Create project. Creator is auto-added as OWNER. Body: `{title, field?, description?}` |
| `GET` | `/` | ✅ | List all projects where the current user is a member. |
| `GET` | `/<id>` | ✅ | Project detail including stats: `{task_count, paper_count, member_count, progress}` |
| `PUT` | `/<id>` | ✅ Owner | Update project fields. |
| `DELETE` | `/<id>` | ✅ Owner | Delete project and all related data. |

### Members — `/api/projects/<project_id>/members`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/` | ✅ Owner | Invite member by email. Body: `{user_email, role}`. Role: `RESEARCHER` or `OWNER`. |
| `GET` | `/` | ✅ Member | List all project members. |
| `PUT` | `/<user_id>` | ✅ Owner | Update member role. |
| `DELETE` | `/<user_id>` | ✅ Owner | Remove member from project. |

### Tasks — `/api/projects/<id>/tasks` + `/api/tasks/<id>`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/projects/<id>/tasks` | ✅ Member | Create task. Body: `{title, description?, priority?, deadline?, assigned_to?}` |
| `GET` | `/api/projects/<id>/tasks` | ✅ Member | List tasks. Query: `?status=TODO&assigned_to=<user_id>` |
| `GET` | `/api/tasks/<id>` | ✅ Member | Task detail. |
| `PUT` | `/api/tasks/<id>` | ✅ Member | Update task. Statuses: `TODO`, `IN_PROGRESS`, `REVIEW`, `COMPLETED`. |
| `DELETE` | `/api/tasks/<id>` | ✅ Member | Delete task. |

### Papers — `/api/projects/<id>/papers` + `/api/papers/<id>`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/projects/<id>/papers` | ✅ Member | Create paper. Body: `{title, abstract?}` |
| `GET` | `/api/projects/<id>/papers` | ✅ Member | List papers. |
| `GET` | `/api/papers/<id>` | ✅ Member | Paper detail. |
| `PUT` | `/api/papers/<id>` | ✅ Member | Update paper. Statuses: `DRAFT`, `REVIEW`, `SUBMITTED`, `PUBLISHED`. |
| `DELETE` | `/api/papers/<id>` | ✅ Member | Delete paper and all versions. |

### Versions — `/api/papers/<id>/versions` + `/api/versions/<id>`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/papers/<id>/versions` | ✅ Member | Add version. Body: `{content, change_summary?}`. Content stored as base64. |
| `GET` | `/api/papers/<id>/versions` | ✅ Member | List all versions (content decoded from base64 in response). |
| `GET` | `/api/versions/<id>` | ✅ Member | Single version detail. |

### Milestones — `/api/projects/<id>/milestones` + `/api/milestones/<id>`

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/projects/<id>/milestones` | Create milestone. Body: `{title, description?, due_date}` |
| `GET` | `/api/projects/<id>/milestones` | List milestones. |
| `PUT` | `/api/milestones/<id>` | Update (e.g. toggle status: `PENDING` / `ACHIEVED`). |
| `DELETE` | `/api/milestones/<id>` | Delete milestone. |

### References — `/api/projects/<id>/references` + `/api/references/<id>`

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/projects/<id>/references` | Add reference. Body: `{title, authors, year, doi?, url?, notes?}` |
| `GET` | `/api/projects/<id>/references` | List references. |
| `PUT` | `/api/references/<id>` | Update reference. |
| `DELETE` | `/api/references/<id>` | Delete reference. |

### Comments

| Method | Path | Description |
|--------|------|-------------|
| `POST` / `GET` | `/api/tasks/<id>/comments` | Comments on a task. |
| `POST` / `GET` | `/api/papers/<id>/comments` | Comments on a paper. |
| `DELETE` | `/api/comments/<id>` | Delete comment (author only). |

### Notifications — `/api/notifications`

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Paginated notifications. Response: `{items, total, pages, page}` |
| `GET` | `/unread-count` | Returns `{count: N}` |
| `PUT` | `/<id>/read` | Mark one notification as read. |
| `PUT` | `/read-all` | Mark all notifications as read. |

### Reports — `/api/projects/<id>/report`

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/` | Trigger async report generation. Returns a Celery `task_id`. |
| `GET` | `/status/<task_id>` | Check generation status. |
| `GET` | `/download/<task_id>` | Download the generated report text. |

### Admin — `/api/admin` *(admin role required)*

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/stats` | System-wide user and project counts. |
| `GET` | `/users` | List all users with profile data. |
| `PUT` | `/users/<id>` | Update a user's active status or role. |
| `DELETE` | `/users/<id>` | Delete a user account. |

---

## Database Models

### User
```
id, email (unique), username (unique), password (hashed),
first_name, last_name, active, confirmed_at,
fs_uniquifier,  ← required by Flask-Security-Too for token generation
last_login_at, current_login_at, last_login_ip, current_login_ip, login_count,
created_at
```

### ResearchProject
```
id, owner_id → User, title, description, field,
status: ACTIVE | COMPLETED | ARCHIVED,
created_at, updated_at
```

### ProjectMember
```
id, project_id → ResearchProject, user_id → User,
role: RESEARCHER | OWNER,
joined_at
```

### ResearchPaper
```
id, project_id → ResearchProject, title, abstract,
status: DRAFT | REVIEW | SUBMITTED | PUBLISHED,
created_at, updated_at
```

### PaperVersion
```
id, paper_id → ResearchPaper, version_number (auto-increment per paper),
created_by → User, content (TEXT, base64-encoded),
change_summary, created_at
```

### Task
```
id, project_id → ResearchProject, assigned_to → User (nullable),
title, description, priority: LOW | MEDIUM | HIGH | CRITICAL,
deadline (nullable), status: TODO | IN_PROGRESS | REVIEW | COMPLETED,
created_at, updated_at
```

### Milestone
```
id, project_id → ResearchProject,
title, description, due_date,
status: PENDING | ACHIEVED,
created_at
```

### Reference
```
id, project_id → ResearchProject, added_by → User,
title, authors, year, journal, doi, url, notes,
created_at
```

### Comment
```
id, author_id → User, content, created_at,
task_id → Task (nullable),
paper_id → ResearchPaper (nullable)
```

### Notification
```
id, user_id → User, message,
type: DEADLINE | TASK_ASSIGNED | COMMENT | PAPER_VERSION | SYSTEM,
is_read (default False), link, created_at
```

---

## Architecture Notes

### Authentication Flow
1. Client sends `POST /api/auth/login` with `{email, password}`
2. Backend verifies password with bcrypt, returns a Flask-Security-Too HMAC token
3. Client stores token in `localStorage['rh_token']`
4. Every subsequent request includes `Authorization: <token>` header
5. Backend validates via `@auth_required('token')` decorator (Flask-Security-Too)

> **Important:** The token is sent as a raw value — not as `Bearer <token>`. Flask-Security-Too is configured with `SECURITY_TOKEN_AUTHENTICATION_HEADER = 'Authorization'`.

### CORS & Dev Proxy
In development, Vite proxies all requests:
- `/api/*` → `http://localhost:5000/api/*`
- `/socket.io/*` → `http://localhost:5000/socket.io/*` (with WebSocket upgrade)

This means the **browser never makes cross-origin requests** in development — no CORS issues at all. The backend still has `Flask-CORS` configured for production deployments where the frontend is served from a different domain.

### Flask-Security-Too Isolation
Flask-Security-Too is configured to keep its own views completely separate from the custom `/api/auth/*` blueprint:
```python
SECURITY_BLUEPRINT_NAME = '_fst_internal'
SECURITY_URL_PREFIX = '/_fst'
```
This moves FST's login/register views to `/_fst/login` etc., preventing any route conflicts. User creation in `/api/auth/register` is done directly via SQLAlchemy (bypassing FST's register view entirely) to ensure the correct JSON response format is returned.

### Python 3.12 Compatibility
`passlib 1.7.x` uses `pkg_resources` which was removed from Python 3.12's standard venv. A compatibility shim in [`compat.py`](backend/compat.py) patches `sys.modules['pkg_resources']` with a minimal `importlib.metadata`-based replacement **before any Flask or Security imports run**. Both `run.py` and `celery_worker.py` import `compat` as their very first line.

---

## Background Jobs (Celery)

Celery connects to Redis as both the broker and result backend.

### Scheduled Tasks (Beat)

| Task | Schedule | Description |
|------|----------|-------------|
| `deadline.check_deadlines` | Daily at 08:00 | Finds tasks and milestones due within 48 hours. Sends email + WebSocket notification to assigned users. |
| `weekly.send_weekly_digest` | Monday at 09:00 | Sends each project owner a digest of the past week: completed tasks, pending tasks, upcoming milestones, new paper versions. |

### On-Demand Tasks

| Task | Trigger | Description |
|------|---------|-------------|
| `reports.generate_report` | `POST /api/projects/<id>/report/` | Builds a plain-text project report. Stores in Redis. Notifies user via WebSocket when ready. |

### Starting Workers

```bash
# Activate venv first
celery -A celery_worker.celery worker --loglevel=info
celery -A celery_worker.celery beat --loglevel=info
```

---

## Real-time (WebSockets)

Built with **Flask-SocketIO** (server) and **socket.io-client** (browser).

### Connection Flow
1. After login, `connectSocket(userId)` is called from the auth store
2. Client connects to the same origin (proxied to `http://localhost:5000` in dev)
3. On connect, client emits `join_user_room` with `{user_id}`
4. Server adds the socket to room `user_<id>`

### Events

| Event | Direction | Payload | Description |
|-------|-----------|---------|-------------|
| `join_user_room` | Client → Server | `{user_id}` | Join the personal notification room |
| `new_notification` | Server → Client | `{id, message, type, is_read, link, created_at}` | Pushed when a new notification is created for the user |

Notifications are stored in the database **and** pushed live. If the user is offline when a notification is generated, they will see it in the `/notifications` page on next load.

---

## Known Limitations

- **No file upload support** — Paper versions store plain text only (base64-encoded). Binary files (PDFs, Word docs) are not supported in this version.
- **No email confirmation** — Registration does not require email verification (`SECURITY_CONFIRMABLE = False`). Users are active immediately.
- **SQLite in development** — SQLite has limited concurrency. Celery workers + the dev server running simultaneously may occasionally lock the database. Switch to PostgreSQL if you run Celery locally.
- **Redis is required for Celery** — If Redis is not running, the Celery tasks will fail silently. The REST API and WebSockets work without Redis.
- **No password reset** — `SECURITY_RECOVERABLE = False`. Password change must be done by an admin or by direct database access.
- **Single tenant** — All users share the same application instance. There is no workspace isolation beyond project-level membership.

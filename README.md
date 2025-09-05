
# HW-13. The Contacts Service API (FastAPI)

## Overview
This project is a REST API for managing contacts with user authentication and email verification.  
Built with **FastAPI**, **PostgreSQL**, **SQLAlchemy (async)**, **Alembic**, **Redis**, and **Docker Compose**.  
It supports registration, login, email verification, password reset, JWT authentication, and contact CRUD operations.  

---

## 🛠 Features
- **User authentication** with JWT (access + refresh tokens).
- **Email verification** after signup.
- **Password reset** via email link with token.
- **CORS enabled** for frontend integration.
- **Avatar upload to Cloudinary** (optional, if configured).
- **CRUD for contacts**:
   Create / Read / Update / Delete
   Search contacts
   Upcoming birthdays
- **Environment variables** stored in `.env`.
- **Docker Compose** to run app + PostgreSQL + Redis.

---

## Project structure
```
goit-web-hw-13/
├─ .env                     # environment variables (DB URL, JWT secret, SMTP, admin credentials)
├─ .env.example             # example env file
├─ .gitignore
├─ alembic.ini              # Alembic configuration
├─ docker-compose.yml       # services: Postgres, Redis, PgAdmin, Jenkins
├─ poetry.lock
├─ pyproject.toml
├─ README.md
│
├─ main.py                  # FastAPI entrypoint (lifespan, middlewares, routers)
├─ seed.py                  # script to create initial admin user
├─ parse_jwt.py             # standalone JWT parser (dev/debug tool)
├─ check_smtp.py            # SMTP debug script
│
├─ migrations/              # Alembic migrations
│   ├─ env.py
│   └─ versions/...
│
├── postman/             
│   └── HW_13_Smoke_Tests.postman_collection.json
│
└─ src/
    ├─ conf/
    │   └─ config.py        # global settings (DATABASE_URL, SECRET_KEY, SMTP, DEBUG_EMAILS, etc.)
    │
    ├─ core/
    │   └─ error_handlers.py  # global error handlers (422, 404, 409, 500)
    │
    ├─ database/
    │   ├─ db.py            # async engine/session, get_db dependency
    │   └─ models.py        # SQLAlchemy ORM models (User, Contact)
    │
    ├─ repository/
    │   ├─ contacts.py      # DB operations for contacts (CRUD, search, birthdays)
    │   └─ users.py         # DB operations for users (create, roles, tokens, list)
    │
    ├─ routes/
    │   ├─ auth.py          # /api/auth (signup, login, refresh, reset password)
    │   ├─ contacts.py      # /api/contacts (CRUD, search, birthdays)
    │   ├─ health.py        # /api/health (readiness, liveness probes)
    │   ├─ users.py         # /api/users (admin-only endpoints)
    │   └─ debug.py         # /debug (send test email, list routes)
    │
    ├─ services/
    │   ├─templates/           # email templates (html)
    │   │   ├─ email_template.html
    │   │   └─ reset_password_template.html
    │   │
    │   ├─ auth.py          # password hashing, JWT utils, current_user dependency
    │   ├─ cache.py         # Redis helpers
    │   ├─ email.py         # SMTP via FastMail, saving emails to tmp_emails (DEBUG_EMAILS)
    │   ├─ permissions.py   # RoleAccess dependency for RBAC
    │   └─ storage.py       # cloudinary/file storage utils
    │   
    │
    ├─ static/              # static files (avatars, images, etc.)
    │
    ├─ schemas.py       # Pydantic models (UserModel, ContactModel, TokenModel, etc.)
    │
    ├─ tmp_emails/          # saved emails if DEBUG_EMAILS=True
    │   └─ __init__.py
    │
    └─ middleware.py        # custom middlewares (process-time, CORS, logging)

```
---

## Run with Docker
```bash
docker-compose up --build
```
API will be available at: **http://127.0.0.1:8000**

Docs:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

---

## Authentication flow
1. **Signup** → `/api/auth/signup`  
   User receives confirmation email.
2. **Confirm email** → `/api/auth/confirmed_email/{token}`
3. **Login** → `/api/auth/login`  
   Returns `access_token` and `refresh_token`.
4. **Access protected routes** using header:  
   ```
   Authorization: Bearer <access_token>
   ```
5. **Refresh token** → `/api/auth/refresh_token`
6. **Reset password**:  
   - Request: `/api/auth/request_reset_password`
   - Apply: `/api/auth/reset_password/{token}`

---

## Email templates
Located in `src/services/templates/`:
- `email_template.html` – confirmation
- `reset_password_template.html` – password reset

Emails are sent via SMTP.  
Fallback saves emails into `/tmp_emails/`.

---

## Contacts API
### Create contact
`POST /api/contacts/`
```json
{
  "first_name": "John",
  "last_name": "Smith",
  "email": "john@example.com",
  "phone": "+380991112233",
  "birthday": "1990-05-10",
  "extra": "friend"
}
```

### Get all contacts
`GET /api/contacts/`

### Search
`GET /api/contacts/search?query=John`

### Upcoming birthdays
`GET /api/contacts/birthdays`

### Update contact
`PUT /api/contacts/{id}`

### Delete contact
`DELETE /api/contacts/{id}`

---

## Testing
Use Postman collection or Swagger UI.  
Check:
- Signup & confirm
- Login
- Reset password
- Contact CRUD
- Error cases (401, 404, expired token)

---

## Tech stack
- Python 3.11+
- FastAPI
- SQLAlchemy (async) + Alembic
- PostgreSQL
- Redis
- Docker / Docker Compose
- FastAPI-Mail
- Cloudinary SDK (optional)

---

## License

MIT (or your choice). Educational use encouraged.
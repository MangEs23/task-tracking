# Project Management API

Backend API untuk sistem manajemen project (mirip Jira / Linear sederhana) menggunakan **FastAPI + PostgreSQL + Docker**.

## Tech Stack

- **FastAPI** - Web framework
- **PostgreSQL** - Database
- **SQLAlchemy 2.0** - ORM
- **Docker & Docker Compose** - Containerization
- **JWT** - Authentication
- **Pydantic** - Data validation

## Project Structure

```text
.
├── app/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── database.py          # Database connection & session
│   ├── models.py             # SQLAlchemy models
│   ├── schemas.py            # Pydantic schemas
│   ├── security.py           # Password hashing & JWT
│   ├── dependencies.py
│   └── routers/
│       ├── __init__.py
│       └── auth.py           # Register & Login
├── .env
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Database Schema

```mermaid
erDiagram
    USER ||--o{ PROJECT_MEMBER : has
    PROJECT ||--o{ PROJECT_MEMBER : has
    PROJECT ||--o{ EPIC : contains
    PROJECT ||--o{ STATUS : defines
    EPIC ||--o{ TASK : contains
    STATUS ||--o{ TASK : "assigned to"
    TASK ||--o{ TASK_ASSIGNEE : has
    USER ||--o{ TASK_ASSIGNEE : "assigned via"

    USER {
        uuid id PK
        string name
        string email
        string password_hash
        string role "admin/member"
        datetime created_at
    }

    PROJECT {
        uuid id PK
        string name
        string description
        uuid created_by FK
        datetime created_at
    }

    PROJECT_MEMBER {
        uuid id PK
        uuid project_id FK
        uuid user_id FK
        string role "admin/member"
    }

    EPIC {
        uuid id PK
        uuid project_id FK
        string title
        string description
        datetime start_date
        datetime end_date
        datetime created_at
    }

    STATUS {
        uuid id PK
        uuid project_id FK
        string name
        int order
        boolean is_default
    }

    TASK {
        uuid id PK
        uuid epic_id FK
        uuid status_id FK
        string title
        string description
        string priority
        datetime due_date
        datetime created_at
    }

    TASK_ASSIGNEE {
        uuid id PK
        uuid task_id FK
        uuid user_id FK
    }
```

### Keterangan Relasi

| Relasi | Keterangan |
|---|---|
| USER → PROJECT_MEMBER | Satu user bisa menjadi member di banyak project |
| PROJECT → PROJECT_MEMBER | Satu project punya banyak member |
| PROJECT → EPIC | Satu project punya banyak epic |
| PROJECT → STATUS | Setiap project punya status sendiri (Todo, In Progress, dll) |
| EPIC → TASK | Satu epic berisi banyak task |
| STATUS → TASK | Setiap task punya satu status |
| TASK → TASK_ASSIGNEE | Satu task bisa di-assign ke banyak user |
| USER → TASK_ASSIGNEE | Satu user bisa di-assign ke banyak task |

## Prerequisites

- Docker Desktop
- Git

Tidak perlu install Python / PostgreSQL di local. Semua berjalan di dalam Docker.

## Getting Started

### 1. Clone repository

```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Setup environment variables

Buat file `.env` di root project:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password123
POSTGRES_DB=app_db
DATABASE_URL=postgresql://postgres:password123@db:5432/app_db

SECRET_KEY=ganti-dengan-secret-key-yang-panjang-dan-random-minimal-32-karakter
```

### 3. Jalankan project

```bash
docker compose up --build
```

API akan berjalan di: `http://localhost:8000`
Dokumentasi interaktif (Swagger UI): `http://localhost:8000/docs`

## Development

### Menjalankan ulang setelah perubahan code

Karena volume sudah di-mount, perubahan code biasanya langsung terdeteksi (hot reload).

Kalau ada perubahan dependency, jalankan ulang:

```bash
docker compose up --build
```

### Stop container

```bash
docker compose down
```

### Stop + hapus data database

```bash
docker compose down -v
```
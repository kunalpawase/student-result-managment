# Student Result Management System — Architecture & Implementation

## Architecture Overview

```
Internet / Browser
       │
       ▼ :80
 ┌─────────────┐
 │    Nginx    │  ← Reverse Proxy (frontend_network)
 │  (alpine)   │
 └──────┬──────┘
        │ proxy_pass :5000
        ▼
 ┌─────────────┐
 │    Flask    │  ← App Server (frontend_network + backend_network)
 │ (python:    │
 │  3.10-slim) │
 └──────┬──────┘
        │ mysql-connector :3306
        ▼
 ┌─────────────┐
 │    MySQL    │  ← Database (backend_network only)
 │  (mysql:8)  │
 └─────────────┘
```

---

## 1. Persistent Storage (Volumes & Bind Mounts)

| Volume Name           | Type        | Purpose                        |
|-----------------------|-------------|--------------------------------|
| `student_mysql_data`  | Named       | MySQL data persistence         |
| `student_app_logs`    | Named       | Flask rotating log files       |
| `student_nginx_logs`  | Named       | Nginx access & error logs      |
| `./logs/mysql`        | Bind Mount  | MySQL logs on host             |
| `./nginx/nginx.conf`  | Bind Mount  | Nginx config (read-only)       |

---

## 2. Container Networking

Two isolated bridge networks:

- `student_backend` — MySQL ↔ Flask only (database not exposed to Nginx)
- `student_frontend` — Flask ↔ Nginx only (public-facing traffic)

Flask sits on both networks as the bridge between layers.

---

## 3. Security Practices

- Credentials stored in `.env` file, never hardcoded
- `.env` is in `.gitignore` — `.env.example` committed instead
- Flask runs as non-root user (`appuser`) inside container
- MySQL app user (`app_user`) has only SELECT/INSERT/UPDATE/DELETE — no root access
- Nginx adds security headers: `X-Frame-Options`, `X-Content-Type-Options`, `X-XSS-Protection`
- `SECRET_KEY` loaded from environment variable
- MySQL port 3306 not exposed to host in production (internal only via network)

---

## 4. Image Scanning & Verification

Tool: **Trivy** (by Aqua Security)

```bash
# Local scan
scan.bat

# Manual commands
trivy image student-result-flask:latest          # vulnerability scan
trivy fs --scanners secret .                     # secrets in source code
trivy config .                                   # Dockerfile/Compose misconfigs
```

CI/CD pipeline runs Trivy automatically on every push.

---

## 5. Image Optimization

Multi-stage Dockerfile:

| Stage     | Base Image         | Purpose                          |
|-----------|--------------------|----------------------------------|
| `builder` | `python:3.10-slim` | Install pip dependencies only    |
| `runtime` | `python:3.10-slim` | Copy deps + app, run as non-root |

Benefits:
- `slim` variant ~50% smaller than full `python:3.10`
- Build tools not present in final image
- `--no-cache-dir` prevents pip cache bloat
- Non-root user reduces attack surface

---

## 6. Multi-Container Architecture (Microservices)

Three independent services in Docker Compose:

| Service | Image         | Role                        | Network(s)                    |
|---------|---------------|-----------------------------|-------------------------------|
| mysql   | mysql:8       | Data persistence layer      | backend_network               |
| flask   | custom build  | Business logic / API        | backend + frontend network    |
| nginx   | nginx:alpine  | Reverse proxy / entry point | frontend_network              |

Each service has a single responsibility and communicates only through defined networks.

---

## 7. Logging & Monitoring

**Application Logs (Flask):**
- Python `RotatingFileHandler` → `/app/logs/app.log` (1MB × 3 files)
- Every route access, DB operation, and error is logged with timestamp

**Container Logs:**
- All services use `json-file` driver with `max-size: 10m`, `max-file: 3`
- View with: `docker logs -f flask_app`

**Health Checks:**
- Flask: `/health` endpoint checks DB connectivity
- MySQL: `mysqladmin ping`
- Nginx: depends on Flask health

**Monitoring Commands:**
```bash
logs.bat                          # interactive log viewer menu
docker stats                      # live CPU/memory usage
docker inspect flask_app          # full container metadata
```

---

## 8. CI/CD Integration (GitHub Actions)

Pipeline: `.github/workflows/ci.yml`

```
Push to main
     │
     ▼
Job 1: Build & Lint (flake8)
     │
     ▼
Job 2: Docker Build + Trivy Scan
     │
     ▼
Job 3: Push to Docker Hub (main branch only)
```

Secrets stored in GitHub repository secrets (`DOCKER_USERNAME`, `DOCKER_PASSWORD`).

---

## 9. Running the Project

```bash
# Start all services
docker-compose up --build

# Access points
http://localhost        ← via Nginx (port 80)  [recommended]
http://localhost:5000   ← direct Flask access

# View logs
logs.bat

# Scan images
scan.bat

# Stop
docker-compose down

# Stop and remove volumes (full reset)
docker-compose down -v
```

---

## Project Structure

```
student-result-managment/
├── .github/
│   └── workflows/
│       └── ci.yml              ← CI/CD pipeline
├── nginx/
│   └── nginx.conf              ← Reverse proxy config
├── templates/
│   ├── index.html
│   ├── add_student.html
│   └── view_result.html
├── app.py                      ← Flask application
├── requirements.txt
├── Dockerfile                  ← Multi-stage build
├── docker-compose.yml          ← 3-service orchestration
├── .env                        ← Secrets (not committed)
├── .env.example                ← Template (committed)
├── .gitignore
├── .trivyignore
├── scan.bat                    ← Local image scanning
├── logs.bat                    ← Log viewer utility
└── ARCHITECTURE.md             ← This file
```

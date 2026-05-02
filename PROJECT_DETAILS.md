# 📘 Student Result Management System — Complete Project Details

---

## 📌 Project Overview

| Field            | Details                                      |
|------------------|----------------------------------------------|
| Project Name     | Student Result Management System             |
| Purpose          | Manage student records, results & analytics  |
| Architecture     | 3-tier Microservices (Nginx → Flask → MySQL) |
| Containerization | Docker + Docker Compose                      |
| Language         | Python (Flask), HTML (Jinja2), SQL           |
| Database         | MySQL 8                                      |
| Web Server       | Nginx (Reverse Proxy)                        |
| CI/CD            | GitHub Actions                               |
| Image Scanning   | Trivy (Aqua Security)                        |
| Orchestration    | Docker Swarm + Kubernetes                    |

---

## 🗂️ Complete Project Structure

```
student-result-managment/
│
├── 📄 app.py                        ← Flask application (all routes + logic)
├── 📄 requirements.txt              ← Python dependencies
├── 📄 Dockerfile                    ← Multi-stage Docker build
├── 📄 docker-compose.yml            ← 3-service orchestration
├── 📄 .env                          ← Secret credentials (NOT committed)
├── 📄 .env.example                  ← Credential template (committed)
├── 📄 .gitignore                    ← Git ignore rules
├── 📄 .trivyignore                  ← Trivy scan ignore rules
│
├── 📁 templates/                    ← HTML Jinja2 templates
│   ├── index.html                   ← Home page (navigation)
│   ├── add_student.html             ← Add student form
│   ├── view_result.html             ← Results table + grade pie chart
│   ├── search.html                  ← Search by roll number
│   └── stats.html                   ← Topper + subject avg + bar chart
│
├── 📁 nginx/
│   └── nginx.conf                   ← Reverse proxy configuration
│
├── 📁 logs/
│   └── mysql/                       ← MySQL log bind mount (host folder)
│
├── 📁 swarm/
│   └── docker-stack.yml             ← Docker Swarm stack file
│
├── 📁 k8s/                          ← Kubernetes manifests
│   ├── namespace.yml
│   ├── secret.yml
│   ├── mysql-pvc.yml
│   ├── mysql-deployment.yml
│   ├── flask-deployment.yml
│   ├── nginx-deployment.yml
│   └── flask-hpa.yml
│
├── 📁 .github/workflows/
│   └── ci.yml                       ← GitHub Actions CI/CD pipeline
│
├── 📄 scan.bat                      ← Local Trivy image scan script
├── 📄 logs.bat                      ← Log viewer utility
├── 📄 swarm.bat                     ← Docker Swarm management script
├── 📄 k8s.bat                       ← Kubernetes management script
├── 📄 ARCHITECTURE.md               ← Architecture documentation
└── 📄 PROJECT_DETAILS.md            ← This file
```

---

## 🏗️ System Architecture

```
         Browser / Client
               │
               ▼  Port 80
      ┌─────────────────┐
      │      Nginx      │   ← Reverse Proxy
      │  (nginx:alpine) │   ← Security Headers
      │  frontend_net   │   ← Access Logs
      └────────┬────────┘
               │ proxy_pass :5000
               ▼
      ┌─────────────────┐
      │      Flask      │   ← Business Logic
      │ (python:3.10)   │   ← REST Routes
      │ frontend_net    │   ← Rotating File Logs
      │ + backend_net   │   ← /health endpoint
      └────────┬────────┘
               │ mysql-connector :3306
               ▼
      ┌─────────────────┐
      │      MySQL      │   ← Data Persistence
      │   (mysql:8)     │   ← Named Volume
      │  backend_net    │   ← Health Checked
      └─────────────────┘
```

---

## 🛠️ Technology Stack

### Backend
| Technology              | Version  | Purpose                          |
|-------------------------|----------|----------------------------------|
| Python                  | 3.10     | Core programming language        |
| Flask                   | 3.0.0    | Web framework                    |
| mysql-connector-python  | 8.2.0    | MySQL database driver            |
| Jinja2                  | 3.1.6    | HTML templating engine           |
| Werkzeug                | 3.1.8    | WSGI utility library             |

### Frontend
| Technology  | Purpose                              |
|-------------|--------------------------------------|
| HTML5       | Page structure                       |
| CSS3        | Styling and responsive layout        |
| Chart.js    | Grade pie chart + subject bar chart  |

### Database
| Technology | Version | Purpose                     |
|------------|---------|-----------------------------|
| MySQL      | 8       | Relational data storage      |
| student_db | —       | Application database         |
| results    | —       | Student records table        |

### Infrastructure
| Technology     | Version      | Purpose                          |
|----------------|--------------|----------------------------------|
| Docker         | Latest       | Containerization                 |
| Docker Compose | Latest       | Multi-container orchestration    |
| Nginx          | alpine       | Reverse proxy + security headers |
| Docker Swarm   | Built-in     | Container cluster management     |
| Kubernetes     | Latest       | Production orchestration + HPA   |

---

## 🗄️ Database Schema

```sql
Database: student_db

Table: results
┌─────────────┬──────────────┬──────────┬─────────────────────────┐
│   Column    │     Type     │ Nullable │       Description        │
├─────────────┼──────────────┼──────────┼─────────────────────────┤
│ id          │ INT          │ NOT NULL │ Primary Key, Auto Inc    │
│ name        │ VARCHAR(255) │ NOT NULL │ Student full name        │
│ roll_number │ VARCHAR(50)  │ NOT NULL │ Unique roll identifier   │
│ subject     │ VARCHAR(100) │ NOT NULL │ Subject name             │
│ marks       │ INT          │ NOT NULL │ Marks obtained (0-100)   │
└─────────────┴──────────────┴──────────┴─────────────────────────┘

Users:
  root      → Full access (used only during init_db)
  app_user  → SELECT, INSERT, UPDATE, DELETE on student_db only
```

---

## 🌐 Application Routes

| Method | Route              | Description                          |
|--------|--------------------|--------------------------------------|
| GET    | `/`                | Home page with navigation            |
| GET    | `/add_student`     | Show add student form                |
| POST   | `/add_student`     | Submit and save student record       |
| GET    | `/view_result`     | All results table + grade pie chart  |
| GET    | `/search`          | Search student by roll number        |
| GET    | `/stats`           | Topper + subject avg + bar chart     |
| POST   | `/delete/<id>`     | Delete a student record by ID        |
| GET    | `/health`          | Health check (DB connectivity check) |

---

## 📊 Grade Logic

| Marks Range | Grade | Color  |
|-------------|-------|--------|
| 90 – 100    | A     | Green  |
| 75 – 89     | B     | Teal   |
| 60 – 74     | C     | Yellow |
| 0  – 59     | D     | Red    |

---

## 🐳 Docker Configuration

### Dockerfile — Multi-Stage Build

```
Stage 1: builder (python:3.10-slim)
  └── Install all pip dependencies

Stage 2: runtime (python:3.10-slim)
  ├── Copy only site-packages from builder
  ├── Install curl (for healthcheck)
  ├── Create non-root user: appuser
  ├── Copy application source
  └── Run as appuser (not root)
```

**Benefits:**
- `slim` base = ~50% smaller than full Python image
- Build tools not present in final image
- Non-root user reduces attack surface
- `--no-cache-dir` prevents pip cache bloat

### Docker Compose Services

| Service     | Image                      | Port  | Role                  |
|-------------|----------------------------|-------|-----------------------|
| mysql       | mysql:8                    | 3306  | Database              |
| flask       | student-result-flask:latest| 5000  | Application server    |
| nginx       | nginx:alpine               | 80    | Reverse proxy         |

### Networks

| Network          | Type   | Connected Services    |
|------------------|--------|-----------------------|
| student_backend  | bridge | mysql ↔ flask         |
| student_frontend | bridge | flask ↔ nginx         |

### Volumes

| Volume Name          | Type        | Mount Path              | Purpose               |
|----------------------|-------------|-------------------------|-----------------------|
| student_mysql_data   | Named       | /var/lib/mysql          | MySQL data persistence|
| student_app_logs     | Named       | /app/logs               | Flask rotating logs   |
| student_nginx_logs   | Named       | /var/log/nginx          | Nginx access/error    |
| ./logs/mysql         | Bind Mount  | /var/log/mysql          | MySQL logs on host    |
| ./nginx/nginx.conf   | Bind Mount  | /etc/nginx/conf.d/      | Nginx config (ro)     |

---

## 📈 Monitoring & Logging

### 1. Application Logging (Flask)

- **Library:** Python `logging` + `RotatingFileHandler`
- **Log file:** `/app/logs/app.log`
- **Rotation:** 1 MB per file, keeps last 3 files
- **Format:** `YYYY-MM-DD HH:MM:SS [LEVEL] message`
- **Output:** Both file and stdout (console)

**What gets logged:**
```
Home page accessed
Student added: Roll=R001 | Subject=Maths | Marks=85
Results page accessed — 10 records returned
Search: 'R001' — 3 results
Record deleted: id=5
Health check: OK
DB connection attempt 1/30 failed: ...
```

### 2. Container Logging (Docker)

All 3 containers use the `json-file` logging driver:

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"    ← rotate after 10MB
    max-file: "3"      ← keep last 3 log files
```

**View logs with:**
```bash
docker logs flask_app              # Flask logs
docker logs mysql_db               # MySQL logs
docker logs nginx_proxy            # Nginx logs
docker logs -f flask_app           # Live streaming
docker-compose logs -f             # All services live
```

### 3. Health Checks

| Service | Health Check Method              | Interval | Retries |
|---------|----------------------------------|----------|---------|
| Flask   | `curl http://localhost:5000/health` | 30s    | 5       |
| MySQL   | `mysqladmin ping`                | 10s      | 10      |
| Nginx   | depends_on flask                 | —        | —       |

**Flask /health endpoint response:**
```json
{ "status": "healthy", "database": "connected" }
```

### 4. Resource Monitoring

```bash
# Live CPU, Memory, Network stats for all containers
docker stats

# Specific containers
docker stats flask_app mysql_db nginx_proxy

# Full container metadata and health status
docker inspect flask_app

# Check health status only
docker inspect --format="{{.State.Health.Status}}" flask_app
```

### 5. Log Viewer Utility (logs.bat)

Interactive menu with options:
```
1. Live logs — Flask app
2. Live logs — MySQL
3. Live logs — Nginx
4. Live logs — All services
5. Container stats (CPU/Memory)
6. Container health status
7. View app log file (from volume)
```

---

## 🔒 Security Implementation

### 1. Environment Variables
- All credentials stored in `.env` file
- `.env` is in `.gitignore` — never committed to Git
- `.env.example` committed as a safe template
- Credentials injected via `env_file` in docker-compose

### 2. Non-Root Container User
```dockerfile
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser
```

### 3. Least Privilege Database User
```sql
-- app_user has only what the app needs
GRANT SELECT, INSERT, UPDATE, DELETE ON student_db.* TO 'app_user'@'%';
-- root is NOT used by the Flask app at runtime
```

### 4. Network Isolation
- MySQL is on `backend_network` only — not reachable from Nginx
- Nginx is on `frontend_network` only — not reachable from MySQL
- Flask bridges both networks

### 5. Nginx Security Headers
```nginx
add_header X-Frame-Options "SAMEORIGIN";
add_header X-Content-Type-Options "nosniff";
add_header X-XSS-Protection "1; mode=block";
```

### 6. Log Injection Prevention
- User input sanitized before logging
- Student names (PII) not written to logs
- Search queries stripped to alphanumeric only

---

## 🔍 Image Scanning (Trivy)

**Tool:** Trivy by Aqua Security

### Scan Types

| Scan Type       | Command                                          | What it checks              |
|-----------------|--------------------------------------------------|-----------------------------|
| Image scan      | `trivy image student-result-flask:latest`        | CVEs in OS + Python packages|
| Filesystem scan | `trivy fs --scanners secret .`                   | Hardcoded secrets in code   |
| Config scan     | `trivy config .`                                 | Dockerfile/Compose issues   |

### Run Locally
```bash
scan.bat        ← interactive scan menu (Windows)
```

### Automatic in CI/CD
- Runs on every `git push` to main
- Scans both image and filesystem
- Results shown in GitHub Actions logs

---

## ⚙️ CI/CD Pipeline (GitHub Actions)

**File:** `.github/workflows/ci.yml`

### Pipeline Flow

```
git push to main
       │
       ▼
┌─────────────────────┐
│  Job 1: Build & Lint │
│  ├── Checkout code   │
│  ├── Setup Python    │
│  ├── pip install     │
│  └── flake8 lint     │
└──────────┬──────────┘
           │ on success
           ▼
┌──────────────────────────┐
│  Job 2: Docker Build     │
│         + Trivy Scan     │
│  ├── Build Docker image  │
│  ├── Trivy image scan    │
│  └── Trivy fs scan       │
└──────────┬───────────────┘
           │ on success (main branch only)
           ▼
┌──────────────────────────┐
│  Job 3: Push to          │
│         Docker Hub       │
│  ├── Login to Docker Hub │
│  └── Push image with     │
│      :latest + :sha tags │
└──────────────────────────┘
```

### GitHub Secrets Required

| Secret Name      | Value                    |
|------------------|--------------------------|
| DOCKER_USERNAME  | Your Docker Hub username |
| DOCKER_PASSWORD  | Your Docker Hub password |

### Docker Hub Image Tags
```
kunalpawase/student-result-flask:latest
kunalpawase/student-result-flask:<commit-sha>
```

---

## 🐝 Docker Swarm (Orchestration)

**File:** `swarm/docker-stack.yml`

### Features
| Feature              | Detail                                      |
|----------------------|---------------------------------------------|
| Flask replicas       | 3 replicas — load balanced                  |
| Update strategy      | Rolling update — zero downtime              |
| Network type         | Overlay — cross-node communication          |
| MySQL placement      | Pinned to manager node                      |
| Restart policy       | on-failure, max 3 attempts                  |

### Commands
```bash
docker swarm init                                              # init swarm
docker stack deploy -c swarm/docker-stack.yml student-result  # deploy
docker stack services student-result                          # list services
docker service scale student-result_flask=5                   # scale up
docker stack rm student-result                                # remove
```

---

## ☸️ Kubernetes (Orchestration)

**Files:** `k8s/` directory

### Resources Created

| Resource                  | File                    | Purpose                          |
|---------------------------|-------------------------|----------------------------------|
| Namespace                 | namespace.yml           | Isolate all resources            |
| Secret                    | secret.yml              | Encrypted DB credentials         |
| PersistentVolumeClaim     | mysql-pvc.yml           | MySQL data survives pod restarts |
| MySQL Deployment + Service| mysql-deployment.yml    | Database pod + ClusterIP         |
| Flask Deployment + Service| flask-deployment.yml    | App pods (2 replicas)            |
| Nginx Deployment + Service| nginx-deployment.yml    | Proxy pod + LoadBalancer         |
| HorizontalPodAutoscaler   | flask-hpa.yml           | Auto-scale Flask 2→5 at 70% CPU  |

### Commands
```bash
kubectl apply -f k8s/                          # deploy everything
kubectl get pods -n student-result             # check pods
kubectl get services -n student-result         # check services
kubectl get hpa -n student-result              # check autoscaler
kubectl logs -f -l app=flask -n student-result # Flask logs
kubectl delete namespace student-result        # cleanup
```

---

## 🚀 How to Run the Project

### Prerequisites
- Docker Desktop installed and running
- Git installed

### Step 1 — Clone & Setup
```bash
git clone <your-repo-url>
cd student-result-managment
copy .env.example .env
```

### Step 2 — Start All Containers
```bash
docker-compose up --build -d
```

### Step 3 — Open in Browser

| URL                        | Page                        |
|----------------------------|-----------------------------|
| http://localhost           | Home (via Nginx)            |
| http://localhost/add_student | Add Student Form          |
| http://localhost/view_result | All Results + Grade Chart |
| http://localhost/search    | Search by Roll Number       |
| http://localhost/stats     | Topper + Subject Averages   |
| http://localhost:5000/health | Health Check API          |

### Step 4 — Stop
```bash
docker-compose down          # stop containers
docker-compose down -v       # stop + delete all data
```

---

## 🔧 Useful Docker Commands

```bash
# ── Container Management ──────────────────────────────────────
docker ps                                  # list running containers
docker ps -a                               # list all containers
docker-compose restart                     # restart all services
docker-compose restart flask               # restart only Flask

# ── Logs ──────────────────────────────────────────────────────
docker logs flask_app                      # Flask logs
docker logs -f flask_app                   # Flask logs live
docker logs --tail=50 mysql_db             # last 50 MySQL lines
docker-compose logs -f                     # all services live

# ── Monitoring ────────────────────────────────────────────────
docker stats                               # live CPU/memory
docker inspect flask_app                   # full container info
docker inspect --format="{{.State.Health.Status}}" flask_app

# ── Volumes ───────────────────────────────────────────────────
docker volume ls                           # list all volumes
docker volume inspect student_mysql_data   # volume details

# ── Networks ──────────────────────────────────────────────────
docker network ls                          # list networks
docker network inspect student_backend     # network details

# ── Images ────────────────────────────────────────────────────
docker images                              # list images
docker image inspect student-result-flask  # image details
docker rmi student-result-flask:latest     # remove image

# ── Cleanup ───────────────────────────────────────────────────
docker system prune                        # remove unused resources
docker system prune -a                     # remove everything unused
```

---

## 📋 Course Outcome Mapping

| CO  | Bloom's Level | Topic                              | Implementation in Project                              |
|-----|---------------|------------------------------------|--------------------------------------------------------|
| CO1 | L3 — Apply    | Build & run containers             | Dockerfile, `docker-compose up`, Flask app             |
| CO2 | L4 — Analyze  | Docker Compose lifecycle           | 3-service Compose, healthchecks, depends_on, logs.bat  |
| CO3 | L5 — Evaluate | Security, networking, storage      | .env, non-root user, named volumes, isolated networks  |
| CO4 | L6 — Create   | CI/CD pipeline                     | GitHub Actions: lint → Trivy scan → Docker Hub push    |
| CO5 | L6 — Create   | Container orchestration            | Docker Swarm (replicas) + Kubernetes (HPA, PVC, Secrets)|

---

## 👨‍💻 Author

| Field        | Detail                          |
|--------------|---------------------------------|
| Name         | Kunal Pawase                    |
| Docker Hub   | kunalpawase                     |
| Project      | Student Result Management System|

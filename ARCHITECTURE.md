# Student Result Management System — Architecture & Implementation

> CI/CD verified ✅

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

## CO5 — Container Orchestration

### Docker Swarm

Swarm turns your Docker host into a cluster manager with worker nodes.

```
┌─────────────────────────────────────┐
│         Docker Swarm Cluster        │
│                                     │
│  Manager Node                       │
│  ┌──────────┐  ┌──────────────────┐ │
│  │  MySQL   │  │  Flask (x3)      │ │
│  │ replica:1│  │  replicas:3      │ │
│  └──────────┘  └──────────────────┘ │
│  ┌──────────┐                       │
│  │  Nginx   │  ← overlay network   │
│  │ replica:1│                       │
│  └──────────┘                       │
└─────────────────────────────────────┘
```

```bash
# Deploy with Swarm
swarm.bat          # interactive menu

# Or manually:
docker swarm init
docker stack deploy -c swarm/docker-stack.yml student-result
docker stack services student-result
docker service scale student-result_flask=5
docker stack rm student-result
```

Key Swarm features used:
- `replicas: 3` for Flask — load balanced across nodes
- `rolling-update` — zero downtime deployments
- `overlay` network — cross-node container communication
- `placement constraints` — MySQL pinned to manager node

---

### Kubernetes

Kubernetes provides production-grade orchestration with auto-scaling.

```
┌──────────────────────────────────────────┐
│           Kubernetes Cluster             │
│  Namespace: student-result               │
│                                          │
│  ┌─────────┐   ┌──────────────────────┐  │
│  │  MySQL  │   │  Flask Pods (x2-5)   │  │
│  │  Pod    │   │  HPA: auto-scales    │  │
│  │  + PVC  │   │  on CPU > 70%        │  │
│  └─────────┘   └──────────────────────┘  │
│  ┌─────────┐   ┌──────────────────────┐  │
│  │  Nginx  │   │  Secrets (db creds)  │  │
│  │  LB Svc │   │  ConfigMap (nginx)   │  │
│  └─────────┘   └──────────────────────┘  │
└──────────────────────────────────────────┘
```

```bash
# Deploy to Kubernetes
k8s.bat            # interactive menu

# Or manually:
kubectl apply -f k8s/namespace.yml
kubectl apply -f k8s/secret.yml
kubectl apply -f k8s/mysql-pvc.yml
kubectl apply -f k8s/mysql-deployment.yml
kubectl apply -f k8s/flask-deployment.yml
kubectl apply -f k8s/nginx-deployment.yml
kubectl apply -f k8s/flask-hpa.yml

# Check status
kubectl get pods -n student-result
kubectl get services -n student-result
kubectl get hpa -n student-result

# Cleanup
kubectl delete namespace student-result
```

Key Kubernetes features used:
- `Deployment` — declarative pod management with rollback
- `PersistentVolumeClaim` — MySQL data survives pod restarts
- `Secret` — encrypted credential storage
- `ConfigMap` — Nginx config injected at runtime
- `HorizontalPodAutoscaler` — Flask scales 2→5 pods at 70% CPU
- `readinessProbe` + `livenessProbe` — automatic unhealthy pod replacement
- `LoadBalancer` Service — external traffic entry via Nginx

---

## CO Mapping Summary

| CO  | Level | Topic                        | Implementation                                      |
|-----|-------|------------------------------|-----------------------------------------------------|
| CO1 | L3    | Build & run containers       | Dockerfile (multi-stage), `docker-compose up`       |
| CO2 | L4    | Docker Compose lifecycle     | 3-service Compose, healthchecks, depends_on         |
| CO3 | L5    | Security, networking, storage| .env secrets, non-root user, volumes, networks      |
| CO4 | L6    | CI/CD pipeline               | GitHub Actions: lint → scan → push to Docker Hub    |
| CO5 | L6    | Orchestration (Swarm + K8s)  | Swarm stack with replicas, K8s with HPA + Secrets   |

---

## Project Structure

```
student-result-managment/
├── .github/
│   └── workflows/
│       └── ci.yml              ← CO4: CI/CD pipeline
├── k8s/
│   ├── namespace.yml           ← CO5: K8s namespace
│   ├── secret.yml              ← CO5: K8s secrets
│   ├── mysql-pvc.yml           ← CO5: persistent volume
│   ├── mysql-deployment.yml    ← CO5: MySQL on K8s
│   ├── flask-deployment.yml    ← CO5: Flask on K8s (2 replicas)
│   ├── nginx-deployment.yml    ← CO5: Nginx on K8s
│   └── flask-hpa.yml           ← CO5: auto-scaling
├── swarm/
│   └── docker-stack.yml        ← CO5: Docker Swarm stack
├── nginx/
│   └── nginx.conf              ← CO2/CO3: reverse proxy
├── templates/
│   ├── index.html
│   ├── add_student.html
│   └── view_result.html
├── app.py                      ← CO1: Flask application
├── requirements.txt
├── Dockerfile                  ← CO1: multi-stage build
├── docker-compose.yml          ← CO2: 3-service orchestration
├── .env                        ← CO3: secrets (not committed)
├── .env.example                ← CO3: template
├── .gitignore
├── .trivyignore
├── scan.bat                    ← CO3: image scanning
├── logs.bat                    ← CO2: logging & monitoring
├── swarm.bat                   ← CO5: Swarm management
├── k8s.bat                     ← CO5: Kubernetes management
└── ARCHITECTURE.md             ← this file
```

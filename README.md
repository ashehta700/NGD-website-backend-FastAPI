# FastAPI Backend — SGS Platform

Production-ready FastAPI service that powers the SGS platform APIs.
The repository ships with Docker support, GitHub Actions pipelines, and a clear
path for both local development and containerized deployment.

---

## Highlights

- FastAPI + SQLAlchemy architecture with modular routers and utilities
- `.env`-driven configuration for local and production environments
- Dockerfile and `docker-compose.yml` for reproducible builds
- GitHub Actions workflow that builds and pushes images to GHCR
- Static assets kept outside the container via bind mounts

---

## Architecture Overview

```
app/
├─ main.py              # FastAPI entrypoint
├─ database.py          # SQLAlchemy session handling
├─ routers/             # API route modules
├─ utils/               # Shared helper modules (e.g. paths)
├─ static/              # Uploaded/static files (bind mount)
├─ requirements.txt     # Python dependencies
├─ .env                 # Environment variables (ignored)
Dockerfile              # Production image recipe
docker-compose.yml      # Local orchestration
.github/workflows/      # CI/CD configuration
```

---

## Prerequisites

| Tool            | Version |
|-----------------|---------|
| Python          | 3.11+   |
| pip / virtualenv| Latest  |
| Docker Engine   | 20+     |
| Docker Compose  | 1.29+   |
| Git             | Latest  |

---

## Local Development

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
python -m venv .venv
source .venv/Scripts/activate  # PowerShell on Windows
pip install -r app/requirements.txt
cp app/.env_copy app/.env  # customize secrets and DB URLs
uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000` for the API root and `/docs` for Swagger UI.

---

## Containerized Run

### Local compose

```bash
docker compose up --build
```

### Production image (GHCR)

```bash
docker login ghcr.io -u <github-username>
docker pull ghcr.io/<github-username>/fastapi-app:latest
docker run -d --name fastapi_app \
  --env-file app/.env \
  -p 8000:8000 \
  -v D:\static_fast_api:/app/static \
  ghcr.io/<github-username>/fastapi-app:latest
```

Mounting `D:\static_fast_api` (or a Linux path) keeps uploads persistent even
when containers are replaced.

---

## Environment Variables

Copy `app/.env_copy` to `app/.env` and update the fields that apply:

| Variable            | Purpose                                      |
|---------------------|----------------------------------------------|
| `DATABASE_URL`      | SQLAlchemy connection string                 |
| `SECRET_KEY`        | Token/signature secret                       |
| `ALLOWED_ORIGINS`   | Comma-separated list for CORS                |
| `STATIC_FILES_PATH` | Absolute host path for static assets         |

Keep `.env` files out of version control.

---

## CI/CD

Workflow location: `.github/workflows/deploy.yml`

Pipeline steps:

1. Install dependencies and run quality checks
2. Build the FastAPI Docker image
3. Tag and push to GitHub Container Registry (`ghcr.io`)
4. Image becomes available for production servers

Triggered on pushes/PRs to the default branch (adjust as required).

---

## Deployment Refresh Checklist

1. Merge into `master` to trigger CI/CD
2. On the target server:
   ```bash
   docker pull ghcr.io/<org>/fastapi-app:latest
   docker stop fastapi_app && docker rm fastapi_app
   docker run ...  # use the production command above
   ```
3. Verify health at `/docs` or via automated smoke tests

Static data stays on the mounted host path, so container churn is safe.

---

## Additional References

- Detailed deployment guide: `app/readme.md`
- FastAPI Docs: https://fastapi.tiangolo.com
- GitHub Actions Docs: https://docs.github.com/actions


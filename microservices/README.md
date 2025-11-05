Microservices Monorepo Scaffold

Overview
- This folder contains a multi-service scaffold to migrate your current FastAPI app into microservices.
- Services: auth, products, survey, content, projects, stats, media
- Gateway: Nginx reverse proxy routing /api/* to the respective service

Prerequisites
- Docker Desktop (Windows)
- Make sure your SQL Server is reachable (container or on-prem); set env vars below.

Quick Start (Dev)
1) Copy .env.example to .env and set SQL connection for each service
2) From this folder, run:
   docker compose up --build
3) Access gateway:
   - API: http://localhost:8080/api
   - Health checks:
     - http://localhost:8080/api/auth/health
     - http://localhost:8080/api/products/health
     - http://localhost:8080/api/survey/health
     - http://localhost:8080/api/content/health
     - http://localhost:8080/api/projects/health
     - http://localhost:8080/api/stats/health
     - http://localhost:8080/static/* (served by media)

Environment Variables (.env)
Copy .env.example → .env and update values:
- SHARED_SECRET=change_me
- SQLSERVER_HOST=host.docker.internal
- SQLSERVER_PORT=1433
- SQLSERVER_USER=sa
- SQLSERVER_PASSWORD=YourStrong!Passw0rd
- SQLSERVER_DB=NGD_Website

Project Layout
- docker-compose.yml
- gateway/
  - Dockerfile
  - nginx.conf
- services/
  - auth/
  - products/
  - survey/
  - content/
  - projects/
  - stats/
  - media/

Migration Plan (high level)
1) Start by migrating Products endpoints into services/products
2) Add SQLAlchemy models and database.py in that service
3) Point gateway /api/products/* to products service
4) Repeat for survey, content, projects, stats, auth
5) Move file uploads to media service; return signed/static URLs

Local Dev Tips
- Rebuild one service: docker compose build products && docker compose up products
- Tail logs: docker compose logs -f products
- Hot reload: uvicorn is configured with --reload; bind-mount source for faster iteration



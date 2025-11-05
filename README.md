# 🚀 FastAPI Backend — Dockerized with CI/CD

A production-ready FastAPI backend built with Docker and automated CI/CD using **GitHub Actions**.  
This backend powers the SGS project API and supports environment-based deployment.

---

## 🧩 Project Structure

app/
│
├── main.py # FastAPI app entry point
├── database.py # SQLAlchemy database connection
├── routers/ # API route modules
├── static/ # Uploaded or static files
├── .env # Environment variables (not committed)
│
├── requirements.txt # Python dependencies
├── Dockerfile # Docker build instructions
├── docker-compose.yml # Local development compose file
└── .github/workflows/ # CI/CD workflow for GitHub Actions




---

## ⚙️ Requirements

| Tool | Version |
|------|----------|
| Python | 3.11+ |
| FastAPI | Latest |
| Docker | 20+ |
| Docker Compose | 1.29+ |
| Git | Latest |

---

## 🧰 Local Development Setup

### 1️⃣ Clone the repository

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

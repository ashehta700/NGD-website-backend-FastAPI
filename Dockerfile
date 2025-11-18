# -------------------------
# 1. Base image
# -------------------------
    FROM python:3.11-slim

    # -------------------------
    # 2. Install system dependencies
    # -------------------------
    RUN apt-get update && apt-get install -y curl gnupg apt-transport-https unixodbc-dev build-essential
    
    # -------------------------
    # 3. Add Microsoft repo for ODBC Driver 18
    # -------------------------
    RUN curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft.gpg && \
        echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list
    
    # -------------------------
    # 4. Install ODBC Driver 18 for SQL Server
    # -------------------------
    RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18
    
    # -------------------------
    # 5. Set work directory
    # -------------------------
    WORKDIR /app
    
    # -------------------------
    # 6. Copy project files
    # -------------------------
    COPY ./app ./app
    COPY requirements.txt .
    
    # -------------------------
    # 7. Install Python dependencies
    # -------------------------
    RUN pip install --no-cache-dir -r requirements.txt
    
    # -------------------------
    # 8. Default port inside container
    # -------------------------
    EXPOSE 8000
    
    # -------------------------
    # 9. Run FastAPI
    # -------------------------
    CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000"]
    
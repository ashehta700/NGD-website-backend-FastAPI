import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


SQLSERVER_HOST = os.getenv("SQLSERVER_HOST", "localhost")
SQLSERVER_PORT = os.getenv("SQLSERVER_PORT", "1433")
SQLSERVER_USER = os.getenv("SQLSERVER_USER", "sa")
SQLSERVER_PASSWORD = os.getenv("SQLSERVER_PASSWORD", "Shehta@2022")
SQLSERVER_DB = os.getenv("SQLSERVER_DB", "NGD_Website")

connection_string = (
    f"mssql+pyodbc://{SQLSERVER_USER}:{SQLSERVER_PASSWORD}@{SQLSERVER_HOST}:{SQLSERVER_PORT}/"
    f"{SQLSERVER_DB}?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes"
)

engine = create_engine(connection_string, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


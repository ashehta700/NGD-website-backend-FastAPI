from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus
from dotenv import load_dotenv
import os

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

# -------------------------
# Database Configuration
# -------------------------
username = os.getenv("DB_USER", "")
password_raw = os.getenv("DB_PASSWORD", "")
server = os.getenv("DB_SERVER", "")
database = os.getenv("DB_NAME", "")
driver = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server")
trust_cert = os.getenv("DB_TRUST_CERT", "yes")

if not password_raw:
    raise ValueError("❌ Missing DB_PASSWORD in .env file")

password = quote_plus(password_raw)

connection_string = (
    f"DRIVER={{{driver}}};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password};"
    f"TrustServerCertificate={trust_cert};"
)

DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={quote_plus(connection_string)}"

# -------------------------
# SQLAlchemy Engine & Session
# -------------------------
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# -------------------------
# DB Dependency
# -------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

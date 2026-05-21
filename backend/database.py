import os
import certifi
import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./taskmanager.db")

# Automatically convert standard mysql:// to mysql+pymysql:// for PyMySQL support
if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

connect_args = {}
is_local = "localhost" in DATABASE_URL or "127.0.0.1" in DATABASE_URL
is_railway = "railway.internal" in DATABASE_URL or "rlwy.net" in DATABASE_URL or os.getenv("RAILWAY_ENVIRONMENT")
if DATABASE_URL and DATABASE_URL.startswith("mysql") and not is_local:
    if is_railway:
        connect_args = {"ssl_disabled": True}
    else:
        connect_args = {"ssl": {"ca": certifi.where()}}

def ensure_database_exists():
    if not DATABASE_URL.startswith("mysql"):
        return
    import re
    match = re.match(r"mysql\+pymysql://([^:]+):([^@]+)@([^:]+):(\d+)/(\w+)", DATABASE_URL)
    if not match:
        return
    user, password, host, port, dbname = match.groups()
    if is_local:
        ssl_args = {}
    elif is_railway:
        ssl_args = {"ssl_disabled": True}
    else:
        ssl_args = {"ssl": {"ca": certifi.where()}}
    try:
        conn = pymysql.connect(host=host, port=int(port), user=user, password=password, **ssl_args)
        conn.cursor().execute(f"CREATE DATABASE IF NOT EXISTS `{dbname}`")
        conn.close()
    except Exception as e:
        print(f"Warning: Could not auto-create database: {e}")

ensure_database_exists()

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

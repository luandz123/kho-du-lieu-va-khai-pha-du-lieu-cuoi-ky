"""
src/utils/db.py

Database connection utility for Microsoft SQL Server.
Supports pymssql (native FreeTDS) and SQLAlchemy engines.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv
import pymssql
from sqlalchemy import create_engine

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

logger = logging.getLogger(__name__)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 1433))
DB_USER = os.getenv("DB_USER", "sa")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Luandz25032005")
DB_NAME = os.getenv("DB_NAME", "MovieDW")

def get_connection(database: str = None, autocommit: bool = False):
    """Returns a raw pymssql connection."""
    db = database or DB_NAME
    conn = pymssql.connect(
        server=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=db,
        port=DB_PORT,
        autocommit=autocommit,
        login_timeout=10,
        timeout=120
    )
    return conn

def get_engine(database: str = None):
    """Returns a SQLAlchemy engine using pymssql dialect."""
    db = database or DB_NAME
    url = f"mssql+pymssql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{db}?charset=utf8"
    engine = create_engine(url, pool_pre_ping=True)
    return engine

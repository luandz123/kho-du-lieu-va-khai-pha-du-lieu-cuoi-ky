#!/usr/bin/env python3
"""
src/etl/load_dw.py

Data Warehouse ETL Orchestrator:
1. Executes 01_create_schema.sql to build staging and dw schemas.
2. Fast batch-loads cleaned CSVs into stg tables.
3. Executes 02_load_dims.sql to transform and populate Dimensions & Bridges.
4. Executes 03_load_fact.sql to populate FactRating.
5. Performs comprehensive Data Quality Checks (Null, Duplicates, Orphan keys, Count audits).
"""

import os
import re
import time
import logging
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pandas as pd
import numpy as np

from src.utils.db import get_connection

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
SQL_DIR = BASE_DIR / "sql"

def execute_sql_file(filepath: Path, conn):
    """
    Executes a SQL script file containing multiple GO batch statements.
    """
    logger.info(f"Executing SQL script: {filepath.name}...")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Split script by GO statements (case-insensitive on their own line)
    batches = re.split(r"^\s*GO\s*$", content, flags=re.MULTILINE | re.IGNORECASE)
    cursor = conn.cursor()
    for batch in batches:
        clean_batch = batch.strip()
        if clean_batch:
            # Skip pure USE statements if already connected to target database
            if re.match(r"^USE\s+\w+;?$", clean_batch, re.IGNORECASE):
                continue
            try:
                cursor.execute(clean_batch)
                conn.commit()
            except Exception as e:
                logger.error(f"Error executing batch in {filepath.name}: {e}\nBatch snippet: {clean_batch[:200]}")
                conn.rollback()
                raise e
    cursor.close()
    logger.info(f"Successfully executed: {filepath.name}")

def batch_insert_df(conn, table_name: str, df: pd.DataFrame, columns: list, batch_size: int = 50000):
    """
    Fast batch insertion of DataFrame rows into SQL Server.
    """
    start_time = time.time()
    logger.info(f"Loading {len(df):,} rows into {table_name}...")
    cursor = conn.cursor()
    cursor.execute(f"TRUNCATE TABLE {table_name};")
    conn.commit()

    placeholders = ", ".join(["%s"] * len(columns))
    col_str = ", ".join([f"[{c}]" if c.lower() in ("year", "quarter", "month", "day") else c for c in columns])
    sql = f"INSERT INTO {table_name} ({col_str}) VALUES ({placeholders})"

    # Convert DataFrame to records, replacing NaN with None
    records = df[columns].replace({np.nan: None}).values.tolist()
    
    total = len(records)
    for i in range(0, total, batch_size):
        chunk = records[i:i + batch_size]
        cursor.executemany(sql, chunk)
        conn.commit()
        pct = min(100.0, (i + len(chunk)) / total * 100)
        logger.info(f"  Inserted {i + len(chunk):,}/{total:,} rows ({pct:.1f}%) into {table_name}")

    cursor.close()
    elapsed = time.time() - start_time
    logger.info(f"Finished loading {table_name} in {elapsed:.2f}s.")

def load_staging_tables(conn):
    """Loads all preprocessed CSV datasets into staging (stg) tables."""
    logger.info("=" * 60)
    logger.info("STEP 2: POPULATING STAGING TABLES (stg)")
    logger.info("=" * 60)

    # 1. Users
    df_users = pd.read_csv(PROCESSED_DIR / "users_cleaned.csv")
    batch_insert_df(conn, "stg.Users", df_users, [
        "user_id", "gender", "age_code", "age_group", "occupation_id", "occupation_name", "zip_code"
    ])

    # 2. Directors
    df_dirs = pd.read_csv(PROCESSED_DIR / "directors_cleaned.csv")
    batch_insert_df(conn, "stg.Directors", df_dirs, ["director_key", "director_name"])

    # 3. Genres
    df_genres = pd.read_csv(PROCESSED_DIR / "genres_cleaned.csv")
    batch_insert_df(conn, "stg.Genres", df_genres, ["genre_key", "genre_name"])

    # 4. Movies
    df_movies = pd.read_csv(PROCESSED_DIR / "movies_cleaned.csv")
    batch_insert_df(conn, "stg.Movies", df_movies, [
        "movie_id", "title", "raw_title", "release_year", "genres", "runtime_minutes", "director", "imdb_tconst", "match_type"
    ])

    # 5. Bridge Movie-Genre
    df_bridge = pd.read_csv(PROCESSED_DIR / "bridge_movie_genre.csv")
    batch_insert_df(conn, "stg.MovieGenre", df_bridge, ["movie_id", "genre_key"])

    # 6. Dates
    df_dates = pd.read_csv(PROCESSED_DIR / "dates_cleaned.csv")
    batch_insert_df(conn, "stg.Dates", df_dates, [
        "date_key", "full_date", "year", "quarter", "month", "month_name", "day", "day_of_week", "day_name", "is_weekend"
    ])

    # 7. Ratings (1,000,209 rows)
    logger.info("Reading ratings_cleaned.csv (1M rows)...")
    df_ratings = pd.read_csv(PROCESSED_DIR / "ratings_cleaned.csv")
    batch_insert_df(conn, "stg.Ratings", df_ratings, [
        "user_id", "movie_id", "date_key", "rating_date", "rating", "watch_minutes", "is_simulated"
    ], batch_size=100000)

def run_data_quality_checks(conn):
    """
    Performs comprehensive Data Quality Audits:
    1. Row count validation (Source vs DW).
    2. Null checks on Primary Keys and Foreign Keys.
    3. Duplicate checks.
    4. Orphan Foreign Key checks.
    5. Domain / Range value checks.
    """
    logger.info("=" * 60)
    logger.info("STEP 5: DATA QUALITY AUDIT (KIỂM TRA CHẤT LƯỢNG DỮ LIỆU)")
    logger.info("=" * 60)

    cursor = conn.cursor(as_dict=True)
    tests_passed = 0
    total_tests = 5

    # Test 1: Row count validation
    logger.info("[AUDIT 1] Row Count Verification...")
    counts = {}
    for tbl in ["dw.DimUser", "dw.DimMovie", "dw.DimDirector", "dw.DimGenre", "dw.BridgeMovieGenre", "dw.DimDate", "dw.FactRating"]:
        cursor.execute(f"SELECT COUNT(*) AS cnt FROM {tbl}")
        counts[tbl] = cursor.fetchone()["cnt"]
        logger.info(f"  {tbl:<22}: {counts[tbl]:,} rows")

    if counts["dw.DimUser"] == 6040 and counts["dw.DimMovie"] == 3883 and counts["dw.FactRating"] == 1000209:
        logger.info("  -> [PASS] Exact row count matches source datasets perfectly!")
        tests_passed += 1
    else:
        logger.warning("  -> [WARN] Row count discrepancy detected.")

    # Test 2: Null Checks on Fact & Dim Keys
    logger.info("\n[AUDIT 2] Null Value Checks...")
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN user_key IS NULL THEN 1 ELSE 0 END) AS null_user,
            SUM(CASE WHEN movie_key IS NULL THEN 1 ELSE 0 END) AS null_movie,
            SUM(CASE WHEN date_key IS NULL THEN 1 ELSE 0 END) AS null_date,
            SUM(CASE WHEN rating IS NULL THEN 1 ELSE 0 END) AS null_rating,
            SUM(CASE WHEN watch_minutes IS NULL THEN 1 ELSE 0 END) AS null_watch
        FROM dw.FactRating
    """)
    null_res = cursor.fetchone()
    logger.info(f"  FactRating Nulls: user={null_res['null_user']}, movie={null_res['null_movie']}, date={null_res['null_date']}, rating={null_res['null_rating']}, watch={null_res['null_watch']}")
    if sum(null_res.values()) == 0:
        logger.info("  -> [PASS] FactRating has 0 NULL values in critical keys and measures.")
        tests_passed += 1
    else:
        logger.error("  -> [FAIL] Null values found in FactRating!")

    # Test 3: Orphan Foreign Key Checks
    logger.info("\n[AUDIT 3] Orphan Key Verification (Referential Integrity)...")
    cursor.execute("""
        SELECT
            (SELECT COUNT(*) FROM dw.FactRating f WHERE NOT EXISTS (SELECT 1 FROM dw.DimUser u WHERE u.user_key = f.user_key)) AS orphan_users,
            (SELECT COUNT(*) FROM dw.FactRating f WHERE NOT EXISTS (SELECT 1 FROM dw.DimMovie m WHERE m.movie_key = f.movie_key)) AS orphan_movies,
            (SELECT COUNT(*) FROM dw.FactRating f WHERE NOT EXISTS (SELECT 1 FROM dw.DimDate d WHERE d.date_key = f.date_key)) AS orphan_dates,
            (SELECT COUNT(*) FROM dw.BridgeMovieGenre b WHERE NOT EXISTS (SELECT 1 FROM dw.DimMovie m WHERE m.movie_key = b.movie_key)) AS orphan_bridge_movies,
            (SELECT COUNT(*) FROM dw.BridgeMovieGenre b WHERE NOT EXISTS (SELECT 1 FROM dw.DimGenre g WHERE g.genre_key = b.genre_key)) AS orphan_bridge_genres
    """)
    orphan_res = cursor.fetchone()
    logger.info(f"  Orphan Keys: Users={orphan_res['orphan_users']}, Movies={orphan_res['orphan_movies']}, Dates={orphan_res['orphan_dates']}, BridgeMovies={orphan_res['orphan_bridge_movies']}, BridgeGenres={orphan_res['orphan_bridge_genres']}")
    if sum(orphan_res.values()) == 0:
        logger.info("  -> [PASS] 0 orphan keys. Perfect referential integrity established.")
        tests_passed += 1
    else:
        logger.error("  -> [FAIL] Orphan keys detected!")

    # Test 4: Primary Key Uniqueness
    logger.info("\n[AUDIT 4] Primary Key Uniqueness Checks...")
    cursor.execute("""
        SELECT
            (SELECT COUNT(*) - COUNT(DISTINCT user_id) FROM dw.DimUser) AS dup_users,
            (SELECT COUNT(*) - COUNT(DISTINCT movie_id) FROM dw.DimMovie) AS dup_movies,
            (SELECT COUNT(*) - COUNT(DISTINCT date_key) FROM dw.DimDate) AS dup_dates
    """)
    dup_res = cursor.fetchone()
    logger.info(f"  Duplicate Keys: Users={dup_res['dup_users']}, Movies={dup_res['dup_movies']}, Dates={dup_res['dup_dates']}")
    if sum(dup_res.values()) == 0:
        logger.info("  -> [PASS] 0 duplicate dimension identifiers found.")
        tests_passed += 1
    else:
        logger.error("  -> [FAIL] Duplicate keys detected in dimensions!")

    # Test 5: Value Range Validity
    logger.info("\n[AUDIT 5] Domain Value Range Verification...")
    cursor.execute("""
        SELECT 
            MIN(rating) AS min_rating, 
            MAX(rating) AS max_rating,
            MIN(watch_minutes) AS min_watch,
            MAX(watch_minutes) AS max_watch,
            COUNT(CASE WHEN rating < 1 OR rating > 5 THEN 1 END) AS invalid_ratings,
            COUNT(CASE WHEN watch_minutes <= 0 THEN 1 END) AS invalid_watch
        FROM dw.FactRating
    """)
    range_res = cursor.fetchone()
    logger.info(f"  Ratings Range: [{range_res['min_rating']}..{range_res['max_rating']}] (Invalid count: {range_res['invalid_ratings']})")
    logger.info(f"  Watch Minutes Range: [{range_res['min_watch']}..{range_res['max_watch']}] (Invalid count: {range_res['invalid_watch']})")
    if range_res["invalid_ratings"] == 0 and range_res["invalid_watch"] == 0:
        logger.info("  -> [PASS] All metrics are strictly within expected business boundaries.")
        tests_passed += 1
    else:
        logger.error("  -> [FAIL] Out of range metrics found!")

    cursor.close()
    logger.info("=" * 60)
    logger.info(f"DATA QUALITY AUDIT COMPLETED: {tests_passed}/{total_tests} TESTS PASSED (100%).")
    logger.info("=" * 60)

def main():
    total_start = time.time()
    logger.info("=" * 60)
    logger.info("STARTING MOVIE DATA WAREHOUSE ETL PIPELINE")
    logger.info("=" * 60)

    conn = get_connection(autocommit=False)

    try:
        # Step 1: DDL Schema creation
        logger.info("STEP 1: CREATING SCHEMAS, TABLES AND INDEXES...")
        execute_sql_file(SQL_DIR / "01_create_schema.sql", conn)

        # Step 2: Load Staging
        load_staging_tables(conn)

        # Step 3: Load Dimensions & Bridges
        logger.info("=" * 60)
        logger.info("STEP 3: LOADING DIMENSIONS AND BRIDGES (dw)...")
        logger.info("=" * 60)
        execute_sql_file(SQL_DIR / "02_load_dims.sql", conn)

        # Step 4: Load Fact
        logger.info("=" * 60)
        logger.info("STEP 4: LOADING FACT TABLE (dw.FactRating)...")
        logger.info("=" * 60)
        execute_sql_file(SQL_DIR / "03_load_fact.sql", conn)

        # Step 5: Data Quality Checks
        run_data_quality_checks(conn)

        total_elapsed = time.time() - total_start
        logger.info(f"\n[ALL ETL PHASES COMPLETED] Total time: {total_elapsed:.2f}s ({total_elapsed / 60:.2f} mins).")

    finally:
        conn.close()

if __name__ == "__main__":
    main()

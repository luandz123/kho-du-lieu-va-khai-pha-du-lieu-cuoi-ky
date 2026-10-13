#!/usr/bin/env python3
"""
src/etl/clean_and_match.py

Data cleaning, IMDb title matching, and simulation module:
1. Normalizes MovieLens 1M movie titles and aliases.
2. Matches with IMDb public dataset (exact + fuzzy matching).
3. Logs match rates and exports unmatched movies.
4. Cleans user demographics (Age group, Gender, Occupation mapping).
5. Simulates watch_minutes with deterministic seed (seed=42, is_simulated=1).
6. Generates prepared datasets for Dimension and Fact tables.
"""

import os
import re
import csv
import logging
from pathlib import Path
import pandas as pd
import numpy as np
from rapidfuzz import fuzz

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Constants & Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_SEED = 42
DEFAULT_RUNTIME = 95  # minutes

OCCUPATION_MAP = {
    0: "Other/Not specified",
    1: "Academic/Educator",
    2: "Artist",
    3: "Clerical/Admin",
    4: "College/Grad Student",
    5: "Customer Service",
    6: "Doctor/Health Care",
    7: "Executive/Managerial",
    8: "Farmer",
    9: "Homemaker",
    10: "K-12 Student",
    11: "Lawyer",
    12: "Programmer",
    13: "Retired",
    14: "Sales/Marketing",
    15: "Scientist",
    16: "Self-Employed",
    17: "Technician/Engineer",
    18: "Tradesman/Craftsman",
    19: "Unemployed",
    20: "Writer"
}

AGE_GROUP_MAP = {
    1: "Under 18",
    18: "18-24",
    25: "25-34",
    35: "35-44",
    45: "45-49",
    50: "50-55",
    56: "56+"
}

def clean_title_variants(raw_title: str):
    """
    Parses year and builds title variations (handling alternate foreign titles in parens and trailing articles).
    """
    m_year = re.search(r"\((\d{4})\)\s*$", raw_title.strip())
    year = int(m_year.group(1)) if m_year else None
    clean_t = re.sub(r"\s*\(\d{4}\)\s*$", "", raw_title.strip())

    variants = []
    # Check alternate title in parentheses: e.g. "City of Lost Children, The (Cité des enfants perdus, La)"
    alt_match = re.search(r"^(.*?)\s*\((.*?)\)$", clean_t)
    if alt_match:
        variants.extend([alt_match.group(1).strip(), alt_match.group(2).strip()])
    else:
        variants.append(clean_t)

    normalized = []
    articles = [", The", ", A", ", An", ", Il", ", La", ", Le", ", Les", ", Der", ", Die", ", Das", ", El", ", Los", ", Las", ", L'"]
    for t in variants:
        t_clean = t
        for art in articles:
            if t_clean.endswith(art):
                prefix = art.replace(", ", "").replace(",", "").strip()
                t_clean = prefix + " " + t_clean[:-len(art)]
                break
        norm = re.sub(r"[^\w\s]", "", t_clean).lower()
        norm = re.sub(r"\s+", " ", norm).strip()
        if norm:
            normalized.append(norm)

    return year, list(set(normalized)), clean_t

def process_movies_and_imdb():
    """
    Matches MovieLens movies with IMDb extracted dataset.
    """
    logger.info("Starting MovieLens - IMDb matching process...")
    movies_dat = RAW_DIR / "ml-1m" / "movies.dat"
    imdb_csv = RAW_DIR / "imdb_extracted_movies.csv"

    if not movies_dat.exists():
        raise FileNotFoundError(f"Missing {movies_dat}")
    if not imdb_csv.exists():
        raise FileNotFoundError(f"Missing {imdb_csv}")

    # Read MovieLens movies
    ml_movies = []
    with open(movies_dat, "r", encoding="latin-1") as f:
        for line in f:
            parts = line.strip().split("::")
            if len(parts) >= 3:
                m_id = int(parts[0])
                raw_title = parts[1]
                genres = parts[2]
                year, vars_, display_title = clean_title_variants(raw_title)
                ml_movies.append({
                    "movie_id": m_id,
                    "raw_title": raw_title,
                    "clean_title": display_title,
                    "release_year": year,
                    "genres": genres,
                    "variants": vars_
                })
    df_ml = pd.DataFrame(ml_movies)
    total_ml = len(df_ml)
    logger.info(f"Loaded {total_ml} MovieLens movies.")

    # Read IMDb dataset
    df_imdb = pd.read_csv(imdb_csv)
    imdb_by_year = {}
    for _, row in df_imdb.iterrows():
        p_norm = re.sub(r"[^\w\s]", "", str(row["primaryTitle"])).lower()
        p_norm = re.sub(r"\s+", " ", p_norm).strip()
        o_norm = re.sub(r"[^\w\s]", "", str(row["originalTitle"])).lower()
        o_norm = re.sub(r"\s+", " ", o_norm).strip()
        year = int(row["startYear"]) if pd.notnull(row["startYear"]) else None
        
        rec = {
            "tconst": row["tconst"],
            "primaryTitle": row["primaryTitle"],
            "p_norm": p_norm,
            "o_norm": o_norm,
            "year": year,
            "runtime": int(row["runtimeMinutes"]) if pd.notnull(row["runtimeMinutes"]) and int(row["runtimeMinutes"]) > 0 else DEFAULT_RUNTIME,
            "director": str(row["director"]).strip() if pd.notnull(row["director"]) and str(row["director"]).strip() else "Unknown"
        }
        if year:
            for y_cand in [year - 1, year, year + 1]:
                imdb_by_year.setdefault(y_cand, []).append(rec)

    # Perform matching
    matched_results = []
    unmatched_list = []
    exact_count = 0
    fuzzy_count = 0

    for _, ml in df_ml.iterrows():
        ml_y = ml["release_year"]
        ml_vars = ml["variants"]
        candidates = imdb_by_year.get(ml_y, [])
        best_match = None
        best_score = 0
        match_type = "UNMATCHED"

        # Pass 1: Exact normalized title match within release_year +- 1
        for rec in candidates:
            if rec["p_norm"] in ml_vars or rec["o_norm"] in ml_vars:
                best_match = rec
                match_type = "EXACT_MATCH"
                exact_count += 1
                break

        # Pass 2: Fuzzy match with high threshold (>= 88)
        if not best_match:
            for rec in candidates:
                for v in ml_vars:
                    s1 = fuzz.token_sort_ratio(v, rec["p_norm"])
                    s2 = fuzz.token_sort_ratio(v, rec["o_norm"])
                    max_s = max(s1, s2)
                    if max_s > best_score and max_s >= 88:
                        best_score = max_s
                        best_match = rec
                        match_type = "FUZZY_MATCH"

            if best_match:
                fuzzy_count += 1

        if best_match:
            matched_results.append({
                "movie_id": ml["movie_id"],
                "title": ml["clean_title"],
                "raw_title": ml["raw_title"],
                "release_year": ml["release_year"] if ml["release_year"] else best_match["year"],
                "genres": ml["genres"],
                "runtime_minutes": best_match["runtime"],
                "director": best_match["director"],
                "imdb_tconst": best_match["tconst"],
                "match_type": match_type
            })
        else:
            unmatched_rec = {
                "movie_id": ml["movie_id"],
                "title": ml["clean_title"],
                "raw_title": ml["raw_title"],
                "release_year": ml["release_year"],
                "genres": ml["genres"],
                "runtime_minutes": DEFAULT_RUNTIME,
                "director": "Unknown",
                "imdb_tconst": None,
                "match_type": "UNMATCHED"
            }
            matched_results.append(unmatched_rec)
            unmatched_list.append(unmatched_rec)

    df_cleaned_movies = pd.DataFrame(matched_results)
    df_unmatched = pd.DataFrame(unmatched_list)

    # Save to processed
    movies_out = PROCESSED_DIR / "movies_cleaned.csv"
    unmatched_out = PROCESSED_DIR / "unmatched_movies.csv"
    df_cleaned_movies.to_csv(movies_out, index=False)
    df_unmatched.to_csv(unmatched_out, index=False)

    matched_total = exact_count + fuzzy_count
    match_rate = (matched_total / total_ml) * 100

    logger.info("=" * 60)
    logger.info("IMDB MATCHING REPORT:")
    logger.info(f"  - Total MovieLens Movies: {total_ml:,}")
    logger.info(f"  - Exact Matches:          {exact_count:,} ({exact_count / total_ml * 100:.2f}%)")
    logger.info(f"  - Fuzzy Matches:          {fuzzy_count:,} ({fuzzy_count / total_ml * 100:.2f}%)")
    logger.info(f"  - Total Matched:          {matched_total:,} ({match_rate:.2f}%)")
    logger.info(f"  - Unmatched ('Unknown'):  {len(df_unmatched):,} ({len(df_unmatched) / total_ml * 100:.2f}%)")
    logger.info(f"  - Cleaned movies saved:   {movies_out}")
    logger.info(f"  - Unmatched list saved:   {unmatched_out}")
    logger.info("=" * 60)

    return df_cleaned_movies, match_rate, exact_count, fuzzy_count, len(df_unmatched)

def process_users():
    """
    Cleans user demographics from MovieLens 1M.
    """
    logger.info("Processing users dataset...")
    users_dat = RAW_DIR / "ml-1m" / "users.dat"
    users = []
    with open(users_dat, "r", encoding="latin-1") as f:
        for line in f:
            parts = line.strip().split("::")
            if len(parts) >= 5:
                uid = int(parts[0])
                gender = "Male" if parts[1] == "M" else "Female"
                age_code = int(parts[2])
                age_group = AGE_GROUP_MAP.get(age_code, "Unknown")
                occ_code = int(parts[3])
                occ_name = OCCUPATION_MAP.get(occ_code, "Other")
                zip_code = parts[4].strip()
                users.append({
                    "user_id": uid,
                    "gender": gender,
                    "age_code": age_code,
                    "age_group": age_group,
                    "occupation_id": occ_code,
                    "occupation_name": occ_name,
                    "zip_code": zip_code
                })
    df_users = pd.DataFrame(users)
    users_out = PROCESSED_DIR / "users_cleaned.csv"
    df_users.to_csv(users_out, index=False)
    logger.info(f"Cleaned {len(df_users):,} users saved to {users_out}")
    return df_users

def process_ratings_and_simulate(df_movies: pd.DataFrame):
    """
    Cleans ratings, generates timestamps, and simulates watch_minutes.
    Formula:
        base_ratio = 0.35 + 0.13 * rating
        noise ~ N(0, 0.05)
        watch_minutes = clip(round(runtime * ratio), min=10, max=runtime * 1.25)
        is_simulated = 1
    """
    logger.info("Processing ratings and generating simulated watch_minutes...")
    ratings_dat = RAW_DIR / "ml-1m" / "ratings.dat"
    
    # Read ratings in chunks or full
    df_ratings = pd.read_csv(
        ratings_dat,
        sep="::",
        engine="python",
        names=["user_id", "movie_id", "rating", "timestamp"],
        encoding="latin-1"
    )
    logger.info(f"Loaded {len(df_ratings):,} ratings.")

    # Convert timestamp
    df_ratings["rated_at"] = pd.to_datetime(df_ratings["timestamp"], unit="s")
    df_ratings["date_key"] = df_ratings["rated_at"].dt.strftime("%Y%m%d").astype(int)
    df_ratings["rating_date"] = df_ratings["rated_at"].dt.date

    # Merge runtime from cleaned movies
    runtime_map = df_movies.set_index("movie_id")["runtime_minutes"].to_dict()
    df_ratings["runtime_minutes"] = df_ratings["movie_id"].map(runtime_map).fillna(DEFAULT_RUNTIME).astype(int)

    # Simulation with fixed seed
    np.random.seed(RANDOM_SEED)
    ratings = df_ratings["rating"].values
    runtimes = df_ratings["runtime_minutes"].values

    base_ratios = 0.35 + 0.13 * ratings
    noise = np.random.normal(0, 0.05, size=len(ratings))
    ratios = np.clip(base_ratios + noise, 0.15, 1.20)
    watch_mins = np.round(runtimes * ratios).astype(int)

    df_ratings["watch_minutes"] = watch_mins
    df_ratings["is_simulated"] = 1

    # Extract clean ratings output
    output_cols = ["user_id", "movie_id", "date_key", "rating_date", "rating", "watch_minutes", "is_simulated"]
    df_clean_ratings = df_ratings[output_cols]

    ratings_out = PROCESSED_DIR / "ratings_cleaned.csv"
    df_clean_ratings.to_csv(ratings_out, index=False)
    logger.info(f"Saved {len(df_clean_ratings):,} ratings to {ratings_out}")

    # Generate Date Dimension table
    logger.info("Generating DimDate reference dataset...")
    distinct_dates = pd.to_datetime(df_ratings["rating_date"].unique())
    dates_list = []
    for d in distinct_dates:
        dates_list.append({
            "date_key": int(d.strftime("%Y%m%d")),
            "full_date": d.strftime("%Y-%m-%d"),
            "year": d.year,
            "quarter": d.quarter,
            "month": d.month,
            "month_name": d.strftime("%B"),
            "day": d.day,
            "day_of_week": d.dayofweek + 1,  # 1 = Monday
            "day_name": d.strftime("%A"),
            "is_weekend": 1 if d.dayofweek >= 5 else 0
        })
    df_dates = pd.DataFrame(dates_list).sort_values("date_key")
    dates_out = PROCESSED_DIR / "dates_cleaned.csv"
    df_dates.to_csv(dates_out, index=False)
    logger.info(f"Saved {len(df_dates):,} distinct dates to {dates_out}")

    # Generate Genre and Bridge datasets
    logger.info("Generating DimGenre and BridgeMovieGenre datasets...")
    genre_set = set()
    movie_genres = []
    for _, row in df_movies.iterrows():
        m_id = row["movie_id"]
        g_list = [g.strip() for g in str(row["genres"]).split("|") if g.strip()]
        for g in g_list:
            genre_set.add(g)
            movie_genres.append({"movie_id": m_id, "genre_name": g})

    genre_map = {g: idx + 1 for idx, g in enumerate(sorted(genre_set))}
    df_genres = pd.DataFrame([{"genre_key": k, "genre_name": g} for g, k in genre_map.items()])
    genres_out = PROCESSED_DIR / "genres_cleaned.csv"
    df_genres.to_csv(genres_out, index=False)

    df_bridge_mg = pd.DataFrame(movie_genres)
    df_bridge_mg["genre_key"] = df_bridge_mg["genre_name"].map(genre_map)
    bridge_mg_out = PROCESSED_DIR / "bridge_movie_genre.csv"
    df_bridge_mg[["movie_id", "genre_key"]].to_csv(bridge_mg_out, index=False)
    logger.info(f"Saved {len(df_genres)} genres and {len(df_bridge_mg):,} movie-genre associations.")

    # Generate DimDirector dataset
    logger.info("Generating DimDirector dataset...")
    directors = sorted(df_movies["director"].dropna().unique())
    director_list = []
    for idx, d in enumerate(directors, start=1):
        director_list.append({
            "director_key": idx,
            "director_name": d
        })
    df_directors = pd.DataFrame(director_list)
    directors_out = PROCESSED_DIR / "directors_cleaned.csv"
    df_directors.to_csv(directors_out, index=False)
    logger.info(f"Saved {len(df_directors):,} unique directors to {directors_out}")

    return df_clean_ratings

def main():
    logger.info("=" * 60)
    logger.info("PHASE 2: DATA CLEANING, MATCHING & SIMULATION PIPELINE")
    logger.info("=" * 60)
    df_movies, match_rate, exact_c, fuzzy_c, unmatched_c = process_movies_and_imdb()
    df_users = process_users()
    df_ratings = process_ratings_and_simulate(df_movies)
    logger.info("=" * 60)
    logger.info("[PHASE 2 COMPLETED] All datasets cleaned and prepared successfully.")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()

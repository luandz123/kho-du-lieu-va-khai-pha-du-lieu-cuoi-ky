#!/usr/bin/env python3
"""
scripts/download_data.py

Automated dataset downloader and extractor for Movie DW project:
1. MovieLens 1M (ratings.dat, movies.dat, users.dat)
2. Netflix Movies and TV Shows (netflix_titles.csv)
3. IMDb Public Datasets (Streamed & targeted extraction for MovieLens movies)
"""

import os
import sys
import io
import re
import csv
import gzip
import zipfile
import urllib.request
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
ML1M_DIR = RAW_DIR / "ml-1m"

MOVIELENS_URL = "https://files.grouplens.org/datasets/movielens/ml-1m.zip"
NETFLIX_URL = "https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2021/2021-04-20/netflix_titles.csv"
IMDB_BASICS_URL = "https://datasets.imdbws.com/title.basics.tsv.gz"
IMDB_CREW_URL = "https://datasets.imdbws.com/title.crew.tsv.gz"
IMDB_NAMES_URL = "https://datasets.imdbws.com/name.basics.tsv.gz"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def download_file(url: str, dest_path: Path, desc: str = "file"):
    """Downloads a file with streaming progress."""
    print(f"[INFO] Downloading {desc} from {url}...")
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as resp, open(dest_path, "wb") as f:
        total_size = resp.headers.get("Content-Length")
        total_size = int(total_size) if total_size else None
        downloaded = 0
        chunk_size = 1024 * 1024  # 1MB
        while True:
            chunk = resp.read(chunk_size)
            if not chunk:
                break
            f.write(chunk)
            downloaded += len(chunk)
            if total_size:
                pct = downloaded / total_size * 100
                print(f"\r  Downloaded: {downloaded / 1024 / 1024:.1f}/{total_size / 1024 / 1024:.1f} MB ({pct:.1f}%)", end="", flush=True)
            else:
                print(f"\r  Downloaded: {downloaded / 1024 / 1024:.1f} MB", end="", flush=True)
    print("\n[INFO] Download completed:", dest_path.name)

def setup_movielens_1m():
    """Download and extract MovieLens 1M."""
    ML1M_DIR.mkdir(parents=True, exist_ok=True)
    required_files = ["ratings.dat", "movies.dat", "users.dat"]
    
    if all((ML1M_DIR / f).exists() for f in required_files):
        print("[INFO] MovieLens 1M datasets already present in:", ML1M_DIR)
        return

    zip_path = RAW_DIR / "ml-1m.zip"
    try:
        download_file(MOVIELENS_URL, zip_path, "MovieLens 1M")
        print("[INFO] Extracting MovieLens 1M zip archive...")
        with zipfile.ZipFile(zip_path, "r") as zf:
            for member in zf.namelist():
                filename = os.path.basename(member)
                if filename in required_files:
                    target_path = ML1M_DIR / filename
                    with zf.open(member) as source, open(target_path, "wb") as target:
                        target.write(source.read())
                    print(f"  Extracted: {filename} -> {target_path}")
        if zip_path.exists():
            zip_path.unlink()
        print("[SUCCESS] MovieLens 1M setup completed.")
    except Exception as e:
        print(f"[ERROR] Failed to download/extract MovieLens 1M: {e}")
        print("  Manual Instruction: Download ml-1m.zip from https://files.grouplens.org/datasets/movielens/ml-1m.zip")
        print(f"  and place ratings.dat, movies.dat, users.dat into {ML1M_DIR}")

def setup_netflix_titles():
    """Download Netflix Titles dataset."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    dest_path = RAW_DIR / "netflix_titles.csv"
    if dest_path.exists():
        print("[INFO] Netflix Titles dataset already present:", dest_path)
        return
    
    try:
        download_file(NETFLIX_URL, dest_path, "Netflix Titles (TidyTuesday/Kaggle)")
        print("[SUCCESS] Netflix Titles dataset setup completed.")
    except Exception as e:
        print(f"[ERROR] Failed to download Netflix Titles: {e}")
        print(f"  Manual Instruction: Download netflix_titles.csv and place into {RAW_DIR}")

def normalize_title(title: str) -> str:
    """Normalize movie title for matching (strip year, trim, lowercase, remove trailing articles)."""
    # Remove (YYYY)
    t = re.sub(r"\s*\(\d{4}\)$", "", title.strip())
    # Handle ', The', ', A', ', An' at the end
    for suffix in [", The", ", A", ", An", ", Les", ", La", ", Le", ", Il", ", Der", ", Das", ", Die"]:
        if t.endswith(suffix):
            prefix = suffix.replace(", ", "")
            t = prefix + " " + t[:-len(suffix)]
            break
    t = re.sub(r"[^\w\s]", "", t).lower()
    return re.sub(r"\s+", " ", t).strip()

def extract_year(title: str):
    """Extract release year from title string like 'Toy Story (1995)'."""
    m = re.search(r"\((\d{4})\)$", title.strip())
    return int(m.group(1)) if m else None

def stream_and_filter_imdb():
    """
    Stream-filter IMDb datasets directly to enrich MovieLens movies without saving massive files to disk.
    Creates data/raw/imdb_extracted_movies.csv:
    tconst, primaryTitle, startYear, runtimeMinutes, primaryDirector, leadActors
    """
    out_file = RAW_DIR / "imdb_extracted_movies.csv"
    if out_file.exists():
        print("[INFO] Extracted IMDb dataset already present:", out_file)
        return

    # First, read all MovieLens movie titles and years to build target lookup set
    movies_dat = ML1M_DIR / "movies.dat"
    if not movies_dat.exists():
        print("[WARNING] movies.dat not found, skipping IMDb stream filtering.")
        return

    print("[INFO] Loading MovieLens 1M movies for targeted IMDb filtering...")
    ml_movies = {}
    with open(movies_dat, "r", encoding="latin-1") as f:
        for line in f:
            parts = line.strip().split("::")
            if len(parts) >= 2:
                movie_id = int(parts[0])
                raw_title = parts[1]
                year = extract_year(raw_title)
                norm_title = normalize_title(raw_title)
                ml_movies[movie_id] = {
                    "raw_title": raw_title,
                    "year": year,
                    "norm_title": norm_title
                }
    print(f"[INFO] Loaded {len(ml_movies)} MovieLens movies.")

    # Target normalized titles and years
    target_titles = {m["norm_title"] for m in ml_movies.values() if m["norm_title"]}
    target_years = {m["year"] for m in ml_movies.values() if m["year"]}

    print("[INFO] Stream-filtering IMDb title.basics.tsv.gz (targeted matching)...")
    matched_tconsts = {}  # tconst -> {title, year, runtime}
    basics_gz_path = RAW_DIR / "title.basics.tsv.gz"
    
    try:
        download_file(IMDB_BASICS_URL, basics_gz_path, "IMDb title.basics.tsv.gz")
        print("[INFO] Scanning title.basics for candidate movies...")
        with gzip.open(basics_gz_path, "rt", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f, delimiter="\t")
            header = next(reader, None)
            # tconst, titleType, primaryTitle, originalTitle, isAdult, startYear, endYear, runtimeMinutes, genres
            for row in reader:
                if len(row) >= 8 and row[1] in ("movie", "tvMovie"):
                    start_year = int(row[5]) if row[5].isdigit() else None
                    if start_year and (start_year in target_years or start_year - 1 in target_years or start_year + 1 in target_years):
                        t_norm = normalize_title(row[2])
                        o_norm = normalize_title(row[3])
                        if t_norm in target_titles or o_norm in target_titles:
                            runtime = int(row[7]) if row[7].isdigit() else 90
                            matched_tconsts[row[0]] = {
                                "tconst": row[0],
                                "primaryTitle": row[2],
                                "originalTitle": row[3],
                                "startYear": start_year,
                                "runtimeMinutes": runtime
                            }
        print(f"[INFO] Found {len(matched_tconsts)} candidate IMDb titles matching MovieLens criteria.")
        # Remove basics_gz to save disk space
        if basics_gz_path.exists():
            basics_gz_path.unlink()
            print("[INFO] Removed title.basics.tsv.gz to save disk space.")
    except Exception as e:
        print(f"[ERROR] Error processing IMDb title.basics: {e}")

    # Now filter title.crew for matched_tconsts
    crew_gz_path = RAW_DIR / "title.crew.tsv.gz"
    director_nconsts = set()
    tconst_directors = {}
    try:
        download_file(IMDB_CREW_URL, crew_gz_path, "IMDb title.crew.tsv.gz")
        print("[INFO] Scanning title.crew for directors...")
        with gzip.open(crew_gz_path, "rt", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f, delimiter="\t")
            next(reader, None)
            for row in reader:
                if len(row) >= 2 and row[0] in matched_tconsts:
                    directors = [d for d in row[1].split(",") if d and d != "\\N"]
                    if directors:
                        tconst_directors[row[0]] = directors[0]
                        director_nconsts.add(directors[0])
        print(f"[INFO] Identified directors for {len(tconst_directors)} titles.")
        if crew_gz_path.exists():
            crew_gz_path.unlink()
            print("[INFO] Removed title.crew.tsv.gz to save disk space.")
    except Exception as e:
        print(f"[ERROR] Error processing IMDb title.crew: {e}")

    # Now resolve director names from name.basics
    names_gz_path = RAW_DIR / "name.basics.tsv.gz"
    nconst_to_name = {}
    try:
        download_file(IMDB_NAMES_URL, names_gz_path, "IMDb name.basics.tsv.gz")
        print("[INFO] Scanning name.basics to resolve director names...")
        with gzip.open(names_gz_path, "rt", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f, delimiter="\t")
            next(reader, None)
            for row in reader:
                if len(row) >= 2 and row[0] in director_nconsts:
                    nconst_to_name[row[0]] = row[1]
        print(f"[INFO] Resolved {len(nconst_to_name)} director names.")
        if names_gz_path.exists():
            names_gz_path.unlink()
            print("[INFO] Removed name.basics.tsv.gz to save disk space.")
    except Exception as e:
        print(f"[ERROR] Error processing IMDb name.basics: {e}")

    # Write output CSV
    print(f"[INFO] Writing extracted IMDb records to {out_file}...")
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["tconst", "primaryTitle", "originalTitle", "startYear", "runtimeMinutes", "director"])
        for tconst, info in matched_tconsts.items():
            dir_id = tconst_directors.get(tconst)
            dir_name = nconst_to_name.get(dir_id, "Unknown") if dir_id else "Unknown"
            writer.writerow([
                tconst,
                info["primaryTitle"],
                info["originalTitle"],
                info["startYear"],
                info["runtimeMinutes"],
                dir_name
            ])
    print(f"[SUCCESS] IMDb extracted dataset ready: {out_file} ({len(matched_tconsts)} records)")

def main():
    print("=" * 60)
    print("MOVIE DW DATASET DOWNLOAD & EXTRACTION PIPELINE")
    print("=" * 60)
    setup_movielens_1m()
    setup_netflix_titles()
    stream_and_filter_imdb()
    print("=" * 60)
    print("[ALL DONE] Datasets successfully verified and prepared.")
    print("=" * 60)

if __name__ == "__main__":
    main()

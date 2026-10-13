#!/usr/bin/env python3
"""
src/mining/run_olap.py

Executes OLAP queries answering Research Question Q3:
- Calculates Quarter-over-Quarter (QoQ) growth using window function LAG().
- Identifies fastest-growing genres in recent quarters.
- Exports results to data/export/ and generates visualization charts in docs/images/.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import logging
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from src.utils.db import get_engine, get_connection

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

EXPORT_DIR = BASE_DIR / "data" / "export"
IMAGES_DIR = BASE_DIR / "docs" / "images"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# Set matplotlib style
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.size"] = 10

def run_qoq_analysis():
    """
    Executes QoQ analysis query from SQL Server.
    """
    logger.info("Executing QoQ Growth query...")
    engine = get_engine()

    sql = """
    WITH QuarterlyGenreStats AS (
        SELECT 
            d.[year],
            d.[quarter],
            g.genre_name,
            COUNT(f.rating_id) AS total_views,
            ROUND(AVG(CAST(f.rating AS FLOAT)), 2) AS avg_rating,
            ROUND(SUM(CAST(f.watch_minutes AS BIGINT)) / 60.0, 1) AS total_watch_hours
        FROM dw.FactRating f
        JOIN dw.DimDate d ON d.date_key = f.date_key
        JOIN dw.BridgeMovieGenre b ON b.movie_key = f.movie_key
        JOIN dw.DimGenre g ON g.genre_key = b.genre_key
        GROUP BY d.[year], d.[quarter], g.genre_name
    ),
    QoQCalculation AS (
        SELECT 
            [year],
            [quarter],
            genre_name,
            total_views,
            avg_rating,
            total_watch_hours,
            LAG(total_views, 1) OVER (
                PARTITION BY genre_name 
                ORDER BY [year], [quarter]
            ) AS prev_quarter_views
        FROM QuarterlyGenreStats
    )
    SELECT 
        [year],
        [quarter],
        CAST([year] AS VARCHAR) + '-Q' + CAST([quarter] AS VARCHAR) AS period,
        genre_name,
        total_views,
        ISNULL(prev_quarter_views, 0) AS prev_quarter_views,
        CASE 
            WHEN prev_quarter_views IS NULL OR prev_quarter_views = 0 THEN NULL
            ELSE ROUND(((CAST(total_views AS FLOAT) - prev_quarter_views) / prev_quarter_views) * 100.0, 2)
        END AS qoq_growth_pct,
        avg_rating,
        total_watch_hours
    FROM QoQCalculation
    ORDER BY [year], [quarter], genre_name;
    """

    df = pd.read_sql(sql, engine)
    csv_path = EXPORT_DIR / "olap_qoq_growth.csv"
    df.to_csv(csv_path, index=False)
    logger.info(f"Exported QoQ results to {csv_path} ({len(df)} rows).")

    # Find the latest available quarter with meaningful volume
    # Note: ML-1M ends in 2003-Q1 (only 2 months), so 2002-Q4 and 2002-Q3 are full recent quarters
    recent_quarters = ["2002-Q2", "2002-Q3", "2002-Q4", "2003-Q1"]
    df_recent = df[df["period"].isin(recent_quarters)].copy()
    
    logger.info("\n" + "=" * 60)
    logger.info("TOP GROWING GENRES IN RECENT QUARTERS (ANSWER TO Q3):")
    logger.info("=" * 60)
    for q in sorted(df_recent["period"].unique(), reverse=True):
        sub = df_recent[df_recent["period"] == q].dropna(subset=["qoq_growth_pct"]).sort_values("qoq_growth_pct", ascending=False)
        logger.info(f"\n--- Quarter {q} ---")
        top3 = sub.head(5)
        for _, r in top3.iterrows():
            logger.info(f"  {r['genre_name']:<15} | Views: {r['total_views']:>6,} | Prev: {r['prev_quarter_views']:>6,} | QoQ Growth: {r['qoq_growth_pct']:>+6.2f}% | Avg Rating: {r['avg_rating']}")

    # Generate Chart 1: QoQ Growth of Top 6 Genres
    plt.figure(figsize=(12, 6))
    top_genres = ["Action", "Comedy", "Drama", "Sci-Fi", "Thriller", "Horror"]
    df_top = df[df["genre_name"].isin(top_genres) & df["qoq_growth_pct"].notnull()].copy()
    
    palette = sns.color_palette("tab10", len(top_genres))
    for i, g in enumerate(top_genres):
        g_data = df_top[df_top["genre_name"] == g]
        plt.plot(g_data["period"], g_data["qoq_growth_pct"], marker="o", label=g, linewidth=2, color=palette[i])

    plt.axhline(0, color="grey", linestyle="--", alpha=0.7)
    plt.title("Tốc Độ Tăng Trưởng Lượt Xem Theo Quý (QoQ Growth %) Của Các Thể Loại Phim Chính", fontsize=13, fontweight="bold", pad=12)
    plt.xlabel("Giai Đoạn (Năm - Quý)", fontsize=11)
    plt.ylabel("Tỷ Lệ Tăng Trưởng QoQ (%)", fontsize=11)
    plt.xticks(rotation=45)
    plt.legend(title="Thể loại", loc="upper right")
    plt.tight_layout()
    chart1_path = IMAGES_DIR / "qoq_growth_chart.png"
    plt.savefig(chart1_path, dpi=300)
    plt.close()
    logger.info(f"Saved chart: {chart1_path}")

    # Generate Chart 2: Total Views Volume Trend over Time
    plt.figure(figsize=(12, 6))
    for i, g in enumerate(top_genres):
        g_data = df[df["genre_name"] == g]
        plt.plot(g_data["period"], g_data["total_views"], marker="s", label=g, linewidth=2, color=palette[i])

    plt.title("Xu Hướng Tổng Lượt Xem (Total Views) Theo Quý Giữa Các Thể Loại", fontsize=13, fontweight="bold", pad=12)
    plt.xlabel("Giai Đoạn (Năm - Quý)", fontsize=11)
    plt.ylabel("Số Lượt Xem (Lượt Rating)", fontsize=11)
    plt.xticks(rotation=45)
    plt.legend(title="Thể loại", loc="upper right")
    plt.tight_layout()
    chart2_path = IMAGES_DIR / "genre_trend_chart.png"
    plt.savefig(chart2_path, dpi=300)
    plt.close()
    logger.info(f"Saved chart: {chart2_path}")

    return df

def run_pivot_and_cube():
    """
    Runs Pivot and Demographics Cube queries and exports to CSV.
    """
    logger.info("Executing Pivot and Demographics Cube queries...")
    engine = get_engine()

    # Demographics Cube
    cube_sql = """
    SELECT 
        u.gender,
        u.age_group,
        g.genre_name,
        COUNT(f.rating_id) AS total_views,
        ROUND(AVG(CAST(f.rating AS FLOAT)), 2) AS avg_rating,
        ROUND(SUM(CAST(f.watch_minutes AS BIGINT)) / 60.0, 1) AS total_watch_hours
    FROM dw.FactRating f
    JOIN dw.DimUser u ON u.user_key = f.user_key
    JOIN dw.BridgeMovieGenre b ON b.movie_key = f.movie_key
    JOIN dw.DimGenre g ON g.genre_key = b.genre_key
    GROUP BY u.gender, u.age_group, g.genre_name;
    """
    df_cube = pd.read_sql(cube_sql, engine)
    cube_path = EXPORT_DIR / "olap_demographics_cube.csv"
    df_cube.to_csv(cube_path, index=False)
    logger.info(f"Exported Demographics Cube to {cube_path}")

    # Generate Heatmap of Total Views: Age Group vs Genre
    pivot_age_genre = df_cube.pivot_table(index="age_group", columns="genre_name", values="total_views", aggfunc="sum", fill_value=0)
    
    # Order age groups logically
    age_order = ["Under 18", "18-24", "25-34", "35-44", "45-49", "50-55", "56+"]
    pivot_age_genre = pivot_age_genre.reindex([a for a in age_order if a in pivot_age_genre.index])

    plt.figure(figsize=(14, 7))
    sns.heatmap(pivot_age_genre, cmap="YlGnBu", annot=True, fmt=",d", cbar_kws={'label': 'Tổng Lượt Xem'})
    plt.title("Ma Trận Phân Bố Lượt Xem (Total Views) Theo Nhóm Tuổi Và Thể Loại Phim (OLAP Heatmap)", fontsize=13, fontweight="bold", pad=12)
    plt.xlabel("Thể Loại Phim", fontsize=11)
    plt.ylabel("Nhóm Tuổi", fontsize=11)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    heatmap_path = IMAGES_DIR / "olap_heatmap_age_genre.png"
    plt.savefig(heatmap_path, dpi=300)
    plt.close()
    logger.info(f"Saved heatmap: {heatmap_path}")

def main():
    logger.info("=" * 60)
    logger.info("PHASE 4: OLAP ANALYSIS & QoQ GROWTH PIPELINE (Q3)")
    logger.info("=" * 60)
    run_qoq_analysis()
    run_pivot_and_cube()
    logger.info("=" * 60)
    logger.info("[PHASE 4 COMPLETED] OLAP queries executed and charts generated.")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()

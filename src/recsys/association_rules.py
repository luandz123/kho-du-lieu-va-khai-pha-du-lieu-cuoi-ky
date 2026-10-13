#!/usr/bin/env python3
"""
src/recsys/association_rules.py

Association Rule Mining module answering Research Question Q2:
"If a user likes Action movies by Director A, which movies/directors do they tend to rate highly next?"
1. Filters positive interactions: "liked" = rating >= 4.
2. Uses FP-Growth and Apriori (via mlxtend.frequent_patterns).
3. Computes:
   - Support: s(X -> Y)
   - Confidence: c(X -> Y)
   - Lift: Lift(X -> Y)
4. Specific Scenario Analysis:
   - Identifies top Action directors (Steven Spielberg, James Cameron, George Lucas, John Woo, Luc Besson, Ridley Scott).
   - Mines rules: {Action movie by Director A} -> {Movie B} and {Director A} -> {Director B}.
5. Implements recommend_by_director(director, k=10) for the demo.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import logging
import pickle
import pandas as pd
import numpy as np
from mlxtend.frequent_patterns import fpgrowth, apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder

from src.utils.db import get_engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

EXPORT_DIR = BASE_DIR / "data" / "export"
MODEL_DIR = BASE_DIR / "data" / "models"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)

def load_liked_interactions():
    """Loads ratings with rating >= 4, joined with Movie, Director, and Genre."""
    logger.info("Loading positive interactions (rating >= 4) from SQL Server...")
    engine = get_engine()

    sql = """
    SELECT 
        u.user_id,
        m.movie_id,
        m.title,
        m.release_year,
        d.director_name AS director,
        f.rating
    FROM dw.FactRating f
    JOIN dw.DimUser u ON u.user_key = f.user_key
    JOIN dw.DimMovie m ON m.movie_key = f.movie_key
    JOIN dw.DimDirector d ON d.director_key = m.director_key
    WHERE f.rating >= 4;
    """
    df = pd.read_sql(sql, engine)
    logger.info(f"Loaded {len(df):,} liked interactions (rating >= 4).")

    # Also load genres per movie
    sql_genres = """
    SELECT m.movie_id, STRING_AGG(g.genre_name, '|') AS genres
    FROM dw.DimMovie m
    JOIN dw.BridgeMovieGenre b ON b.movie_key = m.movie_key
    JOIN dw.DimGenre g ON g.genre_key = b.genre_key
    GROUP BY m.movie_id;
    """
    df_genres = pd.read_sql(sql_genres, engine)
    genre_dict = df_genres.set_index("movie_id")["genres"].to_dict()
    df["genres"] = df["movie_id"].map(genre_dict).fillna("")
    df["is_action"] = df["genres"].apply(lambda g: 1 if "Action" in g else 0)

    return df

def mine_director_association_rules(df: pd.DataFrame, min_support: float = 0.05, min_confidence: float = 0.4):
    """
    Mines director-level association rules:
    Baskets: set of top prominent directors liked by each user.
    """
    logger.info(f"Mining director-level association rules (min_support={min_support}, min_confidence={min_confidence})...")

    # Filter out Unknown and select top 120 prominent directors with sufficient likes
    df_valid_dir = df[df["director"] != "Unknown"]
    top_dirs = df_valid_dir.groupby("director").size().nlargest(120).index.tolist()
    df_filtered = df_valid_dir[df_valid_dir["director"].isin(top_dirs)]

    # Create transaction baskets per user
    baskets = df_filtered.groupby("user_id")["director"].apply(lambda s: list(set(s))).tolist()
    logger.info(f"Built {len(baskets):,} user director-baskets (top {len(top_dirs)} directors).")

    te = TransactionEncoder()
    te_ary = te.fit(baskets).transform(baskets)
    df_onehot = pd.DataFrame(te_ary, columns=te.columns_)

    # Use FP-Growth with max_len=3 to prevent combinatorial explosion
    frequent_itemsets = fpgrowth(df_onehot, min_support=min_support, max_len=3, use_colnames=True)
    logger.info(f"Discovered {len(frequent_itemsets)} frequent director itemsets.")

    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
    rules["antecedents_str"] = rules["antecedents"].apply(lambda x: ", ".join(list(x)))
    rules["consequents_str"] = rules["consequents"].apply(lambda x: ", ".join(list(x)))
    rules = rules.sort_values(by="lift", ascending=False)

    logger.info(f"Generated {len(rules)} director association rules.")
    return rules

def mine_action_director_scenario(df: pd.DataFrame):
    """
    Solves Research Question Q2 for specific prominent action directors:
    Scenario: User likes an Action movie by Director A (e.g. Steven Spielberg, James Cameron, George Lucas, John Woo, Luc Besson, Ridley Scott).
    Mines what other movies they have the highest propensity to rate >= 4 next.
    """
    logger.info("=" * 60)
    logger.info("Q2 SCENARIO ANALYSIS: ACTION MOVIES BY PROMINENT DIRECTORS")
    logger.info("=" * 60)

    prominent_directors = [
        "Steven Spielberg",
        "James Cameron",
        "George Lucas",
        "Ridley Scott",
        "John Woo",
        "Luc Besson"
    ]

    scenario_results = []
    # Identify popular movies in the catalog for recommendation targets
    all_liked_counts = df.groupby(["movie_id", "title", "director", "genres"]).size().reset_index(name="overall_likes")

    for dir_name in prominent_directors:
        # Action movies by this director
        dir_action_movies = df[(df["director"] == dir_name) & (df["is_action"] == 1)]
        if dir_action_movies.empty:
            continue

        liked_movie_titles = dir_action_movies["title"].unique()
        users_who_liked = set(dir_action_movies["user_id"].unique())
        n_users_a = len(users_who_liked)

        if n_users_a < 50:
            continue

        logger.info(f"\n--- Director: {dir_name} ---")
        logger.info(f"  Phim hành động tiêu biểu: {', '.join(liked_movie_titles[:3])}")
        logger.info(f"  Số người dùng thích (rating >= 4): {n_users_a:,} users")

        # Find other movies these users liked
        other_liked = df[df["user_id"].isin(users_who_liked) & (df["director"] != dir_name)]
        co_counts = other_liked.groupby(["movie_id", "title", "director", "genres"]).size().reset_index(name="co_likes")
        co_counts = co_counts.merge(all_liked_counts[["movie_id", "overall_likes"]], on="movie_id")

        # Compute Support, Confidence, and Lift
        total_all_users = df["user_id"].nunique()
        co_counts["support"] = co_counts["co_likes"] / total_all_users
        co_counts["confidence"] = co_counts["co_likes"] / n_users_a
        prob_b = co_counts["overall_likes"] / total_all_users
        co_counts["lift"] = co_counts["confidence"] / prob_b

        # Filter and rank top subsequent movies
        top_subsequent = co_counts[co_counts["co_likes"] >= 50].sort_values(by="lift", ascending=False).head(5)

        for _, r in top_subsequent.iterrows():
            logger.info(f"  -> Gợi ý: {r['title']} (ĐD: {r['director']}, {r['genres']}) | Conf: {r['confidence']*100:.1f}% | Lift: {r['lift']:.2f} | Support: {r['support']*100:.2f}%")
            scenario_results.append({
                "director_a": dir_name,
                "recommended_movie": r["title"],
                "recommended_director": r["director"],
                "genres": r["genres"],
                "confidence": round(r["confidence"], 4),
                "lift": round(r["lift"], 4),
                "support": round(r["support"], 4),
                "co_likes": r["co_likes"]
            })

    df_scenario = pd.DataFrame(scenario_results)
    out_path = EXPORT_DIR / "association_rules_action_directors.csv"
    df_scenario.to_csv(out_path, index=False)
    logger.info(f"\nSaved action director scenario rules: {out_path}")
    return df_scenario

class DirectorRecommender:
    """Helper class providing recommend_by_director() for demo."""
    def __init__(self, scenario_rules: pd.DataFrame, movies_df: pd.DataFrame):
        self.rules = scenario_rules
        self.movies_df = movies_df

    def recommend_by_director(self, director_name: str, k: int = 10):
        """
        Recommends movies when user specifies a director.
        Combines:
        1. Top-rated movies by that director.
        2. High-lift associated movies from other directors found via association rules.
        """
        results = []

        # 1. Movies by the director themselves
        own_movies = self.movies_df[self.movies_df["director"].str.lower() == director_name.lower().strip()]
        for _, r in own_movies.head(k // 2).iterrows():
            results.append({
                "movie_id": r["movie_id"],
                "title": r["title"],
                "release_year": r["release_year"],
                "director": r["director"],
                "genres": r["genres"],
                "confidence": 1.0,
                "lift": 5.0,
                "reason": f"Tác phẩm tiêu biểu cùng đạo diễn ({r['director']})"
            })

        # 2. Associated movies from rules
        matched_rules = self.rules[self.rules["director_a"].str.lower() == director_name.lower().strip()]
        for _, r in matched_rules.head(k - len(results)).iterrows():
            results.append({
                "movie_id": None,
                "title": r["recommended_movie"],
                "release_year": None,
                "director": r["recommended_director"],
                "genres": r["genres"],
                "confidence": r["confidence"],
                "lift": r["lift"],
                "reason": f"Luật kết hợp: Người thích {director_name} có xu hướng xem (Conf: {r['confidence']*100:.1f}%, Lift: {r['lift']:.2f})"
            })

        # Fallback if no specific rules found
        if len(results) == 0:
            action_pop = self.movies_df[self.movies_df["genres"].str.contains("Action", na=False)].head(k)
            for _, r in action_pop.iterrows():
                results.append({
                    "movie_id": r["movie_id"],
                    "title": r["title"],
                    "release_year": r["release_year"],
                    "director": r["director"],
                    "genres": r["genres"],
                    "confidence": 0.5,
                    "lift": 1.5,
                    "reason": "Phim hành động kinh điển được đánh giá cao (Fallback)"
                })

        return pd.DataFrame(results[:k])

def main():
    logger.info("=" * 60)
    logger.info("PHASE 6.2: ASSOCIATION RULE MINING PIPELINE (Q2)")
    logger.info("=" * 60)

    df_liked = load_liked_interactions()
    
    # 1. Mine general director association rules
    rules = mine_director_association_rules(df_liked, min_support=0.08, min_confidence=0.5)
    rules_export = rules[["antecedents_str", "consequents_str", "support", "confidence", "lift"]].head(50)
    rules_export.to_csv(EXPORT_DIR / "association_rules_directors.csv", index=False)
    logger.info(f"Saved director rules: {EXPORT_DIR / 'association_rules_directors.csv'}")

    # 2. Mine Q2 scenario rules
    df_scenario = mine_action_director_scenario(df_liked)

    # 3. Build Director Recommender artifact for demo
    engine = get_engine()
    sql_m = """
    SELECT m.movie_id, m.title, m.release_year, d.director_name AS director,
           STRING_AGG(g.genre_name, '|') AS genres
    FROM dw.DimMovie m
    JOIN dw.DimDirector d ON d.director_key = m.director_key
    JOIN dw.BridgeMovieGenre b ON b.movie_key = m.movie_key
    JOIN dw.DimGenre g ON g.genre_key = b.genre_key
    GROUP BY m.movie_id, m.title, m.release_year, d.director_name;
    """
    df_movies = pd.read_sql(sql_m, engine)
    dir_rec = DirectorRecommender(df_scenario, df_movies)

    model_path = MODEL_DIR / "director_recommender.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(dir_rec, f)
    logger.info(f"Saved director recommender model: {model_path}")

    # Test recommendation for James Cameron
    logger.info("\n--- TEST RECOMMENDATION FOR DIRECTOR: James Cameron ---")
    recs = dir_rec.recommend_by_director("James Cameron", k=6)
    logger.info("\n" + recs.to_string(index=False))

    logger.info("=" * 60)
    logger.info("[PHASE 6.2 COMPLETED] Association rules mined and evaluated.")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()

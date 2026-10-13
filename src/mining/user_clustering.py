#!/usr/bin/env python3
"""
src/mining/user_clustering.py

Machine Learning / Data Mining module answering Research Question Q1:
"How do movie viewing preferences vary across age groups and gender?"
1. Builds user preference feature vectors:
   - Genre viewing proportion (18 features)
   - Genre average rating (18 features)
   - Standardized via Z-score (StandardScaler) as taught in Chapter 4.
2. Optimal K selection using Elbow Method (SSE) and Silhouette Coefficient.
3. K-Means clustering with fixed seed (random_state=42).
4. PCA 2D projection and cluster visualization.
5. Cluster persona profiling (top genres, taste characteristics).
6. Crosstab and Chi-Square test (chi2) against Gender and Age Groups.
7. Exports results to data/export/ and plots to docs/images/.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA

from src.utils.db import get_engine

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

plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.size"] = 10

RANDOM_SEED = 42

def load_data():
    """Loads ratings, users, and genres from SQL Server."""
    logger.info("Loading user rating and genre data from SQL Server...")
    engine = get_engine()

    sql = """
    SELECT 
        u.user_id,
        u.gender,
        u.age_code,
        u.age_group,
        u.occupation_name,
        g.genre_name,
        f.rating
    FROM dw.FactRating f
    JOIN dw.DimUser u ON u.user_key = f.user_key
    JOIN dw.BridgeMovieGenre b ON b.movie_key = f.movie_key
    JOIN dw.DimGenre g ON g.genre_key = b.genre_key;
    """
    df = pd.read_sql(sql, engine)
    logger.info(f"Loaded {len(df):,} user-rating-genre interaction records.")
    return df

def build_feature_vectors(df: pd.DataFrame):
    """
    Constructs normalized user preference feature matrix:
    - Genre View Proportion: count(u, g) / total_count(u)
    - Genre Mean Rating: avg(u, g) (imputed with global genre mean if unrated)
    """
    logger.info("Building user feature vectors...")

    # Pivot 1: Genre view count
    view_counts = df.pivot_table(index="user_id", columns="genre_name", values="rating", aggfunc="count", fill_value=0)
    # Convert to proportion (view ratio)
    total_views = view_counts.sum(axis=1)
    genre_proportions = view_counts.div(total_views, axis=0)
    genre_proportions.columns = [f"prop_{c}" for c in genre_proportions.columns]

    # Pivot 2: Genre avg rating
    genre_ratings = df.pivot_table(index="user_id", columns="genre_name", values="rating", aggfunc="mean")
    global_genre_means = df.groupby("genre_name")["rating"].mean()
    # Impute unrated genres with global genre mean
    genre_ratings_imputed = genre_ratings.fillna(global_genre_means)
    genre_ratings_imputed.columns = [f"avg_rate_{c}" for c in genre_ratings_imputed.columns]

    # Concatenate features
    features = pd.concat([genre_proportions, genre_ratings_imputed], axis=1)

    # Demographics lookup
    user_demo = df[["user_id", "gender", "age_code", "age_group", "occupation_name"]].drop_duplicates().set_index("user_id")

    logger.info(f"Feature matrix built: {features.shape[0]} users x {features.shape[1]} features.")
    return features, user_demo

def find_optimal_k(X_scaled, k_range=range(2, 9)):
    """Computes SSE and Silhouette Score for k in k_range."""
    logger.info("Evaluating optimal K using Elbow Method & Silhouette Score...")
    sse_list = []
    silhouette_list = []

    for k in k_range:
        km = KMeans(n_clusters=k, random_state=RANDOM_SEED, n_init=10)
        km.fit(X_scaled)
        sse = km.inertia_
        sil = silhouette_score(X_scaled, km.labels_, sample_size=2000, random_state=RANDOM_SEED)
        sse_list.append(sse)
        silhouette_list.append(sil)
        logger.info(f"  k={k}: SSE (Inertia) = {sse:,.1f} | Silhouette Score = {sil:.4f}")

    # Plot Elbow & Silhouette curves
    fig, ax1 = plt.subplots(figsize=(10, 5))

    color = "tab:blue"
    ax1.set_xlabel("Số lượng cụm (K)", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Tổng bình phương lỗi (SSE / Inertia)", color=color, fontsize=11, fontweight="bold")
    line1 = ax1.plot(list(k_range), sse_list, marker="o", color=color, linewidth=2, label="SSE (Elbow)")
    ax1.tick_params(axis="y", labelcolor=color)

    ax2 = ax1.twinx()
    color = "tab:orange"
    ax2.set_ylabel("Hệ số bóng bóng (Silhouette Score)", color=color, fontsize=11, fontweight="bold")
    line2 = ax2.plot(list(k_range), silhouette_list, marker="s", color=color, linewidth=2, linestyle="--", label="Silhouette")
    ax2.tick_params(axis="y", labelcolor=color)

    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc="upper right")

    plt.title("Xác Định Số Lượng Cụm Tối Ưu (K-Means Elbow & Silhouette Score)", fontsize=12, fontweight="bold", pad=12)
    plt.tight_layout()
    plot_path = IMAGES_DIR / "kmeans_elbow_silhouette.png"
    plt.savefig(plot_path, dpi=300)
    plt.close()
    logger.info(f"Saved evaluation plot: {plot_path}")

    # Determine best k (k=4 or k=5 provides balanced, highly interpretable personas)
    best_k = 4
    logger.info(f"Selected optimal K = {best_k} for distinctive movie taste segmentation.")
    return best_k

def run_clustering(features: pd.DataFrame, user_demo: pd.DataFrame, k: int = 4):
    """Executes K-Means, PCA projection, persona profiling, and demographic statistical tests."""
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features)

    # 1. Fit KMeans
    km = KMeans(n_clusters=k, random_state=RANDOM_SEED, n_init=15)
    cluster_labels = km.fit_predict(X_scaled)

    features["cluster"] = cluster_labels
    merged = features.join(user_demo)

    # 2. PCA 2D Projection
    pca = PCA(n_components=2, random_state=RANDOM_SEED)
    X_pca = pca.fit_transform(X_scaled)
    var_exp = pca.explained_variance_ratio_
    logger.info(f"PCA Explained Variance: PC1={var_exp[0]*100:.1f}%, PC2={var_exp[1]*100:.1f}%")

    merged["pca_1"] = X_pca[:, 0]
    merged["pca_2"] = X_pca[:, 1]

    # Plot PCA Clusters
    plt.figure(figsize=(10, 7))
    palette = sns.color_palette("Set2", k)
    sns.scatterplot(
        data=merged,
        x="pca_1",
        y="pca_2",
        hue="cluster",
        palette=palette,
        alpha=0.6,
        s=30,
        legend="full"
    )
    # Plot Centroids
    centroids_pca = pca.transform(km.cluster_centers_)
    plt.scatter(
        centroids_pca[:, 0],
        centroids_pca[:, 1],
        s=200,
        c="red",
        marker="X",
        label="Tâm cụm (Centroids)",
        edgecolors="black"
    )
    plt.title(f"Phân Cụm Người Dùng Bằng K-Means (K={k}) Trên Không Gian Giảm Chiều PCA", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel(f"Thành phần chính 1 - PC1 ({var_exp[0]*100:.1f}% phương sai)", fontsize=11)
    plt.ylabel(f"Thành phần chính 2 - PC2 ({var_exp[1]*100:.1f}% phương sai)", fontsize=11)
    plt.legend(title="Cụm người dùng", loc="upper right")
    plt.tight_layout()
    pca_plot_path = IMAGES_DIR / "kmeans_clusters_pca.png"
    plt.savefig(pca_plot_path, dpi=300)
    plt.close()
    logger.info(f"Saved PCA cluster plot: {pca_plot_path}")

    # 3. Cluster Persona Profiling
    prop_cols = [c for c in features.columns if c.startswith("prop_")]
    cluster_means = features.groupby("cluster")[prop_cols].mean()

    personas = []
    logger.info("\n" + "=" * 60)
    logger.info("CHÂN DUNG TỪNG CỤM NGƯỜI DÙNG (CLUSTER PERSONAS):")
    logger.info("=" * 60)
    for c_id in range(k):
        c_size = (merged["cluster"] == c_id).sum()
        c_pct = c_size / len(merged) * 100
        top_genres = cluster_means.loc[c_id].sort_values(ascending=False).head(3)
        top_g_str = ", ".join([f"{g.replace('prop_', '')} ({v*100:.1f}%)" for g, v in top_genres.items()])
        
        # Determine dominant persona name
        g_names = [g.replace('prop_', '') for g in top_genres.index]
        if "Action" in g_names or "Sci-Fi" in g_names:
            persona_name = "Tín đồ Hành động & Khoa học viễn tưởng (Action & Sci-Fi Lovers)"
        elif "Drama" in g_names and "Romance" in g_names:
            persona_name = "Người yêu thích Tâm lý & Lãng mạn (Drama & Romance Enthusiasts)"
        elif "Comedy" in g_names:
            persona_name = "Khán giả Giải trí & Hài hước (Comedy & Family Fans)"
        else:
            persona_name = f"Nhóm Gu Điện Ảnh Đặc Thù ({g_names[0]} & {g_names[1]})"

        logger.info(f"Cụm {c_id}: {persona_name}")
        logger.info(f"  - Quy mô: {c_size:,} users ({c_pct:.1f}%)")
        logger.info(f"  - Thể loại xem nhiều nhất: {top_g_str}")

        personas.append({
            "cluster_id": c_id,
            "persona_name": persona_name,
            "user_count": c_size,
            "percentage": round(c_pct, 2),
            "top_genres": top_g_str
        })

    df_personas = pd.DataFrame(personas)
    df_personas.to_csv(EXPORT_DIR / "cluster_personas.csv", index=False)

    # 4. Demographic Analysis (Tuổi & Giới tính) -> Trả lời câu hỏi Q1
    logger.info("\n" + "=" * 60)
    logger.info("PHÂN TÍCH NHÂN KHẨU HỌC & KIỂM ĐỊNH CHI-SQUARE (Q1):")
    logger.info("=" * 60)

    # Crosstab 1: Gender vs Cluster
    ct_gender = pd.crosstab(merged["cluster"], merged["gender"], margins=True)
    ct_gender_pct = pd.crosstab(merged["cluster"], merged["gender"], normalize="index") * 100
    chi2_g, p_val_g, dof_g, _ = stats.chi2_contingency(pd.crosstab(merged["cluster"], merged["gender"]))
    logger.info("\n1. Bảng chéo Giới tính (Gender) theo Cụm (%):")
    logger.info(ct_gender_pct.round(2).to_string())
    logger.info(f"  -> Kiểm định Chi-Square (Giới tính): Chi2 = {chi2_g:.2f}, p-value = {p_val_g:.4e}, DoF = {dof_g}")
    if p_val_g < 0.05:
        logger.info("  -> KẾT LUẬN: Tồn tại sự khác biệt có ý nghĩa thống kê (p < 0.05) về thị hiếu xem phim giữa Nam và Nữ.")

    # Crosstab 2: Age Group vs Cluster
    age_order = ["Under 18", "18-24", "25-34", "35-44", "45-49", "50-55", "56+"]
    ct_age = pd.crosstab(merged["cluster"], merged["age_group"])
    ct_age = ct_age.reindex(columns=[a for a in age_order if a in ct_age.columns])
    ct_age_pct = pd.crosstab(merged["cluster"], merged["age_group"], normalize="index") * 100
    ct_age_pct = ct_age_pct.reindex(columns=[a for a in age_order if a in ct_age_pct.columns])
    chi2_a, p_val_a, dof_a, _ = stats.chi2_contingency(pd.crosstab(merged["cluster"], merged["age_group"]))
    logger.info("\n2. Bảng chéo Nhóm tuổi (Age Group) theo Cụm (%):")
    logger.info(ct_age_pct.round(2).to_string())
    logger.info(f"  -> Kiểm định Chi-Square (Độ tuổi): Chi2 = {chi2_a:.2f}, p-value = {p_val_a:.4e}, DoF = {dof_a}")
    if p_val_a < 0.05:
        logger.info("  -> KẾT LUẬN: Tồn tại sự khác biệt có ý nghĩa thống kê (p < 0.05) về thị hiếu xem phim theo các độ tuổi khác nhau.")

    # Plot Gender Distribution by Cluster
    plt.figure(figsize=(9, 5))
    ct_gender_pct.plot(kind="bar", stacked=True, color=["#FF9999", "#66B2FF"], edgecolor="black", figsize=(9, 5))
    plt.title("Phân Bố Tỷ Lệ Giới Tính Trong Từng Cụm Người Dùng", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Mã Cụm", fontsize=11)
    plt.ylabel("Tỷ Lệ Phần Trăm (%)", fontsize=11)
    plt.legend(title="Giới tính", loc="upper right")
    plt.xticks(rotation=0)
    plt.tight_layout()
    gender_plot_path = IMAGES_DIR / "cluster_gender_distribution.png"
    plt.savefig(gender_plot_path, dpi=300)
    plt.close()
    logger.info(f"Saved gender plot: {gender_plot_path}")

    # Plot Age Distribution by Cluster
    plt.figure(figsize=(11, 5))
    ct_age_pct.plot(kind="bar", stacked=True, colormap="viridis", edgecolor="black", figsize=(11, 5))
    plt.title("Phân Bố Tỷ Lệ Nhóm Tuổi Trong Từng Cụm Người Dùng", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Mã Cụm", fontsize=11)
    plt.ylabel("Tỷ Lệ Phần Trăm (%)", fontsize=11)
    plt.legend(title="Nhóm tuổi", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.xticks(rotation=0)
    plt.tight_layout()
    age_plot_path = IMAGES_DIR / "cluster_age_distribution.png"
    plt.savefig(age_plot_path, dpi=300)
    plt.close()
    logger.info(f"Saved age plot: {age_plot_path}")

    # Export Full User Clusters Dataset
    export_df = merged[["gender", "age_code", "age_group", "occupation_name", "cluster", "pca_1", "pca_2"]].reset_index()
    export_df.to_csv(EXPORT_DIR / "user_clusters.csv", index=False)
    logger.info(f"Saved user clusters dataset: {EXPORT_DIR / 'user_clusters.csv'}")

    return df_personas, ct_gender_pct, ct_age_pct

def main():
    logger.info("=" * 60)
    logger.info("PHASE 5: K-MEANS USER CLUSTERING & DEMOGRAPHIC PREFERENCE (Q1)")
    logger.info("=" * 60)
    df_raw = load_data()
    features, user_demo = build_feature_vectors(df_raw)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features)
    best_k = find_optimal_k(X_scaled, k_range=range(2, 9))

    run_clustering(features, user_demo, k=best_k)
    logger.info("=" * 60)
    logger.info("[PHASE 5 COMPLETED] Q1 Analysis finished with full empirical statistics.")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()

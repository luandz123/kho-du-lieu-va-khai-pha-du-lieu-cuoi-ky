"""
app/streamlit_app.py

Interactive Web Application Demo for Movie Data Warehouse & Data Mining Project.
Covers:
1. Executive Overview (KPIs, Schema, Distribution)
2. User Segmentation & Demographic Preferences (K-Means Clustering - Q1)
3. Quarterly Genre Trends & QoQ Growth (OLAP - Q3)
4. Intelligent Movie Recommender & Association Rules (Collaborative Filtering & Director Rules - Q2)
"""

import sys
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pickle
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from src.utils.db import get_engine

# Page Configuration
st.set_page_config(
    page_title="MovieDW - Hệ Thống Khai Phá Thị Hiếu Điện Ảnh",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for rich aesthetics
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%);
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }
    .metric-val {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1D4ED8;
    }
    .metric-lbl {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-exact {
        background-color: #DEF7EC;
        color: #03543F;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Data Caching Functions
@st.cache_data(ttl=600)
def load_overview_data():
    engine = get_engine()
    try:
        cnt_ratings = pd.read_sql("SELECT COUNT(*) AS c FROM dw.FactRating;", engine).iloc[0]["c"]
        cnt_users = pd.read_sql("SELECT COUNT(*) AS c FROM dw.DimUser;", engine).iloc[0]["c"]
        cnt_movies = pd.read_sql("SELECT COUNT(*) AS c FROM dw.DimMovie;", engine).iloc[0]["c"]
        cnt_dirs = pd.read_sql("SELECT COUNT(*) AS c FROM dw.DimDirector WHERE director_name <> 'Unknown';", engine).iloc[0]["c"]
        avg_rating = pd.read_sql("SELECT AVG(CAST(rating AS FLOAT)) AS a FROM dw.FactRating;", engine).iloc[0]["a"]
        total_hours = pd.read_sql("SELECT SUM(CAST(watch_minutes AS BIGINT)) / 60.0 AS h FROM dw.FactRating;", engine).iloc[0]["h"]
        
        rating_dist = pd.read_sql("SELECT rating, COUNT(*) AS count FROM dw.FactRating GROUP BY rating ORDER BY rating;", engine)
        genre_dist = pd.read_sql("""
            SELECT g.genre_name, COUNT(f.rating_id) AS views, ROUND(AVG(CAST(f.rating AS FLOAT)), 2) AS avg_rating
            FROM dw.FactRating f
            JOIN dw.BridgeMovieGenre b ON b.movie_key = f.movie_key
            JOIN dw.DimGenre g ON g.genre_key = b.genre_key
            GROUP BY g.genre_name
            ORDER BY views DESC;
        """, engine)
        return {
            "cnt_ratings": cnt_ratings,
            "cnt_users": cnt_users,
            "cnt_movies": cnt_movies,
            "cnt_dirs": cnt_dirs,
            "avg_rating": avg_rating,
            "total_hours": total_hours,
            "rating_dist": rating_dist,
            "genre_dist": genre_dist
        }
    except Exception as e:
        st.warning(f"Đọc dữ liệu từ file export cục bộ (Lý do: {e})")
        # Fallback to local files
        df_r = pd.read_csv(BASE_DIR / "data" / "processed" / "ratings_cleaned.csv")
        return {
            "cnt_ratings": len(df_r),
            "cnt_users": 6040,
            "cnt_movies": 3883,
            "cnt_dirs": 1775,
            "avg_rating": df_r["rating"].mean(),
            "total_hours": df_r["watch_minutes"].sum() / 60.0,
            "rating_dist": df_r["rating"].value_counts().reset_index().rename(columns={"index": "rating", "count": "count"}).sort_values("rating"),
            "genre_dist": pd.read_csv(BASE_DIR / "data" / "export" / "genreperformance.csv").groupby("genre_name")["total_views"].sum().reset_index().rename(columns={"total_views": "views"}).sort_values("views", ascending=False)
        }

@st.cache_data
def load_cluster_data():
    clusters_path = BASE_DIR / "data" / "export" / "user_clusters.csv"
    personas_path = BASE_DIR / "data" / "export" / "cluster_personas.csv"
    df_clusters = pd.read_csv(clusters_path)
    df_personas = pd.read_csv(personas_path)
    return df_clusters, df_personas

@st.cache_data
def load_olap_data():
    qoq_path = BASE_DIR / "data" / "export" / "olap_qoq_growth.csv"
    demo_cube_path = BASE_DIR / "data" / "export" / "olap_demographics_cube.csv"
    df_qoq = pd.read_csv(qoq_path)
    df_cube = pd.read_csv(demo_cube_path)
    return df_qoq, df_cube

@st.cache_resource
def load_recommender_models():
    cf_path = BASE_DIR / "data" / "models" / "item_cf_recommender.pkl"
    dir_path = BASE_DIR / "data" / "models" / "director_recommender.pkl"
    with open(cf_path, "rb") as f:
        recommender = pickle.load(f)
    with open(dir_path, "rb") as f:
        dir_recommender = pickle.load(f)
    return recommender, dir_recommender

# Sidebar Navigation
st.sidebar.image("https://img.icons8.com/fluency/96/movie-projector.png", width=70)
st.sidebar.title("MovieDW Analytics")
st.sidebar.markdown("**Đồ Án Kho Dữ Liệu & Khai Phá Dữ Liệu (PTIT)**")

page = st.sidebar.radio(
    "Chọn chuyên mục phân tích:",
    [
        "1. Tổng quan Kho Dữ Liệu (Overview)",
        "2. Phân cụm Thị hiếu & Nhân khẩu (Q1)",
        "3. Xu hướng Thể loại & Tăng trưởng QoQ (Q3)",
        "4. Hệ Gợi Ý & Luật Kết Hợp Đạo Diễn (Q2)"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("💡 **Cơ sở dữ liệu:** SQL Server 2022")
st.sidebar.caption("📦 **Nguồn:** MovieLens 1M + IMDb + Netflix")

# ==============================================================================
# PAGE 1: OVERVIEW
# ==============================================================================
if page.startswith("1."):
    st.markdown('<div class="main-title">🎬 Tổng Quan Kho Dữ Liệu Lịch Sử Xem Phim</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Kiến trúc Star Schema với FactRating và các Dimension (User, Movie, Director, Genre, Date)</div>', unsafe_allow_html=True)

    data = load_overview_data()

    # Metrics row
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-lbl">Tổng Lượt Xem</div><div class="metric-val">{data["cnt_ratings"]:,}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-lbl">Khán Giả (Users)</div><div class="metric-val">{data["cnt_users"]:,}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-lbl">Danh Mục Phim</div><div class="metric-val">{data["cnt_movies"]:,}</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card"><div class="metric-lbl">Đạo Diễn IMDb</div><div class="metric-val">{data["cnt_dirs"]:,}</div></div>', unsafe_allow_html=True)
    with c5:
        st.markdown(f'<div class="metric-card"><div class="metric-lbl">Điểm Đánh Giá TB</div><div class="metric-val">{data["avg_rating"]:.2f} ⭐</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("📊 Phân Bố Điểm Đánh Giá (Rating Distribution)")
        fig, ax = plt.subplots(figsize=(6, 3.8))
        df_r = data["rating_dist"]
        ax.bar(df_r["rating"], df_r["count"], color="#3B82F6", edgecolor="black", width=0.6)
        ax.set_xlabel("Số sao đánh giá (1-5)")
        ax.set_ylabel("Số lượt đánh giá")
        for i, v in enumerate(df_r["count"]):
            ax.text(df_r["rating"].iloc[i], v + 5000, f"{v:,}", ha="center", fontsize=8, fontweight="bold")
        st.pyplot(fig)

    with col_right:
        st.subheader("🎯 Thị Phần Lượt Xem Theo Thể Loại Phim")
        fig, ax = plt.subplots(figsize=(6, 3.8))
        df_g = data["genre_dist"].head(8)
        ax.barh(df_g["genre_name"], df_g["views"], color="#10B981", edgecolor="black")
        ax.invert_yaxis()
        ax.set_xlabel("Tổng lượt xem")
        st.pyplot(fig)

    st.info("ℹ️ **Lưu ý phương pháp luận:** Cột `watch_minutes` được sinh mô phỏng dựa trên thời lượng phim thực tế từ IMDb và điểm rating (nhiễu Gauss, seed=42) và gắn cờ `is_simulated = 1`.")

# ==============================================================================
# PAGE 2: USER CLUSTERING (Q1)
# ==============================================================================
elif page.startswith("2."):
    st.markdown('<div class="main-title">👥 Phân Cụm Người Dùng & Phân Tích Thị Hiếu (Q1)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Trả lời Q1: Thị hiếu xem phim thay đổi thế nào theo độ tuổi và giới tính? (Thuật toán K-Means & Kiểm định Chi-Square)</div>', unsafe_allow_html=True)

    df_clusters, df_personas = load_cluster_data()

    # Personas Table
    st.subheader("📋 Chân Dung 4 Cụm Thị Hiếu Khán Giả (K-Means Personas)")
    st.dataframe(
        df_personas,
        column_config={
            "cluster_id": "Mã cụm",
            "persona_name": "Tên chân dung cụm",
            "user_count": st.column_config.NumberColumn("Số lượng User", format="%d"),
            "percentage": st.column_config.NumberColumn("Tỷ lệ (%)", format="%.2f%%"),
            "top_genres": "Thể loại ưa chuộng nhất"
        },
        use_container_width=True,
        hide_index=True
    )

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns([1.2, 1])

    with c1:
        st.subheader("🗺️ Biểu Đồ Không Gian Giảm Chiều PCA (K=4)")
        fig, ax = plt.subplots(figsize=(7, 5))
        palette = sns.color_palette("Set2", 4)
        for cid in range(4):
            sub = df_clusters[df_clusters["cluster"] == cid]
            ax.scatter(sub["pca_1"], sub["pca_2"], label=f"Cụm {cid}", alpha=0.5, s=20, color=palette[cid])
        ax.set_title("Phân bố người dùng trên 2 thành phần chính (PC1 & PC2)")
        ax.set_xlabel("PC1 (19.8% phương sai)")
        ax.set_ylabel("PC2 (9.8% phương sai)")
        ax.legend(loc="upper right")
        st.pyplot(fig)

    with c2:
        st.subheader("🧪 Kiểm Định Ý Nghĩa Thống Kê Chi-Square")
        st.markdown("""
        - **Kiểm định Giới tính (Gender):**
          - $\\chi^2 = 358.78$, $p = 1.87 \\times 10^{-77} < 0.001$, $DoF = 3$
          - **Kết luận:** Giới tính tác động cực kỳ mạnh mẽ đến thị hiếu. Cụm Hành động & Sci-Fi (Cụm 0) có **86.3% là Nam**, trong khi Cụm Hoạt hình/Thiếu nhi (Cụm 3) có **55.0% là Nữ**.
        - **Kiểm định Nhóm tuổi (Age Groups):**
          - $\\chi^2 = 329.21$, $p = 4.58 \\times 10^{-59} < 0.001$, $DoF = 18$
          - **Kết luận:** Nhóm trẻ (Under 18) tập trung cao đột biến tại Cụm 3 (14.4%), nhóm 45+ gắn liền với Cụm Tâm lý & Lãng mạn (Cụm 1: 31.3%).
        """)
        
        # Interactive Cluster Demographic Filter
        selected_cluster = st.selectbox("Xem phân bố nhân khẩu của cụm:", [0, 1, 2, 3], format_func=lambda x: f"Cụm {x}: {df_personas.loc[x, 'persona_name']}")
        c_users = df_clusters[df_clusters["cluster"] == selected_cluster]
        gender_counts = c_users["gender"].value_counts(normalize=True) * 100
        st.write(f"**Tỷ lệ giới tính Cụm {selected_cluster}:** Nam: `{gender_counts.get('Male', 0):.1f}%` | Nữ: `{gender_counts.get('Female', 0):.1f}%`")

# ==============================================================================
# PAGE 3: OLAP & QoQ GENRE TRENDS (Q3)
# ==============================================================================
elif page.startswith("3."):
    st.markdown('<div class="main-title">📈 Xu Hướng Thể Loại & Tăng Trưởng Quý (Q3)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Trả lời Q3: Thể loại nào đang tăng trưởng lượt xem mạnh nhất trong các quý gần đây? (OLAP ROLLUP/CUBE & LAG)</div>', unsafe_allow_html=True)

    df_qoq, df_cube = load_olap_data()

    available_quarters = sorted(df_qoq["period"].unique(), reverse=True)
    selected_period = st.selectbox("Chọn Quý phân tích:", available_quarters, index=0)

    # Filter for selected quarter
    q_data = df_qoq[df_qoq["period"] == selected_period].dropna(subset=["qoq_growth_pct"]).sort_values("qoq_growth_pct", ascending=False)

    col_q1, col_q2 = st.columns([1.2, 1])

    with col_q1:
        st.subheader(f"🏆 Xếp Hạng Tăng Trưởng Thể Loại Quý {selected_period}")
        st.dataframe(
            q_data[["genre_name", "total_views", "prev_quarter_views", "qoq_growth_pct", "avg_rating"]],
            column_config={
                "genre_name": "Thể loại",
                "total_views": st.column_config.NumberColumn("Lượt xem hiện tại", format="%d"),
                "prev_quarter_views": st.column_config.NumberColumn("Lượt xem quý trước", format="%d"),
                "qoq_growth_pct": st.column_config.NumberColumn("Tăng trưởng QoQ (%)", format="%+.2f%%"),
                "avg_rating": st.column_config.NumberColumn("Điểm TB", format="%.2f ⭐")
            },
            use_container_width=True,
            hide_index=True
        )

    with col_q2:
        st.subheader(f"📊 Biểu Đồ Tăng Trưởng QoQ Quý {selected_period}")
        fig, ax = plt.subplots(figsize=(6, 4.5))
        top_growth = q_data.head(8)
        colors = ["#10B981" if x > 0 else "#EF4444" for x in top_growth["qoq_growth_pct"]]
        ax.barh(top_growth["genre_name"], top_growth["qoq_growth_pct"], color=colors, edgecolor="black")
        ax.invert_yaxis()
        ax.axvline(0, color="gray", linestyle="--")
        ax.set_xlabel("Tỷ lệ tăng trưởng QoQ (%)")
        st.pyplot(fig)

    st.markdown("---")
    st.subheader("📉 Chuỗi Thời Gian Tăng Trưởng QoQ Các Thể Loại Trọng Điểm")
    st.image(str(BASE_DIR / "docs" / "images" / "qoq_growth_chart.png"), use_container_width=True)

# ==============================================================================
# PAGE 4: RECOMMENDATIONS & ASSOCIATION RULES (Q2)
# ==============================================================================
elif page.startswith("4."):
    st.markdown('<div class="main-title">🎬 Hệ Gợi Ý Phim & Khai Phá Luật Kết Hợp (Q2)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Trả lời Q2: Nếu người dùng thích phim hành động của đạo diễn A, họ có xu hướng đánh giá cao những phim nào tiếp theo?</div>', unsafe_allow_html=True)

    recommender, dir_recommender = load_recommender_models()

    tab1, tab2, tab3 = st.tabs([
        "🎯 Gợi ý theo Người Dùng (Collaborative Filtering)",
        "🎥 Gợi ý theo Đạo Diễn Hành Động (Q2 Scenario)",
        "📊 Bảng Đánh Giá Độ Chính Xác (Evaluation Metrics)"
    ])

    with tab1:
        st.subheader("Gợi Ý Phim Cá Nhân Hóa (Item-Based Collaborative Filtering)")
        col_in1, col_in2 = st.columns([1, 1])
        with col_in1:
            input_user = st.number_input("Nhập User ID (1 - 6040, hoặc nhập 9999 để test Cold-Start):", min_value=1, max_value=9999, value=1)
        with col_in2:
            top_k = st.slider("Số lượng phim gợi ý (Top-K):", min_value=5, max_value=20, value=10)

        if st.button("🚀 Khám Phá Danh Mục Gợi Ý"):
            recs = recommender.recommend(user_id=input_user, k=top_k)
            st.success(f"Đã tìm thấy Top {len(recs)} bộ phim phù hợp nhất cho User #{input_user}!")
            st.dataframe(
                recs[["title", "release_year", "director", "genres", "score", "reason"]],
                column_config={
                    "title": "Tên phim",
                    "release_year": "Năm",
                    "director": "Đạo diễn",
                    "genres": "Thể loại",
                    "score": st.column_config.NumberColumn("Điểm dự đoán", format="%.2f ⭐"),
                    "reason": "Lý do gợi ý"
                },
                use_container_width=True,
                hide_index=True
            )

    with tab2:
        st.subheader("Kịch Bản Q2: Thích Phim Hành Động Của Đạo Diễn A -> Xem Phim Gì Tiếp Theo?")
        st.markdown("*Khai phá bằng thuật toán FP-Growth / Apriori trên giỏ phim yêu thích (Rating $\ge 4$)*")

        directors_list = ["James Cameron", "Steven Spielberg", "George Lucas", "John Woo", "Luc Besson", "Ridley Scott"]
        selected_dir = st.selectbox("Chọn Đạo diễn Phim Hành Động:", directors_list)
        dir_k = st.slider("Số lượng phim gợi ý:", min_value=3, max_value=10, value=6, key="dir_k")

        if st.button("🔍 Khai Phá Luật Kết Hợp & Gợi Ý Tiếp Theo"):
            dir_recs = dir_recommender.recommend_by_director(selected_dir, k=dir_k)
            st.success(f"Kết quả phân tích luật kết hợp cho người hâm mộ đạo diễn **{selected_dir}**:")
            st.dataframe(
                dir_recs[["title", "director", "genres", "confidence", "lift", "reason"]],
                column_config={
                    "title": "Tên phim gợi ý",
                    "director": "Đạo diễn",
                    "genres": "Thể loại",
                    "confidence": st.column_config.NumberColumn("Độ tin cậy (Confidence)", format="%.2f"),
                    "lift": st.column_config.NumberColumn("Độ nâng (Lift)", format="%.2f"),
                    "reason": "Giải thích luật kết hợp"
                },
                use_container_width=True,
                hide_index=True
            )

    with tab3:
        st.subheader("Bảng So Sánh Hiệu Năng Các Mô Hình (Time-Based Train/Test Split)")
        eval_path = BASE_DIR / "data" / "export" / "recsys_evaluation.csv"
        df_eval = pd.read_csv(eval_path)
        st.dataframe(df_eval, use_container_width=True, hide_index=True)
        st.markdown("""
        **Nhận xét chuyên môn:**
        - Tập dữ liệu được phân chia theo **mốc thời gian (Time-Based Split 80/20)**, mô phỏng đúng môi trường thực tế (dùng dữ liệu quá khứ để dự đoán tương lai), loại trừ hoàn toàn rò rỉ dữ liệu (*Data Leakage*).
        - Mô hình **Item-Based Collaborative Filtering** đạt độ chính xác **Precision@10 = 15.40%** và **RMSE = 1.0126**, vượt trội so với User-based CF trong điều kiện ma trận tương tác thưa.
        """)

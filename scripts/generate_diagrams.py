#!/usr/bin/env python3
"""
scripts/generate_diagrams.py

Generates professional visual architecture diagrams:
1. docs/images/system_architecture.png (4-Tier OLAM Architecture)
2. docs/images/star_schema_diagram.png (Star Schema ERD Diagram)
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
IMAGES_DIR = BASE_DIR / "docs" / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cbd5e1'

def draw_system_architecture():
    """Generates 4-Tier OLAM system architecture diagram."""
    fig, ax = plt.subplots(figsize=(14, 8), dpi=300)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8.5)
    ax.axis('off')

    # Title
    ax.text(7, 8.1, "KIẾN TRÚC TỔNG THỂ HỆ THỐNG KHO DỮ LIỆU & KHAI PHÁ DỮ LIỆU (MÔ HÌNH 4 TẦNG OLAM)",
            ha='center', va='center', fontsize=14, fontweight='bold', color='#1e3a8a')
    ax.text(7, 7.7, "Theo chuẩn giáo trình Kho dữ liệu & Khai phá dữ liệu - Học viện Công nghệ Bưu chính Viễn thông (PTIT)",
            ha='center', va='center', fontsize=10, fontstyle='italic', color='#475569')

    # Tier definitions (x, y, w, h, title, bg, border, content)
    tiers = [
        {
            "name": "TẦNG 1: NGUỒN DỮ LIỆU & ETL PIPELINE",
            "y": 6.1, "color": "#f1f5f9", "border": "#3b82f6",
            "boxes": [
                ("MovieLens 1M\n(1M ratings, 6K users)", 1.2, 2.4, "#dbeafe"),
                ("IMDb Public Dumps\n(Directors, Runtimes)", 4.0, 2.4, "#dbeafe"),
                ("Netflix Titles\n(8.8K catalog titles)", 6.8, 2.4, "#dbeafe"),
                ("ETL & Fuzzy Match Engine\n(Python, Pandas, RapidFuzz)", 9.8, 3.2, "#bfdbfe")
            ]
        },
        {
            "name": "TẦNG 2: KHO DỮ LIỆU ĐA CHIỀU (DATA WAREHOUSE - SQL SERVER 2022)",
            "y": 4.2, "color": "#f8fafc", "border": "#1d4ed8",
            "boxes": [
                ("Staging Layer (stg.*)\n• 7 bảng đệm tạm thời\n• Bulk batch loading", 1.2, 3.4, "#e0e7ff"),
                ("Fact Table (dw.FactRating)\n• 1,000,209 dòng rating\n• rating, watch_minutes", 5.0, 3.8, "#c7d2fe"),
                ("Dimension Tables (dw.*)\n• DimUser, DimMovie, DimDate\n• DimDirector, DimGenre, Bridge", 9.2, 3.8, "#e0e7ff")
            ]
        },
        {
            "name": "TẦNG 3: ĐỘNG CƠ OLAP & KHAI PHÁ DỮ LIỆU (OLAP & DATA MINING ENGINE)",
            "y": 2.3, "color": "#fefce8", "border": "#d97706",
            "boxes": [
                ("Truy Vấn Đa Chiều OLAP (Q3)\n• CUBE, ROLLUP, LAG()\n• Tăng trưởng QoQ (Sci-Fi +17%)", 1.2, 3.6, "#fef3c7"),
                ("Phân Cụm K-Means (Q1)\n• Vector sở thích 36 chiều\n• K=4, PCA 2D, Chi-Square", 5.2, 3.6, "#fef3c7"),
                ("Hệ Gợi Ý & Luật Kết Hợp (Q2)\n• Item-based CF (RMSE 1.01)\n• FP-Growth đạo diễn (Lift > 1.5)", 9.2, 3.8, "#fef3c7")
            ]
        },
        {
            "name": "TẦNG 4: GIAO DIỆN BIỂU DIỄN & NGƯỜI DÙNG (PRESENTATION & GUI)",
            "y": 0.5, "color": "#f0fdf4", "border": "#16a34a",
            "boxes": [
                ("Web App Tương Tác Streamlit\n(streamlit_app.py - 4 tabs UI)", 1.5, 3.4, "#dcfce7"),
                ("Executive BI Dashboard\n(Power BI 3 Trang Quản Trị)", 5.3, 3.4, "#dcfce7"),
                ("Báo Cáo Học Thuật & Slide\n(report.docx & presentation.pptx)", 9.1, 3.6, "#dcfce7")
            ]
        }
    ]

    for tier in tiers:
        # Background tier banner
        rect = patches.FancyBboxPatch((0.5, tier["y"]), 13.0, 1.4,
                                      boxstyle="round,pad=0.08",
                                      facecolor=tier["color"], edgecolor=tier["border"],
                                      linewidth=1.8, linestyle="--")
        ax.add_patch(rect)
        ax.text(0.7, tier["y"] + 1.15, tier["name"], fontsize=9.5, fontweight='bold', color=tier["border"])

        for title, x, w, bg in tier["boxes"]:
            b_rect = patches.FancyBboxPatch((x, tier["y"] + 0.15), w, 0.9,
                                            boxstyle="round,pad=0.05",
                                            facecolor=bg, edgecolor=tier["border"],
                                            linewidth=1.0)
            ax.add_patch(b_rect)
            ax.text(x + w/2, tier["y"] + 0.6, title, ha='center', va='center',
                    fontsize=8.5, fontweight='semibold', color='#0f172a')

    # Draw vertical connecting arrows between tiers
    arrow_props = dict(facecolor='#475569', edgecolor='#475569', width=1.8, headwidth=7, headlength=6)
    ax.annotate('', xy=(7, 5.6), xytext=(7, 6.0), arrowprops=arrow_props)
    ax.annotate('', xy=(7, 3.7), xytext=(7, 4.1), arrowprops=arrow_props)
    ax.annotate('', xy=(7, 1.9), xytext=(7, 2.2), arrowprops=arrow_props)

    plt.tight_layout()
    out_path = IMAGES_DIR / "system_architecture.png"
    plt.savefig(out_path, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"[+] Saved system architecture diagram to {out_path}")

def draw_star_schema():
    """Generates visual Star Schema ERD diagram."""
    fig, ax = plt.subplots(figsize=(14, 8), dpi=300)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8.5)
    ax.axis('off')

    # Title
    ax.text(7, 8.1, "LƯỢC ĐỒ HÌNH SAO KHO DỮ LIỆU (STAR SCHEMA ERD - MOVIEDW)",
            ha='center', va='center', fontsize=14, fontweight='bold', color='#1e3a8a')
    ax.text(7, 7.7, "Microsoft SQL Server 2022 • dw Schema • Khóa thay thế Surrogate Keys & Bảng cầu nối Bridge",
            ha='center', va='center', fontsize=10, fontstyle='italic', color='#475569')

    def add_table_box(x, y, w, h, title, fields, header_color='#1e3a8a', bg_color='#f8fafc'):
        # Table container
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05",
                                      facecolor=bg_color, edgecolor=header_color, linewidth=1.5)
        ax.add_patch(rect)
        # Header bar
        header_h = 0.55
        h_rect = patches.Rectangle((x, y + h - header_h), w, header_h,
                                   facecolor=header_color, edgecolor=header_color)
        ax.add_patch(h_rect)
        ax.text(x + w/2, y + h - header_h/2, title, ha='center', va='center',
                fontsize=9.5, fontweight='bold', color='#ffffff')
        # Fields
        curr_y = y + h - header_h - 0.22
        for f in fields:
            ax.text(x + 0.15, curr_y, f, ha='left', va='center', fontsize=8, color='#0f172a')
            curr_y -= 0.23

    # Center: Fact Table
    add_table_box(5.0, 2.8, 4.0, 2.8, "FACT: dw.FactRating (1,000,209 rows)", [
        "[PK] rating_id (bigint, IDENTITY)",
        "[FK] user_key (DimUser, int)",
        "[FK] movie_key (DimMovie, int)",
        "[FK] date_key (DimDate, int)",
        "[Measure] rating (tinyint, 1-5)",
        "[Measure] watch_minutes (int)",
        "[Meta] is_simulated (bit = 1)"
    ], header_color='#dc2626', bg_color='#fef2f2')

    # Surrounding Dimensions
    # 1. DimUser (Top Left)
    add_table_box(0.6, 5.0, 3.6, 2.3, "DIM: dw.DimUser (6,040 rows)", [
        "[PK] user_key (int)",
        "• user_id (natural ID)",
        "• gender (Male / Female)",
        "• age_group (7 nhom tuoi)",
        "• occupation_name (21 nghe)",
        "• zip_code"
    ], header_color='#2563eb', bg_color='#eff6ff')

    # 2. DimDate (Top Right)
    add_table_box(9.8, 5.0, 3.6, 2.3, "DIM: dw.DimDate (1,040 rows)", [
        "[PK] date_key (YYYYMMDD)",
        "• full_date (date)",
        "• year (2000 - 2003)",
        "• quarter (Q1 - Q4)",
        "• month (1 - 12)",
        "• is_weekend (0 / 1)"
    ], header_color='#059669', bg_color='#ecfdf5')

    # 3. DimMovie (Bottom Left)
    add_table_box(0.6, 1.0, 3.6, 2.5, "DIM: dw.DimMovie (3,883 rows)", [
        "[PK] movie_key (int)",
        "• movie_id (natural ID)",
        "• title (ten phim chuan)",
        "• release_year (nam)",
        "• runtime_minutes (IMDb)",
        "[FK] director_key (DimDirector)",
        "• match_type (EXACT/FUZZY)"
    ], header_color='#7c3aed', bg_color='#f5f3ff')

    # 4. DimDirector (Far Bottom Left)
    add_table_box(0.6, 3.8, 3.6, 1.0, "DIM: dw.DimDirector (1,775 rows)", [
        "[PK] director_key (int)",
        "• director_name (IMDb)"
    ], header_color='#475569', bg_color='#f8fafc')

    # 5. BridgeMovieGenre (Bottom Right)
    add_table_box(9.8, 2.7, 3.6, 1.9, "BRIDGE: dw.BridgeMovieGenre (6,408)", [
        "[PK, FK] movie_key",
        "[PK, FK] genre_key",
        "• Giai quyet quan he N-N",
        "• 1 Phim thuoc nhieu The loai"
    ], header_color='#ea580c', bg_color='#fff7ed')

    # 6. DimGenre (Bottom Far Right)
    add_table_box(9.8, 1.0, 3.6, 1.4, "DIM: dw.DimGenre (18 rows)", [
        "[PK] genre_key (int)",
        "• genre_name (Action, Drama...)"
    ], header_color='#0891b2', bg_color='#ecfeff')

    # Draw Connecting Arrows
    line_props = dict(arrowstyle='<->', color='#334155', lw=1.5)
    # Fact -> DimUser
    ax.annotate('', xy=(3.0, 5.0), xytext=(5.2, 4.8), arrowprops=line_props)
    # Fact -> DimDate
    ax.annotate('', xy=(11.0, 5.0), xytext=(8.8, 4.8), arrowprops=line_props)
    # Fact -> DimMovie
    ax.annotate('', xy=(3.6, 3.2), xytext=(5.0, 3.6), arrowprops=line_props)
    # DimMovie -> DimDirector
    ax.annotate('', xy=(2.4, 3.8), xytext=(2.4, 3.5), arrowprops=line_props)
    # DimMovie -> BridgeMovieGenre
    ax.annotate('', xy=(9.8, 3.5), xytext=(9.0, 3.8), arrowprops=line_props)
    # BridgeMovieGenre -> DimGenre
    ax.annotate('', xy=(11.6, 2.4), xytext=(11.6, 2.7), arrowprops=line_props)

    plt.tight_layout()
    out_path = IMAGES_DIR / "star_schema_diagram.png"
    plt.savefig(out_path, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"[+] Saved Star Schema diagram to {out_path}")

if __name__ == "__main__":
    draw_system_architecture()
    draw_star_schema()

# Khai Phá Kho Dữ Liệu Lịch Sử Xem Phim Để Dự Đoán Thị Hiếu Người Dùng Và Tối Ưu Hóa Danh Mục Nội Dung

**Học phần:** Kho dữ liệu & Kỹ thuật khai phá dữ liệu (PTIT)  
**Nền tảng:** Mô phỏng nền tảng xem phim trực tuyến (tương tự Netflix)  
**Tác giả:** Nhóm sinh viên Công nghệ Thông tin - PTIT  

---

## 1. Mục tiêu đề tài & 3 câu hỏi nghiên cứu
Dự án xây dựng kho dữ liệu quy mô doanh nghiệp và quy trình khai phá dữ liệu toàn diện nhằm giải quyết 3 bài toán trọng tâm:
- **Q1 (Phân cụm):** Thị hiếu xem phim thay đổi thế nào theo độ tuổi và giới tính? (Áp dụng K-Means, Elbow & Silhouette, PCA, kiểm định $\chi^2$ / Crosstab).
- **Q2 (Gợi ý & Luật kết hợp):** Nếu người dùng thích phim hành động của đạo diễn A, họ có xu hướng đánh giá cao những phim nào tiếp theo? (Áp dụng Item-based/User-based Collaborative Filtering, Apriori / FP-Growth).
- **Q3 (OLAP & Tăng trưởng):** Thể loại nào đang tăng trưởng lượt xem mạnh nhất trong các quý gần đây? (Áp dụng `ROLLUP`, `CUBE`, window function `LAG()` tính QoQ growth, các phép toán Roll-up, Drill-down, Slice, Dice, Pivot).

---

## 2. Kiến trúc kho dữ liệu (Star Schema & OLAM)
- **Kiến trúc đa tầng:** Tuân thủ mô hình 4 tầng OLAM (Data Warehouse -> CSDL đa chiều -> OLAP/OLAM Engine -> Presentation GUI) theo giáo trình môn học.
- **Fact Table:** `FactRating` (user_key, movie_key, date_key, rating, watch_minutes, is_simulated).
- **Dimension Tables:** `DimUser`, `DimMovie`, `DimDate`, `DimGenre`, `DimDirector`, `DimActor`.
- **Bridge Tables:** `BridgeMovieGenre`, `BridgeMovieActor` (xử lý quan hệ N-N).

---

## 3. Cấu trúc thư mục dự án

```text
movie-dw-project/
├── docker-compose.yml          # Cấu hình container Microsoft SQL Server
├── requirements.txt            # Danh sách thư viện Python phụ thuộc
├── .env.example                # File mẫu cấu hình biến môi trường
├── .env                        # File biến môi trường thực tế (bảo mật)
├── README.md                   # Hướng dẫn chi tiết dự án
├── data/
│   ├── raw/                    # Dữ liệu gốc (ml-1m, imdb, netflix_titles.csv)
│   ├── processed/              # Dữ liệu sạch sau tiền xử lý
│   └── export/                 # Dữ liệu xuất cho Power BI / báo cáo
├── sql/                        # Tập lệnh SQL phân tầng (stg, dw, olap, views)
├── src/
│   ├── etl/                    # Pipeline trích xuất, làm sạch và nạp dữ liệu
│   ├── mining/                 # Thuật toán phân cụm K-Means & phân tích thị hiếu
│   ├── recsys/                 # Hệ gợi ý CF & luật kết hợp FP-Growth / Apriori
│   └── utils/                  # Tiện ích kết nối DB, ghi log, vẽ biểu đồ
├── notebooks/                  # Jupyter notebooks phân tích thực nghiệm
├── app/                        # Giao diện web Streamlit Demo
├── docs/                       # Báo cáo, hướng dẫn Power BI, kịch bản demo
│   └── references/             # Slide bài giảng và giáo trình PTIT
├── slides/                     # Slide thuyết trình PowerPoint (.pptx)
└── scripts/                    # Scripts tự động hóa (download_data, run_all)
```

---

## 4. Hướng dẫn cài đặt & Khởi chạy

### 4.1. Thiết lập môi trường Python
```bash
# Tạo môi trường ảo
python3 -m venv venv
source venv/bin/activate

# Cài đặt thư viện
pip install -r requirements.txt
```

### 4.2. Khởi chạy Kho dữ liệu SQL Server
```bash
# Khởi chạy SQL Server container qua Docker Compose
docker compose up -d

# Hoặc cấu hình thông số kết nối trong file .env
cp .env.example .env
```

### 4.3. Tải và chuẩn bị dữ liệu tự động
```bash
python scripts/download_data.py
```
*Ghi chú:* Script tự động tải MovieLens 1M (1 triệu rating), Netflix Titles, và thực hiện cơ chế streaming để lọc thông tin đạo diễn/thời lượng phim từ IMDb mà không gây tràn bộ nhớ đĩa.
# kho-du-lieu-va-khai-pha-du-lieu-cuoi-ky

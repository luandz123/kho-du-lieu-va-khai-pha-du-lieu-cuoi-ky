# Khai Phá Kho Dữ Liệu Lịch Sử Xem Phim Để Dự Đoán Thị Hiếu Người Dùng Và Tối Ưu Hóa Danh Mục Nội Dung

**Học phần:** Kho dữ liệu & Kỹ thuật khai phá dữ liệu (PTIT)  
**Nền tảng:** Mô phỏng nền tảng xem phim trực tuyến (tương tự Netflix)  
**Tác giả:** Nhóm sinh viên Công nghệ Thông tin - PTIT  

---

## 1. Mục tiêu đề tài & 3 câu hỏi nghiên cứu
Dự án xây dựng kho dữ liệu quy mô doanh nghiệp và quy trình khai phá dữ liệu toàn diện nhằm giải quyết 3 bài toán trọng tâm:
- **Q1 (Phân cụm):** Thị hiếu xem phim thay đổi thế nào theo độ tuổi và giới tính? (K-Means $K=4$, Elbow & Silhouette, PCA 2D, kiểm định Chi-Square $\chi^2$ với $p < 0.001$).
- **Q2 (Gợi ý & Luật kết hợp):** Nếu người dùng thích phim hành động của đạo diễn A, họ có xu hướng đánh giá cao những phim nào tiếp theo? (Item-Based Collaborative Filtering RMSE=1.0126, Precision@10=15.40% kết hợp FP-Growth khai phá luật kết hợp đa cấp độ với Support, Confidence, Lift).
- **Q3 (OLAP & Tăng trưởng):** Thể loại nào đang tăng trưởng lượt xem mạnh nhất trong các quý gần đây? (Truy vấn đa chiều `ROLLUP`, `CUBE`, window function `LAG()` tính QoQ growth, xác định Sci-Fi đạt +17.02% trong 2003-Q1).

---

## 2. Kiến trúc kho dữ liệu (Star Schema & OLAM)
- **Kiến trúc đa tầng:** Tuân thủ mô hình 4 tầng OLAM (Data Warehouse -> CSDL đa chiều -> OLAP/OLAM Engine -> Presentation GUI) theo giáo trình môn học PTIT (TS. Nguyễn Quỳnh Chi & Jiawei Han).
- **Fact Table:** `FactRating` (1,000,209 dòng, khóa ngoại trỏ tới các bảng Dimension).
- **Dimension Tables:** `DimUser` (6,040 người dùng), `DimMovie` (3,883 phim), `DimDate` (1,040 ngày), `DimGenre` (18 thể loại), `DimDirector` (1,775 đạo diễn).
- **Bridge Tables:** `BridgeMovieGenre` (6,408 quan hệ) giải quyết bài toán đa trị (1 bộ phim thuộc nhiều thể loại).
- **Kiểm định chất lượng dữ liệu (Data Quality Audit):** Đạt 100% (5/5 tiêu chí: 0 bản ghi NULL khóa ngoại, 0 orphan keys, 0 trùng lặp, tính toàn vẹn tham chiếu 100%).

---

## 3. Cấu trúc thư mục dự án

```text
cuoikykhodulieu/
├── docker-compose.yml          # Container Microsoft SQL Server 2022
├── requirements.txt            # Danh sách thư viện Python (pandas, scikit-learn, mlxtend, streamlit,...)
├── .env.example                # File mẫu cấu hình biến môi trường kết nối DB
├── README.md                   # Tài liệu hướng dẫn tổng quan dự án
├── data/
│   ├── raw/                    # Dữ liệu gốc (ml-1m, imdb streams, netflix_titles.csv)
│   ├── processed/              # Dữ liệu sạch sau chuẩn hóa & fuzzy matching (unmatched_movies.csv)
│   ├── models/                 # Mô hình AI đã huấn luyện (item_cf_recommender.pkl, director_recommender.pkl)
│   └── export/                 # Dữ liệu trích xuất dạng CSV phục vụ Power BI
├── sql/
│   ├── 01_create_schema.sql    # Định nghĩa cấu trúc Schema (stg, dw, Fact, Dims, Bridge)
│   ├── 02_load_dims.sql        # Nạp dữ liệu các bảng chiều (SCD Type 1)
│   ├── 03_load_fact.sql        # Nạp bảng FactRating
│   ├── 04_olap_queries.sql     # Các câu truy vấn CUBE, ROLLUP, QoQ Growth LAG()
│   └── 05_views_for_powerbi.sql# Tạo Views tối ưu hóa cho Power BI DirectQuery/Import
├── src/
│   ├── etl/                    # Pipeline làm sạch, Fuzzy matching & nạp SQL Server
│   ├── mining/                 # Phân cụm người dùng K-Means, kiểm định thống kê, OLAP
│   ├── recsys/                 # Hệ gợi ý Item-based CF & FP-Growth Association Rules
│   └── utils/                  # DB connector (pymssql/SQLAlchemy), Logger
├── app/
│   └── streamlit_app.py        # Web App Demo tương tác trực quan 4 trang
├── docs/
│   ├── report.docx             # Báo cáo học thuật định dạng Microsoft Word (~52KB)
│   ├── report.md               # Bản Markdown chi tiết của báo cáo
│   ├── erd.md                  # Sơ đồ quan hệ Star Schema Mermaid
│   ├── powerbi_guide.md        # Hướng dẫn chi tiết xây dựng Dashboard Power BI 3 trang
│   ├── demo_script.md          # Kịch bản thuyết trình & demo 5 phút
│   └── images/                 # Toàn bộ biểu đồ phân tích trực quan
├── slides/
│   └── presentation.pptx       # Slide báo cáo PowerPoint (14 slides chuẩn PTIT có speaker notes)
└── scripts/
    ├── run_all.sh              # Script chạy tự động toàn bộ pipeline dự án (1 lệnh duy nhất)
    ├── download_data.py        # Tải và streaming xử lý IMDb, Netflix, ML-1M
    ├── export_docx.py          # Script biên dịch báo cáo Word chuẩn APA
    └── generate_slides.py      # Script biên dịch Slide PowerPoint tự động
```

---

## 4. Hướng dẫn cài đặt & Khởi chạy

### 4.1. Cài đặt môi trường
```bash
# Tạo môi trường ảo Python 3.10+
python3 -m venv venv
source venv/bin/activate

# Cài đặt toàn bộ thư viện cần thiết
pip install -r requirements.txt
```

### 4.2. Cấu hình cơ sở dữ liệu SQL Server
Tạo file `.env` từ `.env.example` và điều chỉnh thông số kết nối:
```bash
cp .env.example .env
```
Nội dung file `.env`:
```env
DB_SERVER=localhost
DB_PORT=1433
DB_NAME=MovieDW
DB_USER=sa
DB_PASSWORD=YourPasswordHere
```

### 4.3. Chạy toàn bộ Pipeline với 1 lệnh duy nhất
Dự án đã được tích hợp tự động hóa qua file shell script:
```bash
bash scripts/run_all.sh
```
Script sẽ tự động thực hiện:
1. Chuẩn hóa & Fuzzy matching dữ liệu (ML-1M + IMDb + Netflix).
2. Tạo Schema và nạp 1,000,209 dòng vào SQL Server `MovieDW`.
3. Thực thi truy vấn OLAP (`ROLLUP`, `CUBE`, `LAG()`).
4. Chạy mô hình phân cụm K-Means ($K=4$), kiểm định $\chi^2$.
5. Huấn luyện mô hình Item-based CF và khai phá luật FP-Growth.
6. Biên dịch tự động báo cáo Word (`docs/report.docx`) và Slide PowerPoint (`slides/presentation.pptx`).

---

## 5. Khởi chạy Giao diện Trực quan Web App (Streamlit Demo)
Chạy ứng dụng web demo bằng lệnh:
```bash
./venv/bin/streamlit run app/streamlit_app.py
```
Giao diện bao gồm 4 tab chuyên sâu:
1. **Tổng quan Kho dữ liệu (Overview):** KPIs tổng số bản ghi (1,000,209 ratings, 6,040 users, 3,883 movies), phân bố điểm đánh giá và sơ đồ Star Schema.
2. **Q1: Phân cụm người dùng:** Biểu đồ PCA 2D 4 cụm người dùng, hồ sơ sở thích theo cụm, kiểm định Chi-Square giới tính & độ tuổi.
3. **Q2: Hệ thống gợi ý & Luật kết hợp:** Trình mô phỏng gợi ý phim theo từng cá nhân (User ID) và tìm kiếm luật kết hợp đạo diễn (James Cameron, Steven Spielberg,...).
4. **Q3: Xu hướng & Tăng trưởng OLAP:** Phân tích tốc độ tăng trưởng QoQ theo thể loại, biểu đồ tương tác thời gian thực.

---

## 6. Danh mục sản phẩm bàn giao (Deliverables)
1. **Source code đầy đủ:** Kiến trúc modular, comment tiếng Anh chuẩn mực, chạy thành công 100%.
2. **Cơ sở dữ liệu:** Database `MovieDW` trên SQL Server với staging và warehouse schema, views tối ưu.
3. **Báo cáo đồ án (Report):**
   - File Word: [`docs/report.docx`](file:///home/luan/Desktop/cuoikykhodulieu/docs/report.docx) (52 KB, định dạng bảng biểu, hình ảnh, tài liệu tham khảo chuẩn PTIT).
   - File Markdown: [`docs/report.md`](file:///home/luan/Desktop/cuoikykhodulieu/docs/report.md).
4. **Slide thuyết trình:**
   - File PowerPoint: [`slides/presentation.pptx`](file:///home/luan/Desktop/cuoikykhodulieu/slides/presentation.pptx) (14 slides trình bày chuyên nghiệp, hình ảnh minh họa thực nghiệm, đầy đủ speaker notes cho từng slide).
5. **Hướng dẫn Power BI:** [`docs/powerbi_guide.md`](file:///home/luan/Desktop/cuoikykhodulieu/docs/powerbi_guide.md) kèm file CSV xuất tại `data/export/`.
6. **Kịch bản thuyết trình 5 phút:** [`docs/demo_script.md`](file:///home/luan/Desktop/cuoikykhodulieu/docs/demo_script.md).

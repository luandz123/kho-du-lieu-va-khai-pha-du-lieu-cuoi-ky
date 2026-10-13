# HƯỚNG DẪN XÂY DỰNG DASHBOARD TRÊN POWER BI DESKTOP

Tài liệu hướng dẫn kết nối, thiết lập mô hình dữ liệu quan hệ, định nghĩa công thức DAX và thiết kế 4 trang Dashboard phân tích kinh doanh cho đồ án môn học **Kho dữ liệu & Khai phá dữ liệu**.

---

## 1. HƯỚNG DẪN KẾT NỐI DỮ LIỆU VÀO POWER BI DESKTOP

Có 2 phương thức kết nối linh hoạt tùy thuộc vào môi trường máy tính chấm bài:

### Phương thức 1: Kết nối trực tiếp SQL Server (Khuyên dùng)
1. Mở **Power BI Desktop**, chọn **Get Data** $\rightarrow$ **SQL Server**.
2. Thiết lập thông số kết nối:
   - **Server:** `localhost,1433` (hoặc `localhost,14333` nếu dùng cổng container tùy biến).
   - **Database:** `MovieDW`.
   - **Data Connectivity mode:** Chọn **Import** (cho hiệu năng tính toán DAX và visualization mượt mà nhất).
3. Đăng nhập xác thực bằng tài khoản:
   - **User:** `sa`
   - **Password:** Mật khẩu trong file `.env` (ví dụ: `Luandz25032005`).
4. Tại cửa sổ **Navigator**, tích chọn các bảng và view trong schema `dw`:
   - `dw.DimUser`
   - `dw.DimMovie`
   - `dw.DimDirector`
   - `dw.DimGenre`
   - `dw.BridgeMovieGenre`
   - `dw.DimDate`
   - `dw.FactRating`
   - *Hoặc chọn các views đã tạo sẵn:* `dw.V_PowerBI_GenrePerformance`, `dw.V_PowerBI_UserDemographics`, `dw.V_PowerBI_DirectorRankings`.
5. Nhấn **Load**.

### Phương thức 2: Nạp từ thư mục CSV đã xuất (`data/export/`)
Nếu máy chấm không có quyền truy cập SQL Server hoặc cần demo offline nhanh:
1. Chọn **Get Data** $\rightarrow$ **Text/CSV**.
2. Chọn lần lượt các tệp trong thư mục `data/export/`:
   - `genreperformance.csv` (Dữ liệu tăng trưởng thể loại theo quý)
   - `userdemographics.csv` (Dữ liệu người dùng & tương tác)
   - `directorrankings.csv` (Thống kê đạo diễn)
   - `user_clusters.csv` (Kết quả phân cụm K-Means)
   - `olap_qoq_growth.csv` (Tăng trưởng QoQ chi tiết)
3. Nhấn **Load**.

---

## 2. THIẾT KẾ MÔ HÌNH DỮ LIỆU (DATA MODELING & RELATIONSHIPS)

Trong giao diện **Model View** của Power BI, cấu hình các mối quan hệ (Relationships) theo chuẩn **Star Schema**:

| Bảng 1 (From) | Trường liên kết | Bảng 2 (To) | Trường liên kết | Loại quan hệ | Hướng lọc (Cross filter) |
| :--- | :--- | :--- | :--- | :---: | :---: |
| `dw.DimUser` | `user_key` | `dw.FactRating` | `user_key` | **1 to Many (1:*)** | Single |
| `dw.DimMovie` | `movie_key` | `dw.FactRating` | `movie_key` | **1 to Many (1:*)** | Single |
| `dw.DimDate` | `date_key` | `dw.FactRating` | `date_key` | **1 to Many (1:*)** | Single |
| `dw.DimDirector` | `director_key` | `dw.DimMovie` | `director_key` | **1 to Many (1:*)** | Single |
| `dw.DimMovie` | `movie_key` | `dw.BridgeMovieGenre` | `movie_key` | **1 to Many (1:*)** | Both |
| `dw.DimGenre` | `genre_key` | `dw.BridgeMovieGenre` | `genre_key` | **1 to Many (1:*)** | Both |

> [!TIP]
> Bảng `BridgeMovieGenre` cần bật **Cross filter direction: Both** để khi người dùng lọc theo Thể loại (`DimGenre`), bộ lọc sẽ lan truyền qua `DimMovie` xuống `FactRating`.

---

## 3. DANH SÁCH THƯỚC ĐO DAX (DAX MEASURES)

Tạo một bảng rỗng `_Measures` để quản lý tập trung các công thức DAX:

### 3.1. Các chỉ số cơ bản (Core Metrics)
```dax
-- Tổng số lượt xem (đánh giá)
Total Views = COUNTROWS(FactRating)

-- Tổng thời gian xem (Giờ)
Total Watch Hours = 
DIVIDE(
    SUM(FactRating[watch_minutes]), 
    60, 
    0
)

-- Điểm đánh giá trung bình
Average Rating = 
AVERAGE(FactRating[rating])

-- Số lượng phim độc nhất đã xem
Unique Movies Watched = 
DISTINCTCOUNT(FactRating[movie_key])

-- Số lượng người dùng hoạt động
Active Users = 
DISTINCTCOUNT(FactRating[user_key])
```

### 3.2. Chỉ số tương tác tích cực & Tăng trưởng theo thời gian
```dax
-- Số lượt xem đánh giá cao (rating >= 4)
High Rating Views = 
CALCULATE(
    [Total Views],
    FactRating[rating] >= 4
)

-- Tỷ lệ hài lòng / yêu thích (%)
Positive Sentiment Rate = 
DIVIDE(
    [High Rating Views],
    [Total Views],
    0
) * 100

-- Lượt xem quý trước (Previous Quarter Views)
Prev Quarter Views = 
CALCULATE(
    [Total Views],
    PREVIOUSQUARTER(DimDate[full_date])
)

-- Tỷ lệ tăng trưởng theo quý (QoQ Growth %)
QoQ Growth % = 
VAR CurrentViews = [Total Views]
VAR PrevViews = [Prev Quarter Views]
RETURN
IF(
    ISBLANK(PrevViews) || PrevViews = 0,
    BLANK(),
    DIVIDE(CurrentViews - PrevViews, PrevViews, 0) * 100
)
```

---

## 4. BỐ CỤC 4 TRANG DASHBOARD BÁO CÁO KINH DOANH

### Trang 1: Tổng quan Nền tảng (Executive Overview)
- **Mục tiêu:** Cung cấp cái nhìn toàn cảnh về quy mô hệ thống streaming, khối lượng tương tác và phân bố thời gian.
- **Visual 1–4 (Thẻ chỉ số KPI Cards):**
  - Card 1: `Total Views` (1,000,209 lượt).
  - Card 2: `Total Watch Hours` (~1.54M giờ xem).
  - Card 3: `Average Rating` (3.58 sao).
  - Card 4: `Active Users` (6,040 người dùng) & `Unique Movies` (3,706 phim).
- **Visual 5 (Area Chart - Xu hướng thời gian):**
  - Trục X: `DimDate[year]`, `DimDate[quarter]`.
  - Trục Y: `Total Views` và `Total Watch Hours`.
- **Visual 6 (Donut Chart - Phân bố theo ngày trong tuần):**
  - Legend: `DimDate[day_name]`.
  - Values: `Total Views`.
- **Visual 7 (Treemap - Thị phần thể loại phim):**
  - Category: `DimGenre[genre_name]`.
  - Values: `Total Views`.
- **Bộ lọc / Slicers:**
  - Slicer Năm (`DimDate[year]`).
  - Slicer Nhóm tuổi (`DimUser[age_group]`).

---

### Trang 2: Thị hiếu Theo Tuổi & Giới tính + Cụm Người Dùng (Demographics & Clusters - Q1)
- **Mục tiêu:** Trả lời trực tiếp **Câu hỏi Q1**: Sự khác biệt rõ nét về thị hiếu theo độ tuổi và giới tính qua kết quả phân cụm K-Means.
- **Visual 1 (Stacked Bar Chart - Tỷ lệ Giới tính trong từng Cụm):**
  - Trục Y: `UserCluster[cluster_name]`.
  - Trục X: `Total Users` (% of total).
  - Legend: `DimUser[gender]`.
  - *Ý nghĩa:* Cho thấy Cụm 0 (Action/Sci-Fi) có 86.3% Nam, trong khi Cụm 3 (Family/Animation) có 55% Nữ.
- **Visual 2 (100% Stacked Column Chart - Phân bố Nhóm tuổi theo Cụm):**
  - Trục X: `UserCluster[cluster_name]`.
  - Trục Y: `User Count` (100% Stacked).
  - Legend: `DimUser[age_group]`.
  - *Ý nghĩa:* Nhóm Under 18 chiếm tỷ lệ cao vượt trội tại Cụm 3 (14.4%), nhóm 45+ tập trung ở Cụm 1.
- **Visual 3 (Scatter Plot - Phân cụm PCA 2D):**
  - Trục X: `PCA_1`.
  - Trục Y: `PCA_2`.
  - Legend: `Cluster`.
  - Tooltips: `user_id`, `age_group`, `gender`, `top_genres`.
- **Visual 4 (Matrix Table - Chân dung 4 Cụm):**
  - Hàng: `Cluster ID`, `Tên cụm`.
  - Cột/Giá trị: `Số lượng User`, `Tỷ lệ %`, `Thể loại yêu thích nhất`, `Điểm TB`.
- **Bộ lọc / Slicers:**
  - Slicer Cụm người dùng (`Cluster`).
  - Slicer Nghề nghiệp (`DimUser[occupation_name]`).

---

### Trang 3: Xu hướng Tăng trưởng Thể loại Theo Quý (Quarterly Genre Trends - Q3)
- **Mục tiêu:** Trả lời trực tiếp **Câu hỏi Q3**: Thể loại tăng trưởng mạnh nhất trong các quý gần đây thông qua các phép toán OLAP (ROLLUP/CUBE/LAG).
- **Visual 1 (Line Chart - Tỷ lệ tăng trưởng QoQ % theo Quý):**
  - Trục X: `DimDate[period]` (ví dụ: 2001-Q1 ... 2003-Q1).
  - Trục Y: `QoQ Growth %`.
  - Legend: `DimGenre[genre_name]`.
  - Thêm đường tham chiếu hằng số `y = 0%`.
- **Visual 2 (Clustered Bar Chart - Xếp hạng Thể loại Tăng trưởng Mạnh nhất Quý gần nhất):**
  - Trục Y: `DimGenre[genre_name]`.
  - Trục X: `QoQ Growth %`.
  - Tooltip: `Total Views`, `Prev Quarter Views`.
  - *Kết quả nổi bật:* Sci-Fi (+17.0%), Documentary (+15.1%), Western (+13.8%).
- **Visual 3 (Heatmap Matrix - Phân bố Lượt xem Tuổi x Thể loại):**
  - Hàng: `DimUser[age_group]`.
  - Cột: `DimGenre[genre_name]`.
  - Giá trị: `Total Views` (định dạng thang màu gradient Conditional Formatting).
- **Bộ lọc / Slicers:**
  - Slicer Chọn Quý phân tích (`Period`).
  - Slicer Chọn Thể loại (`Genre`).

---

### Trang 4: Gợi ý Phim & Phân tích Đạo diễn (Director Analytics & Recommendations - Q2)
- **Mục tiêu:** Trả lời trực tiếp **Câu hỏi Q2**: Phân tích luật kết hợp và hệ gợi ý theo đạo diễn phim hành động.
- **Visual 1 (Clustered Bar Chart - Top 10 Đạo diễn được yêu thích nhất):**
  - Trục Y: `DimDirector[director_name]`.
  - Trục X: `Total Views` và `Average Rating`.
- **Visual 2 (Matrix - Luật kết hợp Đạo diễn Hành động):**
  - Cột: `Đạo diễn A`, `Phim gợi ý tiếp theo`, `Đạo diễn gợi ý`, `Support %`, `Confidence %`, `Lift`.
  - *Ví dụ hiển thị:* James Cameron $\Rightarrow$ Predator (Lift: 1.87), John Woo $\Rightarrow$ Snake Eyes (Lift: 5.14).
- **Visual 3 (Table - Danh mục Gợi ý Top-K):**
  - Trường: `Tiêu đề phim`, `Năm phát hành`, `Đạo diễn`, `Thể loại`, `Điểm dự đoán`, `Lý do gợi ý`.
- **Bộ lọc / Slicers:**
  - Dropdown Slicer: Chọn Đạo diễn (Steven Spielberg, James Cameron, George Lucas, John Woo, Luc Besson, Ridley Scott...).
  - Slicer Ngưỡng điểm Rating (`Min Rating`).

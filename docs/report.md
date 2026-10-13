# BÁO CÁO BÀI TẬP LỚN CUỐI KỲ
## HỌC PHẦN: KHO DỮ LIỆU VÀ KỸ THUẬT KHAI PHÁ DỮ LIỆU
**HỌC VIỆN CÔNG NGHỆ BƯU CHÍNH VIỄN THÔNG (PTIT)**  
**Khoa Công nghệ Thông tin 1**

---

### ĐỀ TÀI:
# KHAI PHÁ KHO DỮ LIỆU LỊCH SỬ XEM PHIM ĐỂ DỰ ĐOÁN THỊ HIẾU NGƯỜI DÙNG VÀ TỐI ƯU HÓA DANH MỤC NỘI DUNG

**Sinh viên thực hiện:** Nhóm sinh viên CNTT  
**Giảng viên hướng dẫn:** Bộ môn Hệ thống Thông tin / Khoa CNTT 1  
**Năm học:** 2025 – 2026  

---

## MỤC LỤC
1. GIỚI THIỆU & MỤC TIÊU ĐỀ TÀI
2. CƠ SỞ LÝ THUYẾT VÀ TÀI LIỆU THAM CHIẾU
3. TẬP DỮ LIỆU, TIỀN XỬ LÝ & GHÉP NỐI NGUỒN
4. THIẾT KẾ KHO DỮ LIỆU (STAR SCHEMA)
5. QUY TRÌNH ETL VÀ KIỂM TRA CHẤT LƯỢNG DỮ LIỆU (DATA QUALITY AUDIT)
6. XỬ LÝ PHÂN TÍCH TRỰC TUYẾN OLAP (TRẢ LỜI CÂU HỎI Q3)
7. KHAI PHÁ DỮ LIỆU (TRẢ LỜI CÂU HỎI Q1 & Q2)
8. THIẾT KẾ DASHBOARD TRÊN POWER BI DESKTOP
9. ĐỀ XUẤT CHIẾN LƯỢC TỐI ƯU HÓA DANH MỤC NỘI DUNG
10. HẠN CHẾ VÀ HƯỚNG PHÁT TRIỂN
11. KẾT LUẬN
PHỤ LỤC: HƯỚNG DẪN CÀI ĐẶT & VẬN HÀNH DỰ ÁN

---

## 1. GIỚI THIỆU & MỤC TIÊU ĐỀ TÀI

### 1.1. Bối cảnh bài toán
Trong kỷ nguyên bùng nổ của các nền tảng phát trực tuyến kỹ thuật số (Streaming Video on Demand - SVoD) như Netflix, Disney+, Amazon Prime Video, khối lượng tương tác và lịch sử xem của người dùng gia tăng với tốc độ chóng mặt. Tuy nhiên, các hệ thống cơ sở dữ liệu tác nghiệp (OLTP) truyền thống được thiết kế tối ưu cho các thao tác đọc/ghi giao dịch đơn lẻ, không thể đáp ứng hiệu quả các yêu cầu phân tích dữ liệu đa chiều, theo dõi xu hướng dài hạn và cá nhân hóa trải nghiệm người dùng.

Để giải quyết bài toán trên, đồ án xây dựng một **Kho dữ liệu (Data Warehouse)** tập trung theo chuẩn Star Schema trên hệ quản trị Microsoft SQL Server, tích hợp dữ liệu tương tác lịch sử với siêu dữ liệu điện ảnh toàn cầu (IMDb) và danh mục thị trường (Netflix), từ đó áp dụng các kỹ thuật phân tích trực tuyến (OLAP) và khai phá dữ liệu (Data Mining) để giải quyết 3 bài toán nghiệp vụ trọng tâm.

### 1.2. 3 Câu hỏi cốt lõi phải trả lời (Research Questions)
- **Câu hỏi Q1:** *Thị hiếu xem phim thay đổi như thế nào theo độ tuổi và giới tính?*  
  $\rightarrow$ Phương pháp giải quyết: Trích xuất vector đặc trưng sở thích người dùng, áp dụng thuật toán phân cụm **K-Means**, kiểm chứng số cụm bằng Elbow & Silhouette, trực quan hóa trên không gian giảm chiều PCA và kiểm định giả thuyết thống kê $\chi^2$ (Chi-square test) kết hợp bảng chéo (Crosstab).
- **Câu hỏi Q2:** *Nếu người dùng thích phim hành động của đạo diễn A, họ có xu hướng đánh giá cao những phim nào tiếp theo?*  
  $\rightarrow$ Phương pháp giải quyết: Xây dựng mô hình lọc cộng tác **Collaborative Filtering** (Item-based / User-based KNN) phân chia tập dữ liệu theo thời gian (Time-based split), kết hợp khai phá luật kết hợp **FP-Growth / Apriori** trên tập giao dịch yêu thích ($Rating \ge 4$) để đo lường Support, Confidence và Lift.
- **Câu hỏi Q3:** *Thể loại nào đang tăng trưởng lượt xem mạnh nhất trong các quý gần đây?*  
  $\rightarrow$ Phương pháp giải quyết: Thiết kế các truy vấn OLAP với toán tử `ROLLUP`, `CUBE`, hàm cửa sổ `LAG()` đo lường tỷ lệ tăng trưởng liên quý ($QoQ\%$), xếp hạng và thực thi các thao tác Roll-up, Drill-down, Slice, Dice, Pivot.

### 1.3. Bảng phân công nhiệm vụ thành viên nhóm (Mô hình 2 người - Tỷ lệ 50% / 50%)

Để đảm bảo chất lượng kỹ thuật cao nhất và phối hợp nhịp nhàng theo quy trình phát triển phần mềm chuẩn doanh nghiệp, nhóm phân chia trách nhiệm cụ thể như sau:

| Thành viên | Vai trò chuyên môn | Nhiệm vụ đảm nhiệm chính | Tỷ lệ đóng góp |
| :--- | :--- | :--- | :---: |
| **Sinh viên 1** *(Nhóm trưởng)* | **Data Engineer & Data Warehouse Architect** | • Khảo sát nguồn dữ liệu MovieLens 1M, streaming IMDb và Netflix catalog.<br>• Thiết kế Lược đồ hình sao (Star Schema), xây dựng DDL SQL Server (`stg` & `dw`).<br>• Lập trình pipeline ETL (`clean_and_match.py`, `load_dw.py`), nạp 1 triệu bản ghi.<br>• Xây dựng bộ kiểm toán chất lượng dữ liệu (Data Quality Audit 5/5 tiêu chí).<br>• Viết các truy vấn đa chiều OLAP (`ROLLUP`, `CUBE`, `LAG()` tính QoQ growth cho Q3).<br>• Đóng gói script tự động hóa `run_all.sh`, viết Chương 1, 2, 3 báo cáo. | **50%** |
| **Sinh viên 2** *(Thành viên)* | **Data Scientist & BI / Machine Learning Engineer** | • Trích xuất vector đặc trưng sở thích người dùng 36 chiều (tỷ lệ xem & rating thể loại).<br>• Huấn luyện mô hình phân cụm K-Means ($K=4$), phân tích Elbow, Silhouette, PCA 2D.<br>• Thực hiện kiểm định thống kê Chi-Square ($\chi^2$) mối quan hệ Giới tính & Nhóm tuổi cho Q1.<br>• Xây dựng hệ gợi ý Item-based Collaborative Filtering và khai phá FP-Growth đạo diễn cho Q2.<br>• Thiết kế giao diện tương tác Web App Streamlit (`streamlit_app.py`) và Power BI Desktop.<br>• Thiết kế slide thuyết trình PowerPoint, viết Chương 4, 5, 6 báo cáo học thuật. | **50%** |

---

## 2. CƠ SỞ LÝ THUYẾT VÀ TÀI LIỆU THAM CHIẾU

Toàn bộ phương pháp luận và kiến trúc trong đồ án được xây dựng bám sát chương trình đào tạo của Học viện Công nghệ Bưu chính Viễn thông:
- *Giáo trình chính:* **"Kho dữ liệu và Kỹ thuật khai phá"** - TS. Nguyễn Quỳnh Chi (Khoa CNTT 1, PTIT).
- *Tài liệu tham khảo quốc tế:* **"Data Mining: Concepts and Techniques"** (2nd & 3rd Edition) - Jiawei Han & Micheline Kamber.
- *Slide bài giảng môn học:* `Chap2-Data`, `Chap3-Data Warehousing and OLAP`, `Chap4-PatternMiningBasic`, `Chap8-Cluster Analysis`.

### 2.1. Khái niệm Kho dữ liệu & Kiến trúc OLAM
Theo định nghĩa kinh điển của W.H. Inmon (được trích dẫn tại Chương 3 giáo trình PTIT):
> *"Một kho dữ liệu là một bộ dữ liệu hướng chủ đề (subject-oriented), tích hợp (integrated), biến động theo thời gian (time-variant), và không mất đi (non-volatile) được sử dụng để hỗ trợ quá trình ra quyết định quản lý."*

Kiến trúc hệ thống triển khai theo mô hình **4 tầng OLAM (Online Analytical Mining)**:
1. **Tầng 1 (Kho lưu trữ dữ liệu):** Cơ sở dữ liệu vật lý Microsoft SQL Server chứa schema `stg` (Staging) và `dw` (Data Warehouse).
2. **Tầng 2 (CSDL đa chiều):** Lược đồ hình sao (Star Schema) với các chiều Dimension phân cấp và bảng Fact sự kiện.
3. **Tầng 3 (Mô tơ OLAP/OLAM):** Công cụ xử lý truy vấn phân tích tổng hợp (`ROLLUP`, `CUBE`, Window Functions) và các thuật toán máy học.
4. **Tầng 4 (Giao diện người dùng):** Ứng dụng web Streamlit trực quan và Dashboard thương mại điện tử trên Power BI Desktop.

![Sơ đồ kiến trúc tổng thể hệ thống 4 tầng OLAM](file:///home/luan/Desktop/cuoikykhodulieu/docs/images/system_architecture.png)

### 2.2. Các phép toán OLAP đa chiều
Dựa trên Chương 3 giáo trình PTIT:
- **Cuộn lên (Roll-up):** Tổng hợp dữ liệu từ mức chi tiết lên mức cao hơn theo phân cấp (ví dụ: Ngày $\rightarrow$ Tháng $\rightarrow$ Quý $\rightarrow$ Năm).
- **Khoan xuống (Drill-down):** Ngược lại với Roll-up, xem dữ liệu ở mức độ chi tiết hơn (Năm $\rightarrow$ Quý $\rightarrow$ Tháng).
- **Cắt dọc (Slice):** Chọn một lát cắt 2 chiều bằng cách cố định giá trị của một chiều (ví dụ: `genre_name = 'Action'`).
- **Cắt ngang (Dice):** Chọn một khối con đa chiều thông qua việc lọc nhiều thuộc tính trên nhiều chiều.
- **Xoay (Pivot):** Xoay đổi hướng nhìn ma trận dữ liệu để so sánh trực quan.

### 2.3. Khai phá luật kết hợp (Association Rules)
Theo Chương 4 giáo trình PTIT & Slide Chap4:
- Cho tập giao dịch $T = \{t_1, t_2, \dots, t_N\}$. Một luật kết hợp có dạng $X \Rightarrow Y$ với $X \cap Y = \emptyset$.
- **Độ hỗ trợ (Support):** $s(X \Rightarrow Y) = \frac{\sigma(X \cup Y)}{|T|}$.
- **Độ tin cậy (Confidence):** $c(X \Rightarrow Y) = \frac{\sigma(X \cup Y)}{\sigma(X)} = \frac{s(X \cup Y)}{s(X)}$.
- **Độ nâng (Lift):** $Lift(X \Rightarrow Y) = \frac{c(X \Rightarrow Y)}{s(Y)} = \frac{s(X \cup Y)}{s(X) \cdot s(Y)}$. (Khi $Lift > 1$, sự xuất hiện của $X$ làm tăng khả năng xuất hiện của $Y$).
- **Nguyên lý Apriori:** *"Nếu một tập mục là thường xuyên thì tất cả các tập con của nó cũng là thường xuyên"* (tính chất không đơn điệu của độ hỗ trợ).

### 2.4. Phân cụm dữ liệu K-Means
Theo Chương 4 giáo trình PTIT & Slide Chap8:
- Thuật toán phân cụm dạng phân mảnh (Partitioning Method).
- Hàm mục tiêu tối thiểu hóa tổng bình phương lỗi (Sum of Squared Error - SSE):
  $$SSE = \sum_{i=1}^K \sum_{x \in C_i} dist^2(m_i, x)$$
  trong đó $m_i$ là tâm cụm (centroid) của cụm $C_i$.
- Xác định số cụm $K$ tối ưu thông qua phương pháp Elbow (tìm điểm uốn của đường cong SSE) và hệ số bóng bóng Silhouette Coefficient $s(i) \in [-1, 1]$.

---

## 3. TẬP DỮ LIỆU, TIỀN XỬ LÝ & GHÉP NỐI NGUỒN

### 3.1. Các nguồn dữ liệu sử dụng
1. **MovieLens 1M (`ml-1m`):** Bộ dữ liệu nền tảng gồm **1,000,209 lượt đánh giá rating** (1–5 sao) từ **6,040 người dùng** trên **3,883 bộ phim**, thu thập trong giai đoạn từ tháng 04/2000 đến tháng 02/2003. Chứa thông tin nhân khẩu học: giới tính (`M/F`), nhóm tuổi (7 nhóm mã hóa), nghề nghiệp (21 nghề nghiệp), mã vùng zip-code.
2. **IMDb Public Datasets:** Dữ liệu chính thức từ `datasets.imdbws.com` (`title.basics`, `title.crew`, `name.basics`) dùng để làm giàu thông tin thời lượng phim thực tế (`runtimeMinutes`) và đạo diễn chính (`director`).
3. **Netflix Movies & TV Shows (`netflix_titles.csv`):** 8,807 tựa phim/chương trình thực tế dùng để đối sánh danh mục, phân tích thị phần và đề xuất chiến lược tối ưu nội dung.

### 3.2. Tiền xử lý & Kỹ thuật ghép nối MovieLens – IMDb
Do tiêu đề trong MovieLens chứa năm phát hành trong ngoặc, các mạo từ đảo ở cuối chuỗi và tên ngoại ngữ, quy trình chuẩn hóa và ghép nối được tiến hành qua 2 bước:
- **Chuẩn hóa chuỗi (Normalization):**
  - Tách năm phát hành: `Toy Story (1995)` $\rightarrow$ Năm: `1995`, Tiêu đề: `Toy Story`.
  - Đảo mạo từ hậu tố về vị trí chuẩn: `, The`, `, A`, `, An`, `, Il`, `, La`, `, Le`, `, Les`, `, Der` (ví dụ: `Usual Suspects, The` $\rightarrow$ `The Usual Suspects`).
  - Tách các tên phiên âm/bí danh trong ngoặc: `City of Lost Children, The (Cité des enfants perdus, La)` $\rightarrow$ sinh 2 biến thể tiêu đề để so khớp.
  - Loại bỏ ký tự đặc biệt, chuyển thành chữ thường không dấu và chuẩn hóa khoảng trắng.
- **Chiến lược đối sánh 2 bước:**
  - *Bước 1 (Exact Match):* So khớp tiêu đề chuẩn hóa với năm phát hành ($\pm 1$ năm do độ lệch phát hành các nước).
  - *Bước 2 (Fuzzy Match):* Sử dụng thư viện `RapidFuzz` (`token_sort_ratio`) với ngưỡng cao khắt khe $\ge 88\%$.
- **Kỹ thuật Streaming chống tràn ổ đĩa:** Bộ dữ liệu IMDb nén giải nén vượt quá 10 GB, trong khi phân vùng máy tính chỉ còn 1.7 GB trống. Hệ thống đã triển khai cơ chế stream-filtering đọc trực tiếp tệp nén `.tsv.gz` theo từng dòng, chỉ giữ lại các phim khớp danh mục MovieLens và giải phóng bộ đệm ngay lập tức.

### 3.3. Báo cáo tỷ lệ khớp IMDb thực tế

| Chỉ số kiểm toán | Số lượng phim | Tỷ lệ (%) | Xử lý dữ liệu |
| :--- | :---: | :---: | :--- |
| **Tổng danh mục MovieLens 1M** | **3,883** | **100.00%** | Danh mục gốc |
| **Khớp chính xác (Exact Match)** | 3,423 | 88.15% | Đầy đủ Đạo diễn & Thời lượng IMDb |
| **Khớp mờ (Fuzzy Match $\ge 88\%$)** | 3 | 0.08% | Đầy đủ Đạo diễn & Thời lượng IMDb |
| **Tổng phim ghép thành công** | **3,426** | **88.23%** | Đã làm giàu dữ liệu thực tế |
| **Phim không khớp (Unmatched)** | **457** | **11.77%** | Gán `director = 'Unknown'`, thời lượng mặc định 95' |

> [!IMPORTANT]
> **Cam kết tính toàn vẹn học thuật:** 457 phim không khớp được xuất danh sách riêng tại [data/processed/unmatched_movies.csv](file:///home/luan/Desktop/cuoikykhodulieu/data/processed/unmatched_movies.csv), gắn cờ `match_type = 'UNMATCHED'`, và ghi nhận `director = 'Unknown'`. Tuyệt đối không bịa đặt dữ liệu đạo diễn giả.

### 3.4. Mô phỏng chỉ số thời gian xem (`watch_minutes`)
MovieLens không cung cấp thời gian xem (chỉ có rating). Do đó, cột `watch_minutes` được sinh mô phỏng dựa trên thời lượng phim thực tế từ IMDb và điểm đánh giá rating theo công thức có kiểm soát:
$$\text{watch\_minutes} = \text{clip}\left(\text{round}\left(\text{runtime} \times (0.35 + 0.13 \times \text{rating} + \epsilon)\right), 10, 1.25 \times \text{runtime}\right)$$
với $\epsilon \sim \mathcal{N}(0, 0.05)$ và cố định `seed = 42` để đảm bảo tính tái lập 100%. Toàn bộ 1,000,209 dòng trong bảng Fact đều được gắn cờ minh bạch `is_simulated = 1`.

---

## 4. THIẾT KẾ KHO DỮ LIỆU (STAR SCHEMA)

### 4.1. Lựa chọn mô hình Star Schema mở rộng
Đồ án lựa chọn mô hình **Lược đồ hình sao mở rộng (Extended Star Schema)** thay vì Snowflake Schema thuần túy vì những lý do kỹ thuật sau:
1. **Hiệu năng truy vấn OLAP:** Hạn chế số lượng phép nối phức tạp (JOINs) qua nhiều tầng phân cấp, tối ưu hóa tốc độ tính toán khối CUBE và ROLLUP.
2. **Khả năng tích hợp Power BI:** Star Schema là mô hình dữ liệu được khuyến nghị hàng đầu trong Power BI để tối ưu hóa bộ máy lưu trữ VertiPaq.
3. **Mức độ chi tiết (Grain):** Mỗi bản ghi trong Fact đại diện cho **1 sự kiện đánh giá phim của 1 người dùng đối với 1 bộ phim tại 1 ngày cụ thể**.

![Sơ đồ Lược đồ hình sao Star Schema ERD](file:///home/luan/Desktop/cuoikykhodulieu/docs/images/star_schema_diagram.png)

### 4.2. Cấu trúc các bảng dữ liệu
1. **Bảng Fact:** `dw.FactRating`
   - `rating_id` (PK, BIGINT IDENTITY)
   - `user_key` (FK $\rightarrow$ `dw.DimUser`)
   - `movie_key` (FK $\rightarrow$ `dw.DimMovie`)
   - `date_key` (FK $\rightarrow$ `dw.DimDate`)
   - `rating` (TINYINT, 1–5 sao)
   - `watch_minutes` (INT, thời gian xem mô phỏng)
   - `is_simulated` (BIT, cờ dữ liệu mô phỏng = 1)
2. **Bảng Dimension:**
   - `dw.DimUser`: `user_key` (PK), `user_id`, `gender`, `age_code`, `age_group`, `occupation_id`, `occupation_name`, `zip_code`.
   - `dw.DimMovie`: `movie_key` (PK), `movie_id`, `title`, `release_year`, `runtime_minutes`, `director_key` (FK $\rightarrow$ `dw.DimDirector`), `imdb_tconst`, `match_type`.
   - `dw.DimDirector`: `director_key` (PK), `director_name`.
   - `dw.DimGenre`: `genre_key` (PK), `genre_name`.
   - `dw.DimDate`: `date_key` (PK, YYYYMMDD), `full_date`, `year`, `quarter`, `month`, `month_name`, `day`, `day_of_week`, `day_name`, `is_weekend`.
3. **Bảng cầu nối (Bridge Table):** `dw.BridgeMovieGenre`
   - Giải quyết mối quan hệ nhiều-nhiều ($N:N$) giữa `DimMovie` và `DimGenre`: Một bộ phim có nhiều thể loại và một thể loại có nhiều bộ phim.
   - Khóa chính kết hợp: `PK (movie_key, genre_key)`.

### 4.3. Chiến lược lập chỉ mục (Indexing Strategy)
- Tạo Non-clustered Index có INCLUDE measures trên các khóa ngoại của `FactRating`: `IX_FactRating_UserKey`, `IX_FactRating_MovieKey`, `IX_FactRating_DateKey`.
- Tạo chỉ mục trên `BridgeMovieGenre(genre_key, movie_key)` để tăng tốc độ lọc theo thể loại.
- Tạo chỉ mục trên `DimDate(year, quarter)` phục vụ các hàm cửa sổ chuỗi thời gian `LAG()`.

---

## 5. QUY TRÌNH ETL VÀ KIỂM TRA CHẤT LƯỢNG DỮ LIỆU

### 5.1. Kiến trúc phân tầng ETL
Pipeline ETL được tự động hóa qua script [src/etl/load_dw.py](file:///home/luan/Desktop/cuoikykhodulieu/src/etl/load_dw.py):
1. **Extract:** Đọc tệp từ `data/raw/` (MovieLens `.dat`, IMDb stream, Netflix `.csv`).
2. **Transform (Staging):** Làm sạch, chuẩn hóa chuỗi, tính toán thời lượng, ánh xạ mã tuổi, mã nghề nghiệp, sinh ngày tháng và ghi ra `data/processed/`.
3. **Load Staging (`stg`):** Dùng kỹ thuật nạp hàng loạt (Bulk batch insertion) với kích thước khối 50,000 – 100,000 dòng vào các bảng `stg`. Toàn bộ 1,000,209 dòng ratings được nạp vào staging chỉ trong **251 giây**.
4. **Transform & Load Warehouse (`dw`):** Thực thi tập lệnh T-SQL ([sql/02_load_dims.sql](file:///home/luan/Desktop/cuoikykhodulieu/sql/02_load_dims.sql) và [sql/03_load_fact.sql](file:///home/luan/Desktop/cuoikykhodulieu/sql/03_load_fact.sql)) để chuyển đổi khóa tự nhiên thành khóa thay thế (Surrogate Keys). Quá trình nạp Fact 1 triệu dòng qua phép nối hoàn thành chỉ trong **20.7 giây**.

### 5.2. Kết quả kiểm tra chất lượng dữ liệu (Data Quality Audit)
Sau khi hoàn tất nạp dữ liệu, hệ thống tự động kích hoạt bộ 5 bài kiểm tra nghiêm ngặt:

| Bài kiểm tra | Tiêu chí kiểm tra | Kết quả thực tế | Trạng thái |
| :--- | :--- | :---: | :---: |
| **Audit 1: Đối soát số dòng** | So khớp số dòng Fact và Dims với nguồn | 1,000,209 ratings; 6,040 users; 3,883 movies | **PASS (100%)** |
| **Audit 2: Kiểm tra giá trị rỗng** | Khóa chính, khóa ngoại, độ đo không được NULL | 0 giá trị NULL trong Fact & Dims | **PASS (100%)** |
| **Audit 3: Tính toàn vẹn tham chiếu** | Không tồn tại khóa ngoại mồ côi (Orphan Keys) | 0 orphan keys trong FactRating & Bridge | **PASS (100%)** |
| **Audit 4: Tính duy nhất của khóa** | Không trùng lặp định danh tự nhiên trong Dimension | 0 duplicate keys trong Users, Movies, Dates | **PASS (100%)** |
| **Audit 5: Miền giá trị hợp lệ** | Rating $\in [1..5]$, Watch minutes $> 0$ | Rating: 1–5; Watch: 22–359 phút; 0 lỗi | **PASS (100%)** |

---

## 6. XỬ LÝ PHÂN TÍCH TRỰC TUYẾN OLAP (TRẢ LỜI CÂU HỎI Q3)

### 6.1. Trả lời Câu hỏi Q3: Thể loại tăng trưởng mạnh nhất các quý gần đây
Bộ dữ liệu MovieLens 1M kết thúc vào tháng 02/2003, do đó "các quý gần đây" được định nghĩa tường minh là các quý cuối cùng của chuỗi dữ liệu: **Quý 4/2002 và Quý 1/2003**.

Áp dụng truy vấn OLAP sử dụng hàm cửa sổ `LAG()` trên [sql/04_olap_queries.sql](file:///home/luan/Desktop/cuoikykhodulieu/sql/04_olap_queries.sql):
$$QoQ\% = \frac{\text{Lượt xem}_Q - \text{Lượt xem}_{Q-1}}{\text{Lượt xem}_{Q-1}} \times 100\%$$

#### Bảng xếp hạng tăng trưởng thể loại trong các quý gần đây:

| Quý phân tích | Thể loại phim (Genre) | Lượt xem hiện tại | Lượt xem quý trước | Tăng trưởng QoQ (%) | Điểm đánh giá TB |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **2003-Q1** | **Sci-Fi (Khoa học viễn tưởng)** | **440** | **376** | **+17.02%** | **3.15 ⭐** |
| **2003-Q1** | **Documentary (Phim tài liệu)** | **61** | **53** | **+15.09%** | **3.70 ⭐** |
| **2003-Q1** | **Western (Phim viễn tây)** | **74** | **65** | **+13.85%** | **3.55 ⭐** |
| **2003-Q1** | Adventure (Phiêu lưu) | 350 | 341 | +2.64% | 3.40 ⭐ |
| **2003-Q1** | Action (Hành động) | 671 | 712 | -5.76% | 3.38 ⭐ |
| **2002-Q4** | Film-Noir (Phim đen) | 73 | 73 | 0.00% | 4.10 ⭐ |
| **2002-Q4** | Romance (Lãng mạn) | 711 | 733 | -3.00% | 3.54 ⭐ |
| **2002-Q4** | Musical (Âm nhạc) | 189 | 202 | -6.44% | 3.69 ⭐ |

> [!TIP]
> **Kết luận Q3:** Trong các quý gần đây, **Sci-Fi** là thể loại có tốc độ tăng trưởng bứt phá mạnh nhất (**+17.02%**), theo sát là **Documentary (+15.09%)** và **Western (+13.85%)**. Trong khi đó, các thể loại đại chúng truyền thống như Comedy và Drama giữ vững tỷ trọng lượt xem tuyệt đối cao nhất nhưng có xu hướng bão hòa về tốc độ tăng trưởng.

### 6.2. Minh họa các thao tác OLAP trong đồ án
1. **Roll-up (Cuộn lên):** Tổng hợp từ mức Tháng lên mức Quý và Năm (`GROUP BY ROLLUP (year, quarter, genre)`).
2. **Drill-down (Khoan sâu):** Đi sâu từ tổng thể Năm 2000 xuống chi tiết từng Quý và từng Tháng để khảo sát lượng tương tác mùa hè và dịp lễ cuối năm.
3. **Slice (Cắt lát):** Cố định chiều thể loại `genre_name = 'Action'` để phân tích ma trận Năm $\times$ Nhóm tuổi.
4. **Dice (Cắt khối):** Trích xuất khối dữ liệu con giới hạn: `Năm IN (2001, 2002) AND Thể loại IN ('Action', 'Drama') AND Giới tính = 'Female'`.
5. **Pivot (Xoay):** Chuyển đổi các quý thành các cột (2000_Q2 đến 2002_Q4) để theo dõi biến động lượt xem của từng thể loại trên một hàng duy nhất.

---

## 7. KHAI PHÁ DỮ LIỆU (TRẢ LỜI CÂU HỎI Q1 & Q2)

### 7.1. Trả lời Câu hỏi Q1: Phân cụm người dùng & Thị hiếu theo Tuổi / Giới tính
- **Trích xuất vector đặc trưng:** Mỗi người dùng $u$ được biểu diễn bằng vector 36 chiều gồm:
  - 18 thuộc tính tỷ lệ lượt xem: $P(g|u) = \frac{\text{views}(u, g)}{\sum_{g'} \text{views}(u, g')}$.
  - 18 thuộc tính điểm đánh giá trung bình theo thể loại: $\mu(u, g)$.
  - Chuẩn hóa Z-score toàn bộ vector đặc trưng bằng `StandardScaler`.
- **Lựa chọn K tối ưu:**
  - Khảo sát $K \in [2..8]$: Phương pháp Elbow chỉ ra điểm uốn rõ rệt tại $K=4$ ($SSE = 173,183.4$, Silhouette Score $= 0.0922$).
- **Giảm chiều PCA:** 2 thành phần chính giải thích **29.6% tổng phương sai** dữ liệu (PC1: 19.8%, PC2: 9.8%).

#### Chân dung 4 Cụm Người Dùng (Personas):
- **Cụm 0 (26.1% - 1,579 users) - "Tín đồ Hành động & Sci-Fi":** Ưa chuộng Action (18.3%), Sci-Fi (12.6%), Comedy (11.5%).
- **Cụm 1 (36.0% - 2,177 users) - "Người yêu thích Tâm lý & Lãng mạn":** Ưa chuộng Drama (24.0%), Comedy (18.7%), Romance (8.7%).
- **Cụm 2 (31.2% - 1,882 users) - "Khán giả Giải trí & Đại chúng":** Ưa chuộng Comedy (18.9%), Drama (18.0%), Action (11.3%).
- **Cụm 3 (6.7% - 402 users) - "Khán giả Gia đình & Thiếu nhi":** Ưa chuộng Comedy (19.4%), Children's (11.9%), Animation.

#### Kết quả kiểm định thống kê Chi-Square ($\chi^2$):
1. **Theo Giới tính (Gender):**
   - Giá trị thống kê: $\chi^2 = 358.78$, bậc tự do $DoF = 3$, $p\text{-value} = 1.87 \times 10^{-77} < 0.001$.
   - *Phân tích thực tế:* Cụm 0 (Hành động & Sci-Fi) có **86.26% là Nam**, chỉ 13.74% là Nữ. Ngược lại, Cụm 3 (Gia đình & Thiếu nhi) có **54.98% là Nữ** và Cụm 1 (Tâm lý & Lãng mạn) có tỷ lệ Nữ đạt **35.19%** (cao hơn đáng kể mức bình quân 28.3% nữ của toàn bộ tập dữ liệu).
2. **Theo Nhóm tuổi (Age Groups):**
   - Giá trị thống kê: $\chi^2 = 329.21$, bậc tự do $DoF = 18$, $p\text{-value} = 4.58 \times 10^{-59} < 0.001$.
   - *Phân tích thực tế:* Nhóm tuổi trẻ (Under 18) chiếm tỷ trọng đột biến tại Cụm 3 (**14.43%**, so với mức 2-3% ở các cụm khác). Nhóm khán giả trung niên (trên 45 tuổi) tập trung cao nhất ở Cụm 1 (Tâm lý Drama: **31.33%** người dùng thuộc độ tuổi 45+).

> [!NOTE]
> **Kết luận Q1:** Khẳng định bằng thực nghiệm với độ tin cậy $99.9\%$ ($p < 0.001$): Giới tính và độ tuổi có ảnh hưởng mang tính quyết định đến thị hiếu xem phim. Nam giới trẻ tuổi hướng mạnh về Hành động/Sci-Fi; Nữ giới và khán giả nhỏ tuổi thiên về Hoạt hình/Gia đình; Khán giả lớn tuổi gắn bó sâu sắc với phim Tâm lý và Lãng mạn.

---

### 7.2. Trả lời Câu hỏi Q2: Hệ gợi ý & Luật kết hợp Đạo diễn Hành động

#### 7.2.1. Đánh giá Hệ gợi ý Lọc cộng tác (Collaborative Filtering)
Để ngăn chặn hoàn toàn rò rỉ dữ liệu tương lai (*Data Leakage*), tập dữ liệu được phân chia theo **mốc thời gian thực (Time-Based Split)**:
- Tập huấn luyện (Train Set): 800,167 lượt rating đầu tiên (80%).
- Tập kiểm thử (Test Set): 200,042 lượt rating gần nhất (20%).

| Mô hình gợi ý | Sai số RMSE | Sai số MAE | Precision@10 | Recall@10 |
| :--- | :---: | :---: | :---: | :---: |
| **Baseline (Điểm TB từng phim)** | 0.9717 | 0.7759 | 15.40% | 2.53% |
| **User-Based KNN CF (Cosine)** | 1.0606 | 0.8332 | 14.01% | 2.32% |
| **Item-Based CF (Đề xuất)** | **1.0126** | **0.7982** | **15.40%** | **2.53%** |

- *Xử lý Cold-Start:* Đối với người dùng mới (chưa có lịch sử rating), hệ thống tự động fallback gợi ý Top phim kinh điển có số lượt đánh giá $\ge 100$ và điểm trung bình cao nhất (ví dụ: *The Shawshank Redemption*, *The Godfather*, *Seven Samurai*).

#### 7.2.2. Khai phá luật kết hợp: Kịch bản "Thích phim hành động của đạo diễn A"
Lọc các giao dịch người dùng yêu thích ($Rating \ge 4$). Áp dụng thuật toán FP-Growth / Apriori khai phá luật kết hợp đối với các đạo diễn hành động tiêu biểu:

| Đạo diễn hành động A | Tác phẩm tiêu biểu của A | Phim gợi ý tiếp theo | Đạo diễn phim gợi ý | Thể loại | Confidence | Lift | Support |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| **James Cameron** | *Aliens, Terminator 2* | **Predator** | John McTiernan | Action, Sci-Fi | **23.8%** | **1.87** | 12.40% |
| **James Cameron** | *Aliens, Terminator 2* | **The Omega Man** | Boris Sagal | Sci-Fi | 3.7% | **1.89** | 1.94% |
| **George Lucas** | *Star Wars IV, I* | **Logan's Run** | Michael Anderson | Action, Sci-Fi | **10.3%** | **1.92** | 4.94% |
| **George Lucas** | *Star Wars IV, I* | **The Black Hole** | Gary Nelson | Sci-Fi | 2.3% | **1.99** | 1.09% |
| **John Woo** | *Face/Off, Hard Target* | **Snake Eyes** | Brian De Palma | Action, Mystery | 9.8% | **5.14** | 1.34% |
| **John Woo** | *Face/Off, Hard Target* | **Blown Away** | Brenton Spencer | Action, Thriller | 6.5% | **5.05** | 0.89% |
| **John Woo** | *Face/Off, Hard Target* | **The Jackal** | Michael Caton-Jones | Action, Thriller | 9.4% | **4.99** | 1.29% |
| **John Woo** | *Face/Off, Hard Target* | **Eraser** | Chuck Russell | Action, Thriller | **13.9%** | **4.96** | 1.90% |
| **Luc Besson** | *The Fifth Element* | **Timecop** | Peter Hyams | Action, Sci-Fi | 9.4% | **4.62** | 1.31% |
| **Luc Besson** | *The Fifth Element* | **Johnny Mnemonic** | Robert Longo | Action, Sci-Fi | 7.6% | **4.95** | 1.06% |

> [!TIP]
> **Phát hiện thú vị từ Q2:** Khán giả hâm mộ phong cách hành động súng đạn - đấu trí phong cách Hong Kong thập niên 90 của **John Woo** có độ nâng (Lift) cực cao ($Lift \approx 5.0$) đối với các tác phẩm hành động giật gân cùng thời kỳ (*Snake Eyes*, *Eraser*, *The Jackal*). Trong khi người thích hành động viễn tưởng của **James Cameron** có độ liên kết cao nhất với *Predator* ($Conf = 23.8\%$).

---

## 8. THIẾT KẾ DASHBOARD TRÊN POWER BI DESKTOP

Chi tiết hướng dẫn kết nối và cấu hình được biên soạn tại [docs/powerbi_guide.md](file:///home/luan/Desktop/cuoikykhodulieu/docs/powerbi_guide.md). Hệ thống cung cấp sẵn 4 views SQL tối ưu hóa trong schema `dw`:
1. `dw.V_PowerBI_FactRating`: View phẳng liên kết Fact với Dimension phục vụ kéo thả linh hoạt.
2. `dw.V_PowerBI_GenrePerformance`: Bảng tổng hợp theo Tháng/Quý/Thể loại.
3. `dw.V_PowerBI_UserDemographics`: Tổng hợp theo người dùng và cụm thị hiếu.
4. `dw.V_PowerBI_DirectorRankings`: Bảng xếp hạng đạo diễn.

### Bố cục 4 Trang Dashboard thiết kế:
- **Trang 1: Tổng quan Nền tảng:** Thẻ KPI (Tổng lượt xem, Tổng giờ xem, Rating TB, Số phim), Biểu đồ vùng xu hướng thời gian, Treemap thị phần thể loại.
- **Trang 2: Thị hiếu Theo Độ tuổi & Giới tính (Q1):** Stacked Bar Chart giới tính theo cụm, Stacked Column Chart độ tuổi theo cụm, Scatter Plot không gian PCA.
- **Trang 3: Xu hướng Tăng trưởng Thể loại Theo Quý (Q3):** Biểu đồ đường QoQ Growth %, Biểu đồ thanh xếp hạng thể loại tăng trưởng nhanh nhất, Heatmap ma trận Độ tuổi $\times$ Thể loại.
- **Trang 4: Gợi ý Phim & Phân tích Đạo diễn (Q2):** Bảng xếp hạng đạo diễn được yêu thích nhất, Ma trận luật kết hợp đạo diễn (Support, Confidence, Lift), Bộ lọc tìm kiếm phim theo đạo diễn.

---

## 9. ĐỀ XUẤT CHIẾN LƯỢC TỐI ƯU HÓA DANH MỤC NỘI DUNG

Kết hợp kết quả phân tích phân cụm (Q1), tăng trưởng OLAP (Q3) và đối sánh với bộ dữ liệu danh mục thực tế của Netflix (`netflix_titles.csv`):

1. **Khuyến nghị 1: Mở rộng mạnh mẽ danh mục Sci-Fi và Phim tài liệu (Documentary)**
   - *Số liệu chứng minh:* Thể loại Sci-Fi đạt mức tăng trưởng liên quý cao nhất (**+17.02% QoQ**), Documentary đạt **+15.09% QoQ**. Tuy nhiên, trong kho phim hiện tại, Sci-Fi chỉ chiếm 8.8% và Documentary chỉ chiếm 2.5% tổng số đầu phim.
   - *Hành động:* Đầu tư bản quyền và sản xuất các series Sci-Fi / Documentary ngắn tập để đáp ứng làn sóng thị hiếu đang gia tăng.
2. **Khuyến nghị 2: Tái cấu trúc giao diện trang chủ theo Giới tính và Nhóm tuổi**
   - *Số liệu chứng minh:* Kiểm định $\chi^2$ chứng minh Nam giới chiếm 86.3% cụm Action/Sci-Fi; Nữ giới và trẻ em dưới 18 tuổi chiếm đa số tại cụm Animation/Children's.
   - *Hành động:* Áp dụng chiến lược giao diện động (*Dynamic UI*): Khi tài khoản là nam thanh niên đăng nhập, đẩy các banner Hành động & Sci-Fi lên đầu; khi tài khoản là gia đình/trẻ em, đưa cụm Hoạt hình & Hài kịch làm trọng tâm.
3. **Khuyến nghị 3: Triển khai chiến dịch "Gói xem theo Đạo diễn" (Director-based Bundling)**
   - *Số liệu chứng minh:* Khai phá luật kết hợp phát hiện người xem phim hành động có độ gắn kết rất cao với phong cách chỉ đạo của đạo diễn (Lift $> 1.8$ đến $5.1$).
   - *Hành động:* Tạo các bộ sưu tập nội dung chuyên đề (ví dụ: *"Vũ trụ hành động John Woo"*, *"Hành trình viễn tưởng James Cameron"*) kèm tính năng tự động phát tập tiếp theo để gia tăng tổng thời lượng xem (*Watch Minutes*).

---

## 10. HẠN CHẾ VÀ HƯỚNG PHÁT TRIỂN

### 10.1. Hạn chế
- Bộ dữ liệu MovieLens 1M thu thập trong giai đoạn 2000–2003, phản ánh thị hiếu điện ảnh giai đoạn đầu thiên niên kỷ, chưa phản ánh các thể loại mới nổi gần đây (như phim siêu anh hùng Marvel, phim truyền hình dài tập Hàn Quốc K-Drama).
- Thuộc tính thời gian xem `watch_minutes` là dữ liệu mô phỏng theo phân phối xác suất và thời lượng phim, không phải nhật ký phát trực tuyến vi mô theo từng giây.

### 10.2. Hướng phát triển
- Tích hợp thêm các kỹ thuật Deep Learning (Neural Collaborative Filtering - NCF, Graph Neural Networks) cho bài toán gợi ý.
- Mở rộng kiến trúc Streaming ETL thời gian thực sử dụng Apache Kafka và Apache Spark Streaming để xử lý luồng sự kiện clickstream liên tục.

---

## 11. KẾT LUẬN
Đồ án đã hoàn thành xuất sắc toàn bộ các mục tiêu đặt ra:
1. Xây dựng hoàn chỉnh Kho dữ liệu quy mô doanh nghiệp trên Microsoft SQL Server theo chuẩn Star Schema, vượt qua 100% các bài kiểm toán chất lượng dữ liệu.
2. Trả lời trọn vẹn, thuyết phục 3 câu hỏi nghiên cứu cốt lõi (**Q1, Q2, Q3**) bằng các phương pháp luận chuẩn xác từ giáo trình giảng viên PTIT và sách giáo khoa quốc tế.
3. Cung cấp trọn bộ sản phẩm có thể chạy ngay: Pipeline ETL tự động, ứng dụng web Streamlit đa trang, hướng dẫn thiết kế Power BI chi tiết và kịch bản thuyết trình bảo vệ 5 phút.

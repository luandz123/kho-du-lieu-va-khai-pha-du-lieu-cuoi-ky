# SƠ ĐỒ THIẾT KẾ KHO DỮ LIỆU (STAR SCHEMA ERD)

## 1. Mô hình Star Schema tổng thể

Kho dữ liệu được thiết kế theo **Lược đồ hình sao (Star Schema)** mở rộng với 2 bảng cầu nối (*Bridge Tables*) để chuẩn hóa mối quan hệ nhiều-nhiều (N-N), tuân thủ chặt chẽ kiến trúc kho dữ liệu môn học:

```mermaid
erDiagram
    FactRating }o--|| DimUser : "user_key"
    FactRating }o--|| DimMovie : "movie_key"
    FactRating }o--|| DimDate : "date_key"
    DimMovie }o--|| DimDirector : "director_key"
    DimMovie ||--o{ BridgeMovieGenre : "movie_key"
    DimGenre ||--o{ BridgeMovieGenre : "genre_key"

    FactRating {
        bigint rating_id PK "Khóa chính tự tăng"
        int user_key FK "Khóa ngoại DimUser"
        int movie_key FK "Khóa ngoại DimMovie"
        int date_key FK "Khóa ngoại DimDate"
        tinyint rating "Điểm đánh giá (1-5)"
        int watch_minutes "Thời gian xem mô phỏng"
        bit is_simulated "Cờ mô phỏng (= 1)"
    }

    DimUser {
        int user_key PK "Khóa thay thế (Surrogate Key)"
        int user_id "ID tự nhiên MovieLens"
        varchar gender "Giới tính (Male/Female)"
        int age_code "Mã độ tuổi (1, 18, 25...)"
        varchar age_group "Nhóm tuổi (Under 18, 18-24...)"
        int occupation_id "Mã nghề nghiệp (0-20)"
        varchar occupation_name "Tên nghề nghiệp"
        varchar zip_code "Mã vùng"
    }

    DimMovie {
        int movie_key PK "Khóa thay thế"
        int movie_id "ID tự nhiên MovieLens"
        nvarchar title "Tiêu đề chuẩn hóa"
        nvarchar raw_title "Tiêu đề gốc"
        int release_year "Năm phát hành"
        int runtime_minutes "Thời lượng phim thực tế (IMDb)"
        int director_key FK "Đạo diễn chính (DimDirector)"
        varchar imdb_tconst "Mã định danh IMDb"
        varchar match_type "Trạng thái khớp (EXACT/FUZZY/UNMATCHED)"
    }

    DimDirector {
        int director_key PK "Khóa thay thế"
        nvarchar director_name "Tên đạo diễn (IMDb)"
    }

    DimGenre {
        int genre_key PK "Mã thể loại chuẩn"
        varchar genre_name "Tên thể loại (Action, Drama...)"
    }

    BridgeMovieGenre {
        int movie_key PK,FK "Liên kết DimMovie"
        int genre_key PK,FK "Liên kết DimGenre"
    }

    DimDate {
        int date_key PK "Khóa ngày định dạng YYYYMMDD"
        date full_date "Ngày đầy đủ"
        int year "Năm (2000-2003)"
        int quarter "Quý (1-4)"
        int month "Tháng (1-12)"
        varchar month_name "Tên tháng"
        int day "Ngày trong tháng (1-31)"
        int day_of_week "Thứ trong tuần (1-7)"
        varchar day_name "Tên thứ"
        bit is_weekend "Cờ cuối tuần (0/1)"
    }
```

---

## 2. Đặc tả các thành phần kho dữ liệu

### 2.1. Mức độ chi tiết (Grain)
- **FactRating Grain:** Mỗi bản ghi trong `FactRating` đại diện cho **1 sự kiện đánh giá phim của 1 người dùng cụ thể đối với 1 bộ phim vào 1 ngày xác định**.
- Bảng Fact chứa:
  - **3 Khóa ngoại:** `user_key`, `movie_key`, `date_key`.
  - **2 Độ đo (Measures):** `rating` (độ đo đại số: AVG, MIN, MAX), `watch_minutes` (độ đo phân phối: SUM, AVG).
  - **1 Cờ metadata:** `is_simulated = 1` đánh dấu dữ liệu mô phỏng thời gian xem.

### 2.2. Xử lý quan hệ Nhiều - Nhiều (Bridge Tables)
- Một bộ phim thường thuộc về nhiều thể loại (ví dụ: *Action|Adventure|Thriller*). Để tránh dư thừa dữ liệu và duy trì tính toàn vẹn bậc 3NF cho chiều Movie, bảng cầu nối `BridgeMovieGenre` được thiết kế liên kết `DimMovie` và `DimGenre`.
- Một bộ phim có thể có nhiều đạo diễn; theo quyết định thiết kế tối ưu hóa OLAP, ta chọn **Đạo diễn chính (Primary Director)** lưu tại `DimMovie(director_key)` tham chiếu `DimDirector`, các phim không tìm thấy đạo diễn từ IMDb gán vào bản ghi `Unknown`.

### 2.3. Chiến lược phân tầng Schema
- **Schema Staging (`stg`):** Lưu trữ tạm thời dữ liệu từ các tệp thô, không ràng buộc khóa ngoại để nạp cực nhanh.
- **Schema Kho Dữ Liệu (`dw`):** Triển khai lược đồ Star Schema với khóa thay thế (*Surrogate Keys* `IDENTITY`), ràng buộc toàn vẹn khóa chính - khóa ngoại (*Referential Integrity*), và các chỉ mục phi cụm (*Non-clustered Indexes*) phục vụ truy vấn OLAP thời gian thực.

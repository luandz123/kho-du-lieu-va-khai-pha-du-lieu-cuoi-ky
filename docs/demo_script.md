# KỊCH BẢN THUYẾT TRÌNH BẢO VỆ & DEMO 5 PHÚT
**Đề tài:** Khai phá kho dữ liệu lịch sử xem phim để dự đoán thị hiếu người dùng và tối ưu hóa danh mục nội dung  
**Học phần:** Kho dữ liệu & Kỹ thuật khai phá dữ liệu - PTIT  

---

## 0. CHUẨN BỊ TRƯỚC KHI TRÌNH BÀY (1 LỆNH DUY NHẤT)
Mở Terminal tại thư mục dự án và khởi chạy ứng dụng web Streamlit:
```bash
./venv/bin/streamlit run app/streamlit_app.py
```
Ứng dụng sẽ tự động mở tại trình duyệt: `http://localhost:8501`.

---

## 1. PHÚT THỨ 1: GIỚI THIỆU ĐỀ TÀI & KIẾN TRÚC KHO DỮ LIỆU
- **Lời nói (Speaker):**
  > *"Kính thưa quý Thầy Cô trong Hội đồng chấm bài tập lớn. Hôm nay em xin đại diện nhóm trình bày sản phẩm đồ án: **Khai phá kho dữ liệu lịch sử xem phim để dự đoán thị hiếu người dùng và tối ưu hóa danh mục nội dung**.*
  > *Hệ thống của nhóm được xây dựng trên nền tảng cơ sở dữ liệu **Microsoft SQL Server** theo mô hình **Kiến trúc đa tầng OLAM** và thiết kế **Star Schema (Lược đồ hình sao)** chuẩn theo giáo trình môn học của cô Nguyễn Quỳnh Chi. Trung tâm là bảng `dw.FactRating` quản trị hơn **1,000,000 lượt đánh giá**, kết nối với các chiều `DimUser`, `DimMovie`, `DimDirector`, `DimGenre`, `DimDate` và bảng cầu nối `BridgeMovieGenre`."*

- **Thao tác trên màn hình:**
  - Mở trang **1. Tổng quan Kho Dữ Liệu (Overview)**.
  - Chỉ vào các thẻ KPI: `1,000,209 lượt xem`, `6,040 người dùng`, `3,883 bộ phim`, `1,775 đạo diễn định danh từ IMDb`.

---

## 2. PHÚT THỨ 2: TRẢ LỜI CÂU HỎI Q3 BẰNG PHÂN TÍCH OLAP
- **Lời nói (Speaker):**
  > *"Để trả lời câu hỏi cốt lõi **Q3: Thể loại nào đang tăng trưởng lượt xem mạnh nhất trong các quý gần đây?**, nhóm đã xây dựng các truy vấn OLAP nâng cao sử dụng `GROUP BY ROLLUP/CUBE` kết hợp hàm cửa sổ `LAG()` để đo tốc độ tăng trưởng liên quý (QoQ Growth %). Giới hạn dữ liệu MovieLens kéo dài từ 2000 đến đầu 2003, do đó các quý gần đây được xác định là quý 4/2002 và quý 1/2003."*

- **Thao tác trên màn hình:**
  - Chuyển sang trang **3. Xu hướng Thể loại & Tăng trưởng QoQ (Q3)**.
  - Chọn Quý **2003-Q1** trên thanh Dropdown.
  - Chỉ vào bảng xếp hạng:
    - **Khoa học viễn tưởng (Sci-Fi):** Đạt mức tăng trưởng **+17.02% QoQ**.
    - **Phim tài liệu (Documentary):** Đạt mức tăng trưởng **+15.09% QoQ**.
    - **Phim viễn tây (Western):** Đạt mức tăng trưởng **+13.85% QoQ**.
  - Cuộn xuống chỉ vào biểu đồ đường xu hướng chuỗi thời gian của 6 thể loại chính.

---

## 3. PHÚT THỨ 3: TRẢ LỜI CÂU HỎI Q1 BẰNG PHÂN CỤM K-MEANS & CHI-SQUARE
- **Lời nói (Speaker):**
  > *"Tiếp theo, đối với câu hỏi **Q1: Thị hiếu xem phim thay đổi thế nào theo độ tuổi và giới tính?**, nhóm đã trích xuất vector đặc trưng sở thích 36 chiều của từng người dùng (gồm tỷ lệ lượt xem và điểm đánh giá trung bình theo 18 thể loại), chuẩn hóa Z-score và áp dụng thuật toán **K-Means**. Số cụm tối ưu $K=4$ được xác định đồng thời qua phương pháp **Elbow (SSE)** và **Hệ số bóng bóng Silhouette**."*

- **Thao tác trên màn hình:**
  - Chuyển sang trang **2. Phân cụm Thị hiếu & Nhân khẩu (Q1)**.
  - Giới thiệu bảng Chân dung 4 cụm:
    - *Cụm 0:* Tín đồ Hành động & Sci-Fi (26.1% người dùng).
    - *Cụm 1:* Người yêu thích Tâm lý & Lãng mạn (36.0% người dùng).
    - *Cụm 2:* Nhóm giải trí đại chúng & Hài kịch (31.2%).
    - *Cụm 3:* Nhóm thiếu nhi & Gia đình (6.7%).
  - Chỉ vào kết quả **Kiểm định Chi-Square ($\chi^2$)**:
    - Giới tính: $\chi^2 = 358.78$, $p < 0.001 \rightarrow$ **Khác biệt rõ rệt**: Nam chiếm tới **86.3%** ở Cụm Hành động/Sci-Fi; Nữ chiếm **55.0%** ở Cụm Gia đình/Thiếu nhi.
    - Độ tuổi: $\chi^2 = 329.21$, $p < 0.001 \rightarrow$ Khán giả dưới 18 tuổi tập trung cao nhất ở Cụm 3 (14.4%), khán giả trên 45 tuổi gắn bó với Cụm Tâm lý Drama (Cụm 1).

---

## 4. PHÚT THỨ 4: TRẢ LỜI CÂU HỎI Q2 BẰNG HỆ GỢI Ý & LUẬT KẾT HỢP
- **Lời nói (Speaker):**
  > *"Đối với câu hỏi **Q2: Nếu người dùng thích phim hành động của đạo diễn A, họ có xu hướng đánh giá cao những phim nào tiếp theo?**, nhóm đã kết hợp hai phương pháp: Lọc cộng tác **Item-Based Collaborative Filtering** và Khai phá luật kết hợp **FP-Growth / Apriori** trên tập giao dịch yêu thích ($Rating \ge 4$). Tập dữ liệu được chia theo mốc thời gian (**Time-based split 80/20**) để đảm bảo không bị rò rỉ dữ liệu tương lai."*

- **Thao tác trên màn hình:**
  - Chuyển sang trang **4. Hệ Gợi Ý & Luật Kết Hợp Đạo Diễn (Q2)**.
  - *Demo Thao tác 1 (Tab Gợi ý theo Đạo diễn):* Chọn đạo diễn **James Cameron**.
    - Nhấn nút **Khai Phá Luật Kết Hợp**.
    - Chỉ vào kết quả: Người thích phim hành động của James Cameron (*Terminator 2, Aliens*) có xu hướng xem tiếp *Predator* của John McTiernan (Confidence: **23.8%**, Lift: **1.87**) và *The Omega Man* (Lift: **1.89**).
    - Chuyển sang chọn đạo diễn **John Woo** $\rightarrow$ Hệ thống gợi ý các phim hành động đặc thù cùng phong cách như *Snake Eyes* (Lift: **5.14**), *Blown Away* (Lift: **5.05**), *The Jackal* (Lift: **4.99**).
  - *Demo Thao tác 2 (Tab Gợi ý theo Người Dùng):*
    - Nhập `user_id = 1` $\rightarrow$ Nhấn **Khám Phá Danh Mục Gợi Ý** $\rightarrow$ Hiển thị Top 10 phim cá nhân hóa kèm điểm dự đoán và lý do gợi ý minh bạch.
    - Nhập `user_id = 9999` (User mới) $\rightarrow$ Hệ thống tự động kích hoạt cơ chế **Cold-Start** gợi ý các tác phẩm có điểm chất lượng cao nhất.

---

## 5. PHÚT THỨ 5: ĐỀ XUẤT TỐI ƯU HÓA DANH MỤC & KẾT LUẬN
- **Lời nói (Speaker):**
  > *"Từ kết quả phân tích trên và đối sánh với bộ dữ liệu danh mục thực tế của Netflix, nhóm đưa ra 3 khuyến nghị chiến lược có số liệu chứng minh:
  > 1. **Mở rộng danh mục Sci-Fi và Phim tài liệu:** Đây là 2 thể loại có tốc độ tăng trưởng QoQ cao nhất (>15%) nhưng hiện chỉ chiếm lần lượt 8.8% và 2.5% tổng kho phim.
  > 2. **Cá nhân hóa trang chủ theo giới tính và nhóm tuổi:** Tự động ưu tiên cụm Action/Sci-Fi cho tệp khán giả nam thanh niên, và ưu tiên phim Gia đình/Animation cho tệp khán giả trẻ em dưới 18 tuổi.
  > 3. **Chiến lược gói nội dung theo đạo diễn (Director Bundle):** Xây dựng các cụm phim liên kết theo đạo diễn hành động có độ nâng Lift > 1.8 để kéo dài thời gian xem trung bình.
  > Em xin chân thành cảm ơn quý Thầy Cô đã lắng nghe, nhóm sẵn sàng tiếp nhận các câu hỏi phản biện ạ!"*

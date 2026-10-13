#!/bin/bash
# ==============================================================================
# BÀI TẬP LỚN CUỐI KỲ: KHO DỮ LIỆU & KHAI PHÁ DỮ LIỆU (PTIT)
# Đề tài: Khai phá kho dữ liệu lịch sử xem phim để dự đoán thị hiếu người dùng
#         và tối ưu hóa danh mục nội dung (Streaming Platform)
# Script: scripts/run_all.sh
# Mục đích: Thực thi toàn bộ pipeline tự động từ ETL -> DW -> Data Mining -> RecSys -> Export & Reports
# ==============================================================================

set -e

# Đổi thư mục làm việc về gốc project
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "========================================================================"
echo ">>> KHỞI CHẠY PIPELINE BÀI TẬP LỚN KHO DỮ LIỆU & KHAI PHÁ DỮ LIỆU (PTIT)"
echo ">>> Thư mục gốc: $PROJECT_ROOT"
echo "========================================================================"

# 1. Kiểm tra môi trường ảo Python
PYTHON_BIN="$PROJECT_ROOT/venv/bin/python"
if [ ! -f "$PYTHON_BIN" ]; then
    echo "[!] Không tìm thấy venv tại $PROJECT_ROOT/venv. Đang dùng python hệ thống..."
    PYTHON_BIN="python3"
fi
echo "[+] Sử dụng Python: $($PYTHON_BIN --version) ($PYTHON_BIN)"

# 2. Kiểm tra file cấu hình .env
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "[!] Chưa có .env, đang sao chép từ .env.example..."
        cp .env.example .env
    else
        echo "[x] Lỗi: Không tìm thấy .env hoặc .env.example!"
        exit 1
    fi
fi

# 3. Giai đoạn 2: Chuẩn hóa, Khử trùng lặp và Fuzzy Matching (IMDb + Netflix + ML-1M)
echo ""
echo "========================================================================"
echo ">>> [BƯỚC 1/6] TIỀN XỬ LÝ DỮ LIỆU & LIÊN KẾT THỂ THỰC (Clean & Match)"
echo "========================================================================"
$PYTHON_BIN src/etl/clean_and_match.py

# 4. Giai đoạn 3: Nạp dữ liệu vào Kho dữ liệu SQL Server (MovieDW) & Kiểm định DQ
echo ""
echo "========================================================================"
echo ">>> [BƯỚC 2/6] NẠP DỮ LIỆU VÀO KHO DỮ LIỆU (ETL to MovieDW) & KIỂM ĐỊNH CL"
echo "========================================================================"
$PYTHON_BIN src/etl/load_dw.py

# 5. Giai đoạn 4: Phân tích OLAP (ROLLUP, CUBE, LAG() QoQ Growth) - Trả lời Q3
echo ""
echo "========================================================================"
echo ">>> [BƯỚC 3/6] TRUY VẤN OLAP ĐA CHIỀU & TÍNH TĂNG TRƯỞNG QoQ (Câu hỏi Q3)"
echo "========================================================================"
$PYTHON_BIN src/mining/run_olap.py

# 6. Giai đoạn 5: Phân cụm người dùng (K-Means, Silhouette, Chi-Square) - Trả lời Q1
echo ""
echo "========================================================================"
echo ">>> [BƯỚC 4/6] PHÂN CỤM NGƯỜI DÙNG K-MEANS & KIỂM ĐỊNH CHI-SQUARE (Câu hỏi Q1)"
echo "========================================================================"
$PYTHON_BIN src/mining/user_clustering.py

# 7. Giai đoạn 6: Hệ thống gợi ý (Item-based CF + Association Rules) - Trả lời Q2
echo ""
echo "========================================================================"
echo ">>> [BƯỚC 5/6] XÂY DỰNG MÔ HÌNH GỢI Ý & LUẬT KẾT HỢP FP-GROWTH (Câu hỏi Q2)"
echo "========================================================================"
$PYTHON_BIN src/recsys/collaborative_filtering.py
$PYTHON_BIN src/recsys/association_rules.py

# 8. Giai đoạn 9: Biên dịch báo cáo Word (report.docx) và Slide thuyết trình (presentation.pptx)
echo ""
echo "========================================================================"
echo ">>> [BƯỚC 6/6] TẠO BÁO CÁO WORD VÀ SLIDE THUYẾT TRÌNH TỰ ĐỘNG"
echo "========================================================================"
$PYTHON_BIN scripts/export_docx.py
$PYTHON_BIN scripts/generate_slides.py

echo ""
echo "========================================================================"
echo ">>> TOÀN BỘ PIPELINE ĐÃ HOÀN TẤT THÀNH CÔNG 100%!"
echo "========================================================================"
echo "1. Dữ liệu Warehouse: Đã nạp 1,000,209 dòng vào database MovieDW (SQL Server)"
echo "2. Biểu đồ trực quan: Lưu trữ tại thư mục 'docs/images/'"
echo "3. Báo cáo đồ án: 'docs/report.docx' và 'docs/report.md'"
echo "4. Slide báo cáo: 'slides/presentation.pptx' (14 slides chuẩn PTIT có speaker notes)"
echo "5. Khởi chạy Web App Demo Streamlit:"
echo "   $ $PROJECT_ROOT/venv/bin/streamlit run app/streamlit_app.py"
echo "========================================================================"

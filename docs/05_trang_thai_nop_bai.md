# Trạng thái kiểm tra trước khi nộp

Tài liệu này phân biệt rõ artefact đã sinh với giới hạn của từng thí nghiệm;
không thay thế output thực tế bằng số liệu giả định.

| Yêu cầu đề bài | Bằng chứng trong repository | Trạng thái |
|---|---|---|
| Lý thuyết sâu về instance segmentation, CNN, probability map, star-convex và NMS | `docs/01_ly_thuyet_stardist.md`, Chương 2--3 trong `report/report.tex` | Hoàn thành |
| Tham chiếu Fiji/ImageJ và plugin chuẩn hoá | `fiji/scripts/FijiStarDistRunner.java`, `fiji/run_log_dsb2018_reference.csv`, protocol/macro; slide 7 | Hoàn thành: chạy artifact StarDist ImageJ/Fiji 0.3.0 trên Java 8/TensorFlow 1.12 CPU |
| Cài đặt lại bằng Python | `src/xla_gr03/`, CLI, `scripts/run_dsb2018_benchmark.py` | Hoàn thành |
| So sánh StarDist với Otsu/Watershed | `results/dsb2018_benchmark/summary_metrics.csv`, figures, label TIFF | Hoàn thành trên 50 test images |
| Đánh giá định lượng | Python/baseline: `results/dsb2018_benchmark/` (50 test); Fiji/ImageJ: `results/fiji_reference/` (3 ca chọn trước) | Hoàn thành, có per-image CSV, mean ± SD, TIFF label và provenance |
| Ảnh minh hoạ không chọn lọc | `qualitative_low.png`, `qualitative_median.png`, `qualitative_high.png`; TIFF label tương ứng | Hoàn thành |
| Kiểm thử code | `tests/`, `pytest -q`, `ruff check src tests scripts`; Java runner được biên dịch và chạy ra TIFF thật | Hoàn thành: 23 tests passed; ruff và biên dịch Java runner đều pass |
| Báo cáo khoảng 30 trang | `report/report.tex`, `report/report.pdf`, bảng/ảnh/code listing/reference | Hoàn thành nội dung; chỉ còn điền thông tin thành viên thật |
| Slide khoảng 10 trang | `slides/stardist_presentation_submission_v6.pptx` (10 slide, chart editable, có panel Fiji thực tế) | Hoàn thành |

## Hai thao tác người nộp cần làm trước khi LMS submit

1. Điền **tên, MSSV và mã nhóm** trên bìa report/slide.
2. Mở PDF/PPTX cuối, kiểm tra tên/mã nhóm và submit link lên LMS theo yêu cầu
   lớp. Các kết quả Fiji/ImageJ đã có TIFF, panel, metric, runtime và run log.

Kết quả Fiji/ImageJ là 3 ca low/median/high được chọn trước từ test split; không
được coi là benchmark 50 ảnh hay dùng để xếp hạng trực tiếp với các dòng 50 ảnh.

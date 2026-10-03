# Trạng thái kiểm tra trước khi nộp

Tài liệu này phân biệt rõ artefact đã sinh và bước cần thao tác trên máy Fiji;
không thay thế output thực tế bằng số liệu giả định.

| Yêu cầu đề bài | Bằng chứng trong repository | Trạng thái |
|---|---|---|
| Lý thuyết sâu về instance segmentation, CNN, probability map, star-convex và NMS | `docs/01_ly_thuyet_stardist.md`, Chương 2--3 trong `report/report.tex` | Hoàn thành |
| Tham chiếu Fiji/ImageJ và plugin chuẩn hoá | `fiji/workflows/stardist_fiji_protocol.md`, macro, run-log template; slide 7 | Hoàn thành tài liệu; **chưa chạy plugin trên máy này** |
| Cài đặt lại bằng Python | `src/xla_gr03/`, CLI, `scripts/run_dsb2018_benchmark.py` | Hoàn thành |
| So sánh StarDist với Otsu/Watershed | `results/dsb2018_benchmark/summary_metrics.csv`, figures, label TIFF | Hoàn thành trên 50 test images |
| Đánh giá định lượng | AP tại IoU .50/.75/.90, PQ, Dice, MAE đếm, runtime; per-image CSV và validation sweep | Hoàn thành cho Python/baseline |
| Ảnh minh hoạ không chọn lọc | `qualitative_low.png`, `qualitative_median.png`, `qualitative_high.png`; TIFF label tương ứng | Hoàn thành |
| Kiểm thử code | `tests/`, `pytest -q` (23 passed), `ruff check src tests scripts` | Hoàn thành ở lần kiểm tra cuối |
| Báo cáo khoảng 30 trang | `report/report.tex`, bảng/ảnh/code listing/reference | Nguồn hoàn chỉnh; cần điền thành viên và xuất PDF |
| Slide khoảng 10 trang | `slides/stardist_presentation_submission_v4.pptx` (10 slide, chart editable) | Hoàn thành |

## Ba thao tác bắt buộc còn lại trước khi LMS submit

1. Điền **tên, MSSV và mã nhóm** trên bìa report/slide.
2. Cài/chạy Fiji, bật ba update site `CSBDeep`, `StarDist`, `TensorFlow`, rồi
   chạy StarDist trên đúng input DSB2018; lưu Label Image TIFF, ROI ZIP và điền
   `fiji/run_log_template.csv`. Đánh giá label TIFF bằng CLI trong protocol.
3. Mở `report/report.tex` bằng XeLaTeX/LaTeX editor để xuất PDF; kiểm tra số
   trang, bảng và caption trước khi nộp.

Các hàng pending là giới hạn môi trường, không phải kết quả được suy đoán.

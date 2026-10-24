# Trạng thái kiểm tra trước khi nộp

Cập nhật 24/10/2026. Danh mục file chính: `SUBMISSION.md`.

| Hạng mục | Bằng chứng | Trạng thái/giới hạn |
|---|---|---|
| Lý thuyết | `docs/01_ly_thuyet_stardist.md`, báo cáo | Đã nêu NMS overlap theo diện tích nhỏ hơn, khác IoU đánh giá |
| Python | `src/xla_gr03/`, CLI/scripts | Pretrained inference, geometry/metric tham chiếu tự viết; chưa train CNN |
| Benchmark | `results/dsb2018_benchmark/` | 50 test images, validation Watershed tách biệt, clip=False; CSV/figure chạy lại |
| Đối chiếu Fiji–Python | `results/cross_platform/` | Matching trực tiếp, IoU/Dice, ID-invariant pixel agreement, overlay lỗi; low chưa đạt tiêu chí mô tả |
| Validation ablation | `results/validation_ablation/` | 30 ảnh cố định × 10 cấu hình; mean/SD, FP/FN, count, MAE, hai biểu đồ và ví dụ ngưỡng |
| Tái lập dữ liệu/model | `dataset_manifest.csv`, `validation_images.csv`, provenance, freeze | 497 cặp TIFF; hash ảnh/mask/weight; xác nhận train/test không trùng hash ảnh |
| Runtime | CSV/provenance | Python/baseline đo tiền xử lý + inference + hậu xử lý sau warm-up; file I/O tách riêng; không xếp hạng với Fiji cold command |
| Java/Fiji chạy lại | `fiji/pom.xml`, `scripts/run_fiji_reference.py`, `results/fiji_rerun/` | Dựng Maven, chạy Java 8/TensorFlow JNI 1.12 trên macOS Intel; ba mảng label trùng hoàn toàn output lịch sử |
| Tests | `tests/`, CI hai jobs | 39 tests đạt khi chạy cả unit và integration; model thật và đối chiếu thư viện chuẩn; coverage gộp 88% |
| Báo cáo | `report/report.tex`, PDF, `report/generated/` | Bảng sinh từ CSV, thêm RQ2/RQ3 và giới hạn; font TeX Gyre Termes |
| Slide | `slides/stardist_presentation_completed.pptx` | 27 slide, số liệu cập nhật, bảng/chart editable; có render/finalizer; bản cũ ở archive |

## Giới hạn được công bố

- Độc lập giữa dữ liệu train của weight pretrained và 50 test ID chưa xác minh,
  dù train/test TIFF của repo không trùng hash. Không khẳng định tổng quát hoá độc lập.
- Java histogram percentiles/chặn âm khác NumPy linear percentiles; boundary và
  TensorFlow khác nhau. Hai triển khai không cho output đồng nhất ở mọi ca.
- Fiji ba ca là sample chọn theo score ở lần chạy cũ, được giữ cố định, không
  phải mẫu ngẫu nhiên và không thay benchmark 50 ảnh.
- Macro GUI vẫn là protocol tương tác. Đường batch đầy đủ là Maven/Java runner.
- Không có yêu cầu gốc/rubric kèm repo để xác nhận tiêu chí bắt buộc tự train.
- Canva cũ chưa đồng bộ; bộ nộp hiện tại dùng PPTX trong `SUBMISSION.md`.

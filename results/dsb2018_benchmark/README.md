# Benchmark DSB2018

Chạy `python scripts/run_dsb2018_benchmark.py` từ gốc repo sau khi cài
`requirements-model.txt` và package. Chọn `min_distance` cho Watershed trên
30 ảnh train seed 42; Otsu/Watershed/StarDist chạy cùng 50 test images.

Lần chạy cập nhật: CPU Intel macOS, Python 3.11.9, TensorFlow 2.15.1,
normalization Python CSBDeep affine 1/99.8, `clip=False`. StarDist giữ ngưỡng
model công bố. AP@0.50 hiện khoảng 0.846, PQ khoảng 0.782.

- `per_image_metrics.csv`: 450 dòng, 3 phương pháp × 50 ảnh × 3 ngưỡng.
- `summary_metrics.csv`: mean/SD metric và runtime cùng định nghĩa.
- `dataset_manifest.csv`: 497 cặp train/test, dtype, size, SHA256.
- `validation_images.csv`: 30 ID chọn tham số, độc lập test của repo.
- `provenance.json`, `environment-freeze.txt`: device, CPU, versions, weight hash.
- `selected_cases.csv`, `selected_labels/`, `figures/`: ba ca lịch sử giữ cố định
  để không đổi đối tượng đang có nhãn Fiji. Không gọi chúng là min/median/max
  của lần chạy mới.

Runtime đo tiền xử lý + inference + hậu xử lý sau warm-up, không tính đọc/ghi
file/tải model. Kết quả không đại diện GPU hoặc dữ liệu ngoài domain này.
Chưa xác minh test ID với tập train của chính weight pretrained.

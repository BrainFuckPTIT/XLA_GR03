# Lần chạy Fiji được tái tạo ngày 24/10/2026

Sinh bằng `python scripts/run_fiji_reference.py`, Maven 3.9.9, Temurin Java
8u504, CPU Intel macOS. Artifact StarDist_:0.3.0-scijava và JNI TensorFlow 1.12.
Script trích cả JNI và framework native từ JAR vào cùng thư mục để Java 8
nạp đủ thư viện trên macOS; không sửa mã plugin hoặc tạo label giả.

- `run_log.csv`: tham số, runtime cold command, input/label hash, Java runtime.
- `dependency_manifest.csv`: JAR chính xác và SHA256.
- TIFF: ba output thật của plugin.
- `reproduction_check.csv`: so nhãn mới với nhãn Fiji gốc. Cả ba mảng label
  trùng hoàn toàn từng pixel; F1/Dice/IoU ghép đều 1.
- `evaluation/`: đánh giá lại với ground truth.

Không thay runtime lịch sử bằng số mới trên phần cứng khác. Log console đầy
đủ chỉ giữ ở máy chạy (gitignore *.log trong thư mục này).

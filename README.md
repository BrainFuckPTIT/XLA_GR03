# XLA_GR03 — Instance Segmentation với StarDist

Bài tập lớn môn **Xử lý ảnh số**, nhóm 03, PTIT. Repo nghiên cứu StarDist 2D,
đánh giá model pretrained với Otsu và marker-controlled Watershed trên DSB2018,
và đối chiếu đầu ra Python với plugin Fiji/ImageJ trên ba ảnh cố định.

Nhóm tự viết các hàm hình học tham chiếu và metric instance. Inference dùng
CNN, weight và hậu xử lý chính thức của StarDist; bộ giải Hungarian dùng SciPy.
Repo không tuyên bố tự xây/huấn luyện lại toàn bộ mạng.

## Cài đặt

Dùng **Python 3.11** cho thí nghiệm TensorFlow/Keras 2 đã kiểm chứng.

```bash
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements-model.txt
python -m pip install -e ".[dev]"
```

`requirements-model.txt` cố định các thư viện tính toán/model chính. Freeze đầy
đủ của lần chạy tham chiếu, CPU, phiên bản và hash model có trong
`results/dsb2018_benchmark/`. Freeze là bản ghi môi trường macOS x86_64 đã chạy,
không phải cam kết mọi package phụ cài được trên mọi hệ điều hành.

Python 3.10–3.12 vẫn chạy package cơ sở với `pip install -e ".[dev]"`.
Dùng Python 3.11 khi cần model hoặc integration tests.

## Chạy trên dữ liệu đã có

Các cặp TIFF nằm ở `data/dsb2018/dsb2018/{train,test}/{images,masks}/`.
CLI nhận đường dẫn ảnh cụ thể, ví dụ:

```bash
xla-gr03 segment input.tif labels.tif --method otsu --min-size 20
xla-gr03 segment input.tif labels.tif --method watershed --min-distance 9
xla-gr03 segment input.tif labels.tif --method stardist --model 2D_versatile_fluo
xla-gr03 evaluate truth.tif labels.tif --thresholds 0.5 0.75 0.9 --output-json metrics.json
```

StarDist dùng percentile 1/99.8, affine không clipping theo Python CSBDeep.
`--clip` chỉ bật khi chủ đích chạy thí nghiệm cắt input về [0,1]; lựa chọn được
lưu trong metadata. Không giả định chuẩn hoá Java giống hệt NumPy.

## Tái tạo kết quả

Chạy theo thứ tự sau từ gốc repo, sau khi cài môi trường model:

```bash
python scripts/run_dsb2018_benchmark.py
python scripts/run_validation_ablation.py
python scripts/evaluate_fiji_reference.py
python scripts/compare_fiji_python.py
python scripts/build_fiji_workflow_evidence.py
python scripts/build_report_data.py
```

Benchmark chạy CPU, kiểm tra cặp ảnh/mask và trùng hash giữa train/test,
ghi 30 image ID validation, hash dữ liệu/weight và môi trường hiệu lực.
Runtime Python/baseline bao gồm tiền xử lý + phân đoạn + hậu xử lý sau warm-up,
không tính đọc/ghi file hoặc tải model.

Sweep chạy trên đúng 30 ảnh validation, giữ test ở threshold model công bố.
Ba ca Fiji giữ image ID lịch sử để so sánh theo cặp, không chọn lại khi thay
đổi pipeline. Bảng Fiji–Python hiện ghi rõ ca low chưa đạt tiêu chí mô tả
F1≥0.95 và Dice≥0.95; không kết luận hai triển khai giống hệt nhau.

Để tạo lại TIFF bằng plugin Java 8/Maven, xem
[hướng dẫn Fiji](fiji/scripts/README.md). Đánh giá TIFF đã commit không cần Java.

Script tổng quát `scripts/run_experiment.py` báo lỗi khi thiếu mask/prediction.
`--allow-missing-stardist` cho phép ghi dòng `missing_prediction` rõ ràng.
Runtime nhãn nhập sẵn lấy từ `--run-log`, nếu không có thì để trống.

## Kiểm thử

```bash
pytest -q
pytest -m integration -q
ruff check .
```

Unit tests kiểm tra CLI/I/O, split/merge, ghép cặp sát ngưỡng, dữ liệu thiếu,
chuẩn hoá và geometry. Integration tests chạy model thật, so metric với
`stardist.matching`, so normalization/EDT/ray với thư viện chính thức.
Lần đầu cần mạng để lấy weight; CI có job integration riêng trên Python 3.11.

## Tài liệu và bản nộp chính

- [Danh mục bản nộp](SUBMISSION.md).
- [Báo cáo PDF](report/report.pdf), [nguồn LaTeX](report/report.tex).
- [Slide LaTeX/PDF chính](slides/latex/main.pdf), [mã nguồn Beamer](slides/latex/main.tex),
  [hướng dẫn dựng slide](slides/README.md).
- [Lý thuyết](docs/01_ly_thuyet_stardist.md),
  [thiết kế thực nghiệm](docs/04_thiet_ke_thuc_nghiem.md),
  [trạng thái kiểm tra](docs/05_trang_thai_nop_bai.md),
  [hướng dẫn tái lập](docs/06_tai_lap.md).
- `results/dsb2018_benchmark/`: 50 ảnh test, per-image CSV, mean/SD, provenance.
- `results/validation_ablation/`: sweep probability/NMS trên 30 ảnh validation.
- `results/cross_platform/`: bảng đối chiếu trực tiếp và overlay sai khác.
- `results/fiji_labels/`, `results/fiji_reference/`: label/log lịch sử và metric.

Dữ liệu 497 cặp TIFF đã có trong repo. Không commit môi trường, weight model
hoặc output tạm. Nguồn DSB2018 và ghi chú phân phối có trong `data/MANIFEST.md`.
Weight pretrained có nguồn huấn luyện DSB2018; repo chưa xác minh độc lập
image ID huấn luyện của weight với 50 ảnh test, nên kết luận giới hạn ở đánh
giá pretrained trên split công bố. Ba ảnh Fiji không đại diện benchmark n=50.

## Nhóm thực hiện

- Nguyễn Hồng Quang — B23DCVT361.
- Nguyễn Trọng Nam Khánh — B23DCCE052.
- Vũ Dũng — B23DCVT110.

# XLA_GR03 — Instance Segmentation với StarDist

[![CI](https://github.com/BrainFuckPTIT/XLA_GR03/actions/workflows/ci.yml/badge.svg)](https://github.com/BrainFuckPTIT/XLA_GR03/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Fiji](https://img.shields.io/badge/Fiji%2FImageJ-reference-00AEEF)](https://imagej.net/plugins/stardist)

Bài tập lớn môn **Xử lý ảnh số**: nghiên cứu, cài đặt, thực nghiệm và đánh
giá thuật toán phân đoạn từng đối tượng bằng Deep Learning với **StarDist**.
Fiji/ImageJ được sử dụng làm nền tảng tham chiếu; Otsu và
marker-controlled Watershed là hai phương pháp đối chứng.

## Mục tiêu

- Trình bày cơ sở toán học của probability map, star-convex representation,
  CNN/U-Net và Non-Maximum Suppression.
- Chạy và kiểm chứng StarDist 2D trên Fiji/ImageJ.
- Cài đặt pipeline Python có thể tái lập.
- Tự cài đặt các thành phần cốt lõi: normalized EDT theo instance, khoảng
  cách theo tia, polygon decoding, polygon NMS và instance matching.
- So sánh StarDist, Otsu và Watershed bằng metric định lượng.

## Cấu trúc repository

```text
XLA_GR03/
├── .github/                 CI và mẫu issue/pull request
├── configs/                 Cấu hình thí nghiệm có thể version-control
├── data/                    Hướng dẫn dữ liệu; không commit dataset lớn
├── docs/                    Lý thuyết, tài liệu và phân công
├── fiji/                    Workflow, macro/script Fiji
├── models/                  Hướng dẫn model; không commit weight lớn
├── notebooks/               Notebook khám phá và demo
├── references/              Tài liệu tham khảo BibTeX
├── report/                  Báo cáo cuối kỳ
├── results/                 Bảng/biểu đồ kết quả được chọn lọc
├── scripts/                 Entry point chạy từ command line
├── slides/                  Presentation khoảng 10 slide
├── src/xla_gr03/            Mã nguồn Python chính
└── tests/                   Unit test
```

## Cài đặt nhanh

Khuyến nghị Python 3.10 hoặc 3.11 cho môi trường StarDist/TensorFlow trên
Windows.

```bash
python -m venv .venv
```

Kích hoạt môi trường:

```powershell
.venv\Scripts\Activate.ps1
```

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Để chạy model StarDist pretrained:

```bash
python -m pip install -e ".[dev,stardist]"
```

## Sử dụng

### Otsu

```bash
xla-gr03 segment data/raw/example.tif results/otsu_labels.tif \
  --method otsu --foreground bright --min-size 20
```

### Marker-controlled Watershed

```bash
xla-gr03 segment data/raw/example.tif results/watershed_labels.tif \
  --method watershed --foreground bright --min-size 20 --min-distance 7
```

### StarDist pretrained

```bash
xla-gr03 segment data/raw/example.tif results/stardist_labels.tif \
  --method stardist --model 2D_versatile_fluo --prob-thresh 0.5 \
  --nms-thresh 0.3
```

Với ảnh H&E RGB, dùng model `2D_versatile_he`.

### Đánh giá label image

```bash
xla-gr03 evaluate data/ground_truth/example.tif \
  results/stardist_labels.tif --thresholds 0.5 0.75 0.9
```

### Đánh giá output StarDist Fiji/ImageJ

Ba label TIFF thực tế của plugin trên các ca DSB2018 low/median/high đã có ở
`results/fiji_labels/`. Tái tạo bảng metric và panel bằng:

```powershell
.venv\Scripts\python.exe scripts\evaluate_fiji_reference.py
```

Xem `fiji/scripts/run_stardist_headless.ps1` để chạy lại runner Java không GUI;
`fiji/run_log_dsb2018_reference.csv` ghi chính xác artifact plugin, model,
normalization, threshold, TensorFlow/Java runtime và thời gian từng ca.

## Kiểm thử

```bash
pytest
ruff check .
```

## Quy ước dữ liệu

- Ảnh đầu vào giữ nguyên bit depth khi lưu trong `data/raw/`.
- Ground truth và prediction là ảnh nhãn integer.
- Nền mang nhãn `0`; mỗi đối tượng mang một số nguyên dương duy nhất.
- Tên cặp ảnh/nhãn nên giống nhau, ví dụ `image_001.tif`.
- Không commit dataset, model weight, môi trường ảo hoặc toàn bộ output thô.
  Xem [hướng dẫn dữ liệu](data/README.md).

## Tài liệu

- [Cơ sở lý thuyết StarDist](docs/01_ly_thuyet_stardist.md)
- [Tổng hợp tài liệu](docs/02_tong_hop_tai_lieu.md)
- [Phạm vi thành viên 2](docs/ke_hoach_thanh_vien_2.md)
- [Thiết kế thí nghiệm và metric](docs/04_thiet_ke_thuc_nghiem.md)
- [Trạng thái kiểm tra trước khi nộp](docs/05_trang_thai_nop_bai.md)
- [Protocol Fiji/ImageJ](fiji/workflows/stardist_fiji_protocol.md)
- [Báo cáo LaTeX](report/report.tex)
- [Slide PowerPoint 10 trang](slides/stardist_presentation_submission_v6.pptx)

## Artefact nộp bài

- `report/report.pdf` và `report/report.tex`: báo cáo hoàn chỉnh gồm lý thuyết,
  Python, Fiji/ImageJ, protocol, code, metric, benchmark và ảnh kết quả thật.
- `scripts/run_dsb2018_benchmark.py`: benchmark 50 test images DSB2018, có
  validation tách biệt để chọn tham số Watershed.
- `results/dsb2018_benchmark/`: CSV từng ảnh, bảng mean ± SD, validation sweep
  và biểu đồ benchmark.
- `results/fiji_labels/` và `results/fiji_reference/`: TIFF label thật, metric,
  provenance và panel low/median/high từ plugin StarDist Fiji/ImageJ.
- `slides/stardist_presentation_submission_v6.pptx`: deck 10 slide có thể
  chỉnh sửa, gồm benchmark 50 ảnh và evidence Fiji/ImageJ n=3 tách biệt.
- `fiji/run_log_dsb2018_reference.csv`: log tham số/runtimes của lần chạy plugin.
- `results/tables/final_metrics_template.csv`: bảng metric tổng hợp, nêu rõ
  stratum Fiji n=3 không so sánh trực tiếp với n=50.
- [Quy trình đóng góp](CONTRIBUTING.md)

## Nhóm thực hiện

Nhóm 03 — Học viện Công nghệ Bưu chính Viễn thông (PTIT).

Thông tin thành viên sẽ được cập nhật trong báo cáo cuối kỳ.

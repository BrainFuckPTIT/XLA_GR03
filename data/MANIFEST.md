# Dataset manifest

| ID | Nội dung | Nguồn | Giấy phép/ghi chú | Vai trò |
|---|---|---|---|---|
| `dsb2018_stardist_sample` | Ảnh huỳnh quang 2D và instance labels | StarDist package, `test_image_nuclei_2d`; nguồn gốc Data Science Bowl 2018 | Dữ liệu mẫu do StarDist phân phối. Xem StarDist repository và Caicedo et al., 2019 | Demo tái lập một ảnh |
| `dsb2018` | 497 cặp image/instance-mask, gồm 447 train và 50 test | `https://github.com/stardist/stardist/releases/download/0.1.0/dsb2018.zip` | Subset DSB2018 do StarDist phát hành | Benchmark: 30 train validation images, 50 test images |

Ảnh và label được `scripts/run_real_demo.py` materialize vào `data/raw/` và
`data/ground_truth/`, hai thư mục bị Git bỏ qua. Demo gồm đúng một ảnh nên
không phải test set độc lập và không dùng để khẳng định hiệu năng tổng quát.

Script `scripts/run_dsb2018_benchmark.py` tải archive khi chưa có, lưu dữ liệu
vào `data/dsb2018/` (bị Git bỏ qua) và lưu toàn bộ CSV/biểu đồ tổng hợp được
kiểm soát phiên bản ở `results/dsb2018_benchmark/`.

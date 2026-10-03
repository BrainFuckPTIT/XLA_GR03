# Dataset manifest

| ID | Nội dung | Nguồn | Giấy phép/ghi chú | Vai trò |
|---|---|---|---|---|
| `dsb2018_stardist_sample` | Ảnh huỳnh quang 2D và instance labels | StarDist package, `test_image_nuclei_2d`; nguồn gốc Data Science Bowl 2018 | Dữ liệu mẫu do StarDist phân phối. Xem StarDist repository và Caicedo et al., 2019 | Demo tái lập một ảnh |

Ảnh và label được `scripts/run_real_demo.py` materialize vào `data/raw/` và
`data/ground_truth/`, hai thư mục bị Git bỏ qua. Demo gồm đúng một ảnh nên
không phải test set độc lập và không dùng để khẳng định hiệu năng tổng quát.

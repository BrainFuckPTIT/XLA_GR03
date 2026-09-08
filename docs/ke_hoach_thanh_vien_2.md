# Kế hoạch và sản phẩm bàn giao — Thành viên 2

## Nhiệm vụ

1. Xây dựng package Python có thể cài đặt và chạy bằng CLI.
2. Cài đặt Otsu + connected components và marker-controlled Watershed.
3. Tích hợp inference từ model StarDist 2D chính thức.
4. Tự cài đặt reference implementation cho các thành phần cốt lõi StarDist.
5. Cài đặt matching một-một và metric định lượng.
6. Viết unit test, lint và CI.
7. Tối ưu sau khi đã có dataset và profiling thực tế.

## Phạm vi “tự cài đặt”

Mã trong `src/xla_gr03/geometry.py` tự thực hiện:

- normalized Euclidean distance transform theo từng instance;
- sinh khoảng cách đến biên theo các tia cách đều;
- giải mã vector khoảng cách thành polygon;
- đo overlap polygon;
- greedy polygon NMS.

Mã trong `src/xla_gr03/metrics.py` tự thực hiện:

- ma trận IoU giữa các instance;
- Hungarian matching một-một;
- TP, FP, FN, Precision, Recall, F1, accuracy/AP theo StarDist;
- mean matched IoU, PQ, foreground Dice/IoU và sai số đếm.

CNN/U-Net và model weight pretrained được chạy qua thư viện StarDist chính
thức. Báo cáo phải phân biệt rõ phần nhóm tự viết với phần tái sử dụng thư
viện.

## Sản phẩm hiện có

- `src/xla_gr03/`: package Python.
- `tests/`: unit test cho hình học, metric, preprocessing và baseline.
- `pyproject.toml`: dependency, CLI và cấu hình công cụ.
- `configs/default.yaml`: cấu hình thí nghiệm mặc định.
- `.github/workflows/ci.yml`: kiểm tra tự động.

## Công việc tiếp theo khi có dataset

1. Chạy smoke test trên 3–5 ảnh thực.
2. Kiểm tra chiều/kênh/bit depth và quy tắc foreground.
3. Profile ray-distance/NMS reference; chỉ tối ưu nút thắt đã đo được.
4. Chọn probability/NMS threshold trên validation set.
5. So sánh output Python với label image/ROI từ Fiji.
6. Lưu bảng kết quả gọn trong `results/tables/` và biểu đồ trong
   `results/figures/`.

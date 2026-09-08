# Dữ liệu

```text
data/
├── raw/             ảnh đầu vào nguyên bản
├── ground_truth/    label image instance do người gán nhãn
└── processed/       ảnh trung gian đã chuẩn hóa/chuyển đổi
```

Ba thư mục dữ liệu được giữ cục bộ và bị `.gitignore` loại khỏi Git. Không
đưa dữ liệu có điều kiện cấp phép không rõ ràng vào repository công khai.

## Quy ước

- Ảnh và ground truth dùng cùng stem, ví dụ `image_001.tif`.
- Label image là integer 2D: `0` là nền, `1..N` là instance.
- Không lưu ground truth bằng JPEG.
- Ghi nguồn, giấy phép, ngày tải và checksum trong `data/MANIFEST.csv` khi
  dataset được chốt.
- Split train/validation/test phải được lưu bằng danh sách tên file, không
  chọn ngẫu nhiên lại ở mỗi lần chạy.

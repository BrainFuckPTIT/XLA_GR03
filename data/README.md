# Dữ liệu

## Cấu trúc bắt buộc

`raw/` và `ground_truth/` chứa các TIFF có **cùng basename**. Ground truth là
label image integer 2D: nền `0`, mỗi instance là một ID dương. Ví dụ:

```text
data/raw/image_001.tif
data/ground_truth/image_001.tif
```

Không dùng mask RGB để làm ground truth. Nếu nguồn cung cấp mỗi mask instance
riêng, chuyển chúng thành một label TIFF rồi kiểm tra `max(label)` và overlay.
Không commit dữ liệu bị hạn chế bản quyền; ghi URL, license, số ảnh và checksum
trong manifest riêng khi nộp nội bộ.

```text
data/
├── raw/             ảnh đầu vào nguyên bản
├── ground_truth/    label image instance do người gán nhãn
└── processed/       ảnh trung gian đã chuẩn hóa/chuyển đổi
```

Ba thư mục dự án riêng (`raw/`, `ground_truth/`, `processed/`) được giữ cục bộ
và bị `.gitignore` loại khỏi Git. Ngoại lệ có chủ đích là
`data/dsb2018/dsb2018/`: 497 cặp TIFF benchmark do StarDist phân phối được
versioned để tái lập kết quả. Không đưa dữ liệu có điều kiện cấp phép không rõ
ràng vào repository công khai.

## Quy ước

- Ảnh và ground truth dùng cùng stem, ví dụ `image_001.tif`.
- Label image là integer 2D: `0` là nền, `1..N` là instance.
- Không lưu ground truth bằng JPEG.
- Ghi nguồn, giấy phép, ngày tải và checksum trong `data/MANIFEST.csv` khi
  dataset được chốt.
- Split train/validation/test phải được lưu bằng danh sách tên file, không
  chọn ngẫu nhiên lại ở mỗi lần chạy.

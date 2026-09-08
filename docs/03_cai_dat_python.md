# Cài đặt Python cho StarDist, Otsu và Watershed

## Kiến trúc mã nguồn

| Module | Trách nhiệm |
|---|---|
| `preprocessing.py` | Chuyển grayscale và percentile normalization |
| `baselines.py` | Otsu + connected components và Watershed |
| `geometry.py` | EDT, ray distances, polygon decoding và NMS tự cài đặt |
| `stardist_pipeline.py` | Wrapper inference StarDist chính thức |
| `metrics.py` | Matching instance và metric định lượng |
| `io.py` | Đọc ảnh, lưu label TIFF không mất ID |
| `cli.py` | Giao diện dòng lệnh thống nhất |

## Hai tầng cài đặt StarDist

### Tầng kiểm chứng ứng dụng

`segment_stardist` gọi `StarDist2D.predict_instances` của thư viện chính thức.
Tầng này dùng để:

- chạy model pretrained;
- so sánh với Fiji khi dùng cùng model/tham số;
- tạo kết quả thực nghiệm thực tế với tốc độ tối ưu.

### Tầng giải thích thuật toán

`geometry.py` là reference implementation dễ đọc. Nó chứng minh nhóm hiểu và
có thể cài đặt lại các phép biến đổi cốt lõi. Hàm dò tia dùng vòng lặp Python
nên không được dùng để train trên dataset lớn; StarDist chính thức dùng phần
mở rộng C/C++/OpenCL hiệu quả hơn.

## Luồng baseline

### Otsu

```text
ảnh -> grayscale -> Gaussian -> Otsu -> morphology -> fill holes
    -> connected components -> instance labels
```

### Watershed

```text
ảnh -> Otsu foreground -> Euclidean distance transform
    -> local maxima markers -> watershed(-distance) -> instance labels
```

## Định dạng output

Mọi phương pháp trả về `SegmentationResult` gồm:

- `labels`: mảng integer 2D, nền bằng 0;
- `method`: tên phương pháp;
- `metadata`: threshold và tham số cần để tái lập;
- `object_count`: số nhãn dương duy nhất.

Label được lưu dạng TIFF `uint16`; nếu có trên 65.535 đối tượng, mã tự chuyển
sang `uint32`.

## Kiểm thử

Unit test không cần tải model StarDist và không cần GPU. Điều này giúp CI nhẹ,
nhanh và ổn định. Inference StarDist sẽ được smoke-test riêng khi dataset và
môi trường TensorFlow đã được chốt.

## Giới hạn hiện tại

- Chỉ hỗ trợ ảnh 2D/YXC, phù hợp phạm vi Fiji StarDist 2D.
- Chưa có train/fine-tune CNN; hiện dùng model pretrained.
- Chưa có benchmark runtime trên dataset thật.
- Reference polygon overlap được rasterize nên là xấp xỉ theo pixel.
- Cấu hình YAML là hồ sơ tham số; CLI chưa tự đọc YAML ở phiên bản đầu.

# Protocol Fiji/ImageJ: StarDist 2D và kiểm chứng Python

## Mục đích và phạm vi

Quy trình này tạo **instance label image** bằng plugin StarDist 2D của Fiji,
sau đó dùng đúng file đó để đánh giá bằng Python. Không đánh giá screenshot,
binary mask, hoặc ROI đã raster hoá ở kích thước khác. Mỗi pixel nền có nhãn
`0`; mỗi object có một ID dương riêng.

## Cài plugin

1. Cài Fiji bản ổn định từ [fiji.sc](https://fiji.sc/), ghi lại phiên bản tại
   `Help > About Fiji`.
2. Chọn `Help > Update... > Manage update sites`, bật **CSBDeep**,
   **StarDist** và **TensorFlow**, rồi `Apply changes` và khởi động lại Fiji.
   Đây là ba update site mà trang plugin StarDist của ImageJ hướng dẫn cho
   inference 2D.
3. Mở `Help > About Plugins` hoặc hộp thoại StarDist, chụp lại phiên bản plugin
   và lưu vào `fiji/run_log_template.csv`.
4. Mở một ảnh TIFF 2D. Kiểm tra kích thước, bit depth và kênh bằng
   `Image > Show Info...`; không resize hoặc đổi scale ở một phía mà không làm
   tương tự ở phía còn lại.

## Chạy một ảnh

1. Mở ảnh ở `data/raw/<name>.tif`.
2. Chọn `Plugins > StarDist > StarDist 2D`.
3. Chọn model phù hợp. `Versatile (fluorescent nuclei)` phù hợp ảnh huỳnh quang
   nhân sáng; `Versatile (H&E nuclei)` phù hợp ảnh mô bệnh học RGB. Ghi đúng tên
   model hiển thị trong plugin, không chỉ ghi “StarDist”.
4. Chọn percentile normalization, probability/score threshold, overlap/NMS
   threshold và số tile. Bắt buộc ghi toàn bộ giá trị thực tế.
5. Chọn output **Label Image** và **ROI Manager** nếu plugin cung cấp cả hai.
6. Lưu label TIFF không nén vào `results/fiji_labels/<name>.tif`; lưu ROI ZIP
   cùng basename nếu cần minh hoạ. Không dùng `Save As PNG`, vì PNG có thể làm
   mất ID instance.
7. Đo thời gian từ lúc nhấn OK đến khi label image xuất hiện, sau khi model đã
   được tải xong. Ghi `runtime_s` và loại CPU/GPU.

## Ghi macro tái lập

Sau khi thao tác một ảnh thành công, mở `Plugins > Macros > Record...`, chạy
lại StarDist và copy đúng dòng `run("StarDist 2D", "...")` của **phiên bản
plugin đang dùng** vào `fiji/macros/stardist_batch.ijm`. Chạy macro trên 2 ảnh
trước, so sánh basename và kích thước label với input rồi mới chạy batch. Cách
này an toàn hơn việc đoán tên option macro vốn thay đổi theo plugin.

## Kiểm chứng định lượng với Python

Ví dụ, sau khi Fiji xuất `results/fiji_labels/image_001.tif`:

```powershell
python -m xla_gr03 evaluate data/ground_truth/image_001.tif `
  results/fiji_labels/image_001.tif --thresholds 0.5 0.75 0.9 `
  --output-json results/fiji_metrics/image_001.json
```

Chỉ so sánh Fiji và Python nếu ảnh đầu vào, model, `pmin`, `pmax`, probability
threshold, NMS threshold, scale và quy tắc tile giống nhau. Khác biệt số nhãn
phải được kiểm tra bằng overlay và log tham số trước khi kết luận.

## Lần chạy tham chiếu đã lưu trong repository

Ba output thực tế đã được tạo bằng artifact công khai
`de.csbdresden:StarDist_:0.3.0-scijava` (command
`de.csbdresden.stardist.StarDist2D`) trong ImageJ 2.9.0 headless + ImageJ 1.53t
legacy, Eclipse Temurin 8.0.504 và TensorFlow 1.12 CPU. Java 8 được dùng vì
loader TensorFlow ImageJ 1.12 không tương thích các runtime Java mới hơn.

- Các ảnh `low`, `median`, `high` đã chọn trước theo
  `results/dsb2018_benchmark/selected_cases.csv`.
- Label TIFF thật: `results/fiji_labels/`.
- Log model, ngưỡng, tile, runtime và runtime platform:
  `fiji/run_log_dsb2018_reference.csv`.
- Python đánh giá trực tiếp các TIFF: chạy
  `python scripts/evaluate_fiji_reference.py`; kết quả là
  `results/fiji_reference/per_image_metrics.csv`, `summary_metrics.csv` và
  `fiji_reference_panels.png`.

Đây là kiểm chứng cross-platform trên 3 ảnh, không phải ước lượng benchmark 50
ảnh. Không gộp các dòng này với summary Python/baseline 50 ảnh.

## Checklist trước khi đưa vào báo cáo

- [x] Dataset, split, số ảnh và nguồn/giấy phép được nêu rõ.
- [x] Fiji/ImageJ plugin artifact, model, runtime Java/TensorFlow và ngày chạy được ghi lại.
- [x] Label image 2D có kích thước đúng bằng ground truth.
- [x] Bảng có AP/accuracy theo IoU, PQ, Dice foreground, sai số đếm, runtime.
- [x] Ảnh minh hoạ có overlay GT/prediction cho low/median/high.

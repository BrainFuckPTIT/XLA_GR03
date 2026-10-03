# Thiết kế thực nghiệm và đánh giá

## Câu hỏi nghiên cứu

**RQ1.** StarDist có tách các nhân chạm nhau tốt hơn Otsu và Watershed không?

**RQ2.** Kết quả StarDist trong Fiji và Python có tương thích khi giữ nguyên
ảnh, model, chuẩn hoá và hai ngưỡng hậu xử lý không?

**RQ3.** Probability threshold và NMS threshold tác động thế nào tới lỗi tách,
gộp, đếm và thời gian?

## Dataset và split

Chọn một dataset có instance mask hợp pháp, ví dụ Data Science Bowl 2018 cho
ảnh huỳnh quang hoặc MoNuSeg cho H&E. Lưu bảng manifest có `image_id`, nguồn,
license, kích thước, kênh và split. Chốt split **trước** khi thử tham số:

| Split | Vai trò | Quy tắc |
|---|---|---|
| Development | kiểm tra input/output và debug | không đưa vào bảng kết luận |
| Validation | chọn `prob_thresh`, `nms_thresh`, `min_distance` | cố định sau khi chọn |
| Test | so sánh cuối cùng | không đổi tham số theo từng ảnh |

Không trộn ảnh cùng slide/subject sang nhiều split nếu dataset có metadata đó.
Nếu dataset nhỏ, dùng 5-fold cross-validation và báo cáo mean ± SD theo fold.

## Điều kiện chạy công bằng

| Hạng mục | Otsu | Watershed | StarDist Fiji | StarDist Python |
|---|---|---|---|---|
| Input | cùng TIFF gốc | cùng TIFF gốc | cùng TIFF gốc | cùng TIFF gốc |
| Tiền xử lý | Gaussian, Otsu | Gaussian, Otsu | percentile theo plugin | percentile giống Fiji |
| Output | CC labels | watershed labels | label TIFF | label TIFF |
| Chọn tham số | validation | validation | validation | dùng đúng tham số Fiji |
| Metric | cùng GT + script | cùng GT + script | cùng GT + script | cùng GT + script |

Otsu và Watershed không cần bị ép dùng percentile normalization của StarDist,
nhưng mọi bước phải ghi đầy đủ để có thể lặp lại. Không điều chỉnh ngưỡng theo
từng ảnh test.

## Metric và cách tính

Với IoU ma trận $J_{ij}=|G_i\cap P_j|/|G_i\cup P_j|$, ghép cặp một-một bằng
Hungarian assignment. Một pair là TP khi $J_{ij}\ge\tau$; instance chưa ghép
là FN/FP. Báo cáo tại $\tau\in\{0.50,0.75,0.90\}$:

$$P=TP/(TP+FP),\quad R=TP/(TP+FN),\quad F1=2TP/(2TP+FP+FN).$$

Theo định nghĩa dùng trong StarDist, `accuracy` (cũng thường được gọi
$AP_\tau$ trong bài báo) là $TP/(TP+FP+FN)$. Panoptic Quality:

$$PQ=\frac{\sum_{(i,j)\in TP}J_{ij}}{TP+0.5FP+0.5FN}.$$

Thêm Dice/IoU foreground để thấy phủ vùng, nhưng không dùng thay metric
instance. Báo cáo MAE đếm là $|N_{pred}-N_{gt}|$ và thời gian giây/ảnh. Với
nhiều ảnh, xuất mean, SD, median và số ảnh; không chỉ xuất kết quả ảnh đẹp.

## Lệnh tái lập

```powershell
# Cài môi trường một lần
conda env create -f environment.yml
conda activate xla-gr03

# Sinh label baseline, metric cùng IoU 0.50 và lưu CSV
python scripts/run_experiment.py --images data/raw --ground-truth data/ground_truth `
  --stardist-labels results/fiji_labels --output results/experiment --iou 0.5

# Phân tích từng output StarDist ở ba ngưỡng IoU
python -m xla_gr03 evaluate data/ground_truth/image_001.tif `
  results/fiji_labels/image_001.tif --thresholds 0.5 0.75 0.9
```

## Bảng và biểu đồ bắt buộc

1. **Bảng chính:** method, AP@0.50, AP@0.75, AP@0.90, PQ, Dice, MAE đếm,
   runtime. Điền số test mean ± SD.
2. **Bảng Fiji–Python:** cùng model/tham số, so object count, AP@0.50 và
   pixel agreement. Nêu mọi khác biệt về phiên bản.
3. **Ablation:** quét tối thiểu 5 probability threshold với NMS cố định; quét
   NMS threshold với probability cố định. Vẽ metric và object count.
4. **Minh hoạ:** raw, ground truth, Otsu, Watershed, StarDist, overlay lỗi.

`results/tables/final_metrics_template.csv` là schema để nộp. Số liệu điền
vào file đó phải xuất phát từ CSV script, không gõ tay từ ảnh chụp.

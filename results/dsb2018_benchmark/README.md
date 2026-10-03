# Benchmark DSB2018 chính thức

Tạo lại toàn bộ kết quả bằng:

```powershell
.venv\Scripts\python.exe scripts/run_dsb2018_benchmark.py
```

Script tải archive `dsb2018.zip` do nhóm StarDist công bố. Nó chọn
`min_distance` cho Watershed trên 30 ảnh train lấy mẫu với seed 42, rồi đánh giá
Otsu, Watershed và `2D_versatile_fluo` trên 50 ảnh test tách biệt. StarDist sử
dụng default probability/NMS thresholds của model, không điều chỉnh trên test.

- `per_image_metrics.csv`: kết quả từng ảnh tại IoU 0.50, 0.75, 0.90.
- `summary_metrics.csv`: mean và SD trên 50 test images.
- `watershed_validation_sweep.csv`: bằng chứng chọn tham số trên train.
- `figures/benchmark_ap_pq.png`: biểu đồ AP/PQ @ IoU 0.50.
- `figures/qualitative_{low,median,high}.png`: ảnh input, ground truth và ba
  output tại case có AP StarDist thấp, trung vị và cao trong toàn bộ test set.
- `selected_labels/`: label TIFF của ba case minh hoạ; `selected_cases.csv`
  ghi rule chọn case và image ID.

Runtime đo trên CPU sau warm-up model. Kết quả chỉ đánh giá model pretrained
trên DSB2018, không đại diện tự động cho H\&E hoặc dữ liệu phòng thí nghiệm khác.

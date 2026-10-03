# Kết quả chạy thật: StarDist DSB2018 sample

Lệnh tạo toàn bộ artefact:

```powershell
.venv\Scripts\python.exe scripts/run_real_demo.py
```

Kết quả dùng ảnh huỳnh quang và instance mask mẫu mà package StarDist phân
phối, có nguồn gốc từ Data Science Bowl 2018. `metrics_per_threshold.csv` là
metric theo ba ngưỡng IoU; `stardist_threshold_sweep.csv` ghi ablation. Cấu
hình StarDist là `2D_versatile_fluo`, percentile 1/99.8, probability 0.5,
NMS 0.3, CPU. Runtime không tính lần tải model/warm-up đầu tiên.

Đây là **demo một ảnh**. Các số cho thấy pipeline chạy thật và phù hợp để minh
hoạ, nhưng không thay thế benchmark trên test split nhiều ảnh. Không gán nhãn
"Fiji" cho bất kỳ số liệu nào trong thư mục này.

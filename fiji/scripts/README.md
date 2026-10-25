# Fiji/ImageJ chạy từ clone sạch

Cần Java 8 JDK (`JAVA_HOME`) và Maven 3.9+ (`mvn` trên PATH). Chạy từ gốc repo:

```bash
python scripts/run_fiji_reference.py
```

Script biên dịch `FijiStarDistRunner.java`, lấy classpath từ `fiji/pom.xml`,
chạy artifact `de.csbdresden:StarDist_:0.3.0-scijava` trên ba image ID cố định
và lưu TIFF, raw log, runtime, hash ảnh/nhãn và manifest JAR vào
`results/fiji_rerun/`. Output đã tồn tại sẽ báo lỗi; chọn `--output` khác hoặc
chỉ dùng `--overwrite` khi muốn ghi đè output đó.

Log/nhãn gốc ở `fiji/run_log_dsb2018_reference.csv` và `results/fiji_labels/`
vẫn là bằng chứng lịch sử. File PowerShell cũ tiếp tục hỗ trợ môi trường jgo
đã dựng sẵn, nhưng không cần cho đường Maven mới.

Tham số runner: versatile fluorescent nuclei, percentile 1/99.8, probability
0.479071, NMS 0.3, một tile, boundary exclusion 2 px, Label Image TIFF.
Java CSBDeep 0.6.0 dùng histogram percentile, không cắt ngưỡng trên nhưng chặn
âm về 0. Python dùng percentile tuyến tính NumPy, affine không clipping.
Không mô tả hai cách chuẩn hoá là giống hệt nhau.

Đo output mới:

```bash
python scripts/evaluate_fiji_reference.py --labels results/fiji_rerun --run-log results/fiji_rerun/run_log.csv --output results/fiji_rerun/evaluation
```

Macro GUI là protocol tương tác và vẫn cần operator xác nhận option từ Recorder,
không được gọi là batch tự động hoàn chỉnh. Runner Maven là đường batch có thể chạy.

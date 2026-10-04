# Fiji/ImageJ scripts

`FijiStarDistRunner.java` gọi trực tiếp command `de.csbdresden.stardist.StarDist2D`
trong artifact công khai `de.csbdresden:StarDist_:0.3.0-scijava`. Nó cố định model
**Versatile (fluorescent nuclei)**, percentile normalization `1/99.8`, probability
threshold `0.479071`, NMS overlap `0.3`, boundary exclusion `2`, và xuất **Label
Image** TIFF. Các giá trị này là threshold tối ưu đóng gói kèm model, không chọn
trên test split.

`run_stardist_headless.ps1` biên dịch runner rồi chạy không GUI. Cần Java 8 vì
plugin này dùng ImageJ TensorFlow 1.12. Ví dụ (đường dẫn Maven environment thay
đổi theo máy):

```powershell
.\fiji\scripts\run_stardist_headless.ps1 `
  -InputImage data\dsb2018\dsb2018\test\images\example.tif `
  -OutputLabel results\fiji_labels\example.tif `
  -PluginEnvironment C:\path\to\.jgo\envs\de\csbdresden\StarDist_\<hash> `
  -Java8Home "C:\Program Files\Eclipse Adoptium\jdk-8..." `
  -Tiles 1
```

Không ghi đè label đã có; dùng một output filename mới khi chạy lại. Sau khi chạy,
đo label bằng `scripts/evaluate_fiji_reference.py`. Lần chạy thực tế trên ba ca
DSB2018 được ghi đầy đủ tại `../run_log_dsb2018_reference.csv` và output TIFF ở
`results/fiji_labels/`.

Macro GUI vẫn được lưu ở `../macros/stardist_batch.ijm`; xem protocol tại
`../workflows/stardist_fiji_protocol.md`.

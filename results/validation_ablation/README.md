# Probability/NMS ablation trên validation

`python scripts/run_validation_ablation.py` dùng đúng 30 ID trong
`../dsb2018_benchmark/validation_images.csv`, hoàn toàn từ split train.

Có 300 dòng per-image (30 × 10 cấu hình), bảng mean/SD AP, F1, PQ, count,
MAE, FP/FN và hai biểu đồ có SD. Khi quét probability, NMS cố định 0.3.
Khi quét NMS, probability cố định 0.479071. CNN maps được tính một lần/ảnh;
không báo runtime inference cho sweep hậu xử lý. Test vẫn giữ model defaults.

`threshold_examples.png` minh hoạ ảnh validation ID đầu tiên trong danh sách
cố định với hai đầu mút của mỗi sweep, kèm FP/FN. Không chọn ảnh theo score.
Giảm probability thường giữ thêm candidate; số liệu cụ thể và độ dao động
phải đọc từ CSV, không suy rộng thành quy luật cho mọi ảnh.

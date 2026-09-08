# Kế hoạch và sản phẩm bàn giao — Thành viên 1

## 1. Nhiệm vụ

1. Nghiên cứu nền tảng của phân đoạn ảnh và phân đoạn từng đối tượng.
2. Nghiên cứu CNN/U-Net làm backbone của StarDist.
3. Phân tích đầy đủ chuỗi xử lý StarDist: sinh nhãn huấn luyện, dự đoán hai
   đầu ra, giải mã đa giác và Non-Maximum Suppression.
4. Xây dựng mô hình toán học và ký hiệu dùng thống nhất cho cả nhóm.
5. Nghiên cứu cơ sở của Otsu và marker-controlled Watershed để làm baseline.
6. Tổng hợp tài liệu gốc, tài liệu chính thức và các điểm cần kiểm chứng bằng
   thực nghiệm.

## 2. Sản phẩm bàn giao

- Chương lý thuyết tại `docs/01_ly_thuyet_stardist.md`.
- Danh mục BibTeX tại `references/references.bib`.
- Các giả thuyết nghiên cứu và câu hỏi thực nghiệm để thành viên 4 sử dụng.
- Đặc tả đầu vào/đầu ra và pseudocode để thành viên 2 cài đặt.
- Danh sách tham số StarDist cần thành viên 3 khảo sát trên Fiji.

## 3. Điểm cần các thành viên khác tiếp nhận

### Thành viên 2 — Python

- Dùng ảnh nhãn instance, không dùng mask nhị phân làm ground truth StarDist.
- Cài đặt hoặc minh hoạ rõ các bước: EDT chuẩn hoá theo từng instance, khoảng
  cách theo tia, polygon decoding và greedy NMS.
- Xuất ảnh nhãn integer có cùng kích thước với ground truth.
- Không gọi `accuracy` của phân loại pixel để thay cho metric instance.

### Thành viên 3 — Fiji

- Ghi lại model, probability threshold, overlap threshold, normalization,
  số tile và phiên bản Fiji/plugin trong mọi lần chạy.
- Xuất đồng thời label image và ROI khi có thể.
- Kiểm chứng cùng ảnh và cùng tham số tiền xử lý với Python.

### Thành viên 4 — Thực nghiệm

- Tách validation để chọn tham số; không tối ưu tham số trên test set.
- Matching instance theo IoU và quy tắc một-một.
- Báo cáo AP tại nhiều ngưỡng IoU, không chỉ một Dice toàn ảnh.
- Đo cả chất lượng, sai số đếm và thời gian xử lý.

## 4. Tiêu chí hoàn thành phần thành viên 1

- Có định nghĩa chính xác instance segmentation và star-convex.
- Có công thức probability target, ray distance, hai hàm loss và polygon
  decoding.
- Có mô tả/pseudocode NMS và ảnh hưởng của hai threshold.
- Có mô hình toán học Otsu và Watershed.
- Có phân tích ưu, nhược điểm và điều kiện áp dụng của ba phương pháp.
- Có tài liệu tham khảo gốc cho StarDist, U-Net, Otsu và Watershed.
- Có các giả thuyết có thể kiểm chứng bằng metric định lượng.


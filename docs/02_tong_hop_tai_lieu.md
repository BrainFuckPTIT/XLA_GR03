# Tổng hợp tài liệu — Thành viên 1

## Nguyên tắc lựa chọn nguồn

Ưu tiên bài báo gốc, tài liệu chính thức của ImageJ/StarDist và mã nguồn chính
thức. Blog hoặc bài viết thứ cấp chỉ nên dùng để học thao tác, không dùng làm
nguồn chính cho công thức hay kết luận khoa học.

## Bảng tài liệu cốt lõi

| Mã | Tài liệu | Nội dung cần khai thác | Dùng tại phần nào |
|---|---|---|---|
| T1 | Schmidt et al., 2018, *Cell Detection with Star-convex Polygons* | Thuật toán StarDist 2D gốc; probability target; ray distances; kiến trúc hai head; weighted MAE; NMS; AP theo IoU | Lý thuyết chính, mô hình toán, đối chiếu kết quả |
| T2 | Ronneberger et al., 2015, *U-Net* | Encoder–decoder, skip connection, học từ ít ảnh có augmentation | Nền tảng CNN/backbone |
| T3 | Otsu, 1979 | Tiêu chuẩn cực đại phương sai giữa lớp | Baseline Otsu |
| T4 | Vincent & Soille, 1991 | Watershed theo mô hình ngập lụt trong không gian số | Baseline Watershed |
| T5 | Kirillov et al., 2019, *Panoptic Segmentation* | Định nghĩa PQ, SQ và RQ | Metric instance tổng hợp |
| T6 | Kumar et al., 2017 | Dataset nhân mô bệnh học; AJI; khó khăn của threshold/Watershed trên nhân crowded | Dataset và metric bổ sung |
| T7 | Weigert et al., 2020, *StarDist 3D* | Mở rộng star-convex sang polyhedra; anisotropy; chi phí overlap | Hướng phát triển và giới hạn phạm vi 2D |
| T8 | ImageJ StarDist plugin documentation | Khả năng model built-in/custom, normalization, probability threshold, overlap threshold, label image và ROI | Chương Fiji và thiết kế kiểm chứng |
| T9 | StarDist FAQ | Tính phù hợp star-convex, reconstruction IoU, khác biệt Fiji/Python, tiling/GPU/NMS | Thảo luận và thiết kế thí nghiệm |
| T10 | StarDist source: `utils.py`, `matching.py`, `nms.py`, `stardist2d.cpp` | Hành vi implementation: EDT theo label, matching một-một, metric, công thức overlap NMS 2D | Cài đặt Python và kiểm chứng sát mã chuẩn |

## Ghi chú đọc tài liệu quan trọng

### T1 — StarDist 2D gốc

- Dữ liệu huấn luyện là cặp ảnh thô và ảnh nhãn instance đầy đủ.
- Mỗi pixel dự đoán một polygon, không phải mỗi đối tượng chỉ sinh một
  polygon ngay từ mạng.
- Probability target là normalized Euclidean distance đến nền.
- Polygon distance loss dùng probability target làm trọng số.
- Bài báo dùng 32 tia trong các thí nghiệm.
- Metric được gọi là $AP_\tau$ có công thức
  $TP/(TP+FP+FN)$; khi báo cáo phải đưa công thức để không lẫn với area under
  precision–recall curve.

### T8/T9 — Fiji và Python

- Fiji plugin là công cụ inference bằng model đã huấn luyện; Python là bản
  tham chiếu nhiều tính năng hơn và hỗ trợ training.
- Hai tham số hậu xử lý cần lưu là probability/score threshold và
  overlap/NMS threshold.
- Output label image/ROI giúp tiếp tục đo đạc bằng ImageJ.
- Fiji và Python chỉ có thể được coi là kiểm chứng lẫn nhau khi dùng cùng ảnh,
  model, normalization, scale và threshold.

### T10 — Những chi tiết chỉ thấy rõ khi đọc mã

- `edt_prob` chuẩn hoá EDT riêng cho từng object label.
- `matching` dùng Hungarian assignment để thiết lập ghép cặp một-một.
- 2D NMS trong `stardist2d.cpp` dùng
  $|A\cap B|/\min(|A|,|B|)$ cho overlap suppression.
- Vì tên biến/docstring có thể không đủ chính xác, báo cáo nên trích công thức
  thực thi của đúng phiên bản được dùng.

## Đường dẫn nguồn chính

1. [StarDist 2D paper](https://doi.org/10.1007/978-3-030-00934-2_30)
2. [U-Net paper](https://doi.org/10.1007/978-3-319-24574-4_28)
3. [Otsu paper](https://doi.org/10.1109/TSMC.1979.4310076)
4. [Watershed paper](https://doi.org/10.1109/34.87344)
5. [Panoptic Segmentation paper](https://openaccess.thecvf.com/content_CVPR_2019/html/Kirillov_Panoptic_Segmentation_CVPR_2019_paper.html)
6. [Kumar nuclei dataset paper](https://doi.org/10.1109/TMI.2017.2677499)
7. [StarDist 3D paper](https://openaccess.thecvf.com/content_WACV_2020/html/Weigert_Star-convex_Polyhedra_for_3D_Object_Detection_and_Segmentation_in_Microscopy_WACV_2020_paper.html)
8. [ImageJ StarDist plugin](https://imagej.net/plugins/stardist)
9. [StarDist FAQ](https://github.com/stardist/stardist-docs/blob/main/docs/faq.md)
10. [StarDist official source](https://github.com/stardist/stardist)

## Cách dùng danh mục này trong báo cáo

- Các phát biểu về đóng góp và kết quả StarDist: trích T1.
- Các công thức U-Net/Otsu/Watershed/PQ: trích lần lượt T2/T3/T4/T5.
- Các tham số hoặc giới hạn của plugin: trích T8, ghi ngày truy cập.
- Các chi tiết tái lập implementation: trích commit/tag mã nguồn cụ thể của
  T10 trong báo cáo cuối, thay vì chỉ ghi nhánh `main`.
- Kết quả do nhóm tự chạy phải ghi là kết quả thực nghiệm của nhóm, không gắn
  trích dẫn của bài báo gốc.


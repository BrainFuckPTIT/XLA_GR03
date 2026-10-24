# Đối chiếu trực tiếp Python và Fiji

`python scripts/compare_fiji_python.py` đọc ba nhãn Python chạy lại và nhãn
Fiji lịch sử, ghép ID một-một tại IoU 0.50, xuất F1, IoU ghép, Dice và pixel
agreement trên hợp foreground sau matching. Không so ID integer trực tiếp.

Tiêu chí mô tả: F1>=0.95 và Dice>=0.95. Median/high đạt, low chưa đạt.
Ca low: Python 9 đối tượng, Fiji 11, F1=0.900, Dice≈0.940.
Đây không phải kiểm định tương đương thống kê hay đánh giá với ground truth.

Overlay: xanh lá=Python chưa ghép, tím=Fiji chưa ghép, vàng=sai khác pixel/biên
sau matching. Parameter/boundary policy và hash từng nhãn ở comparison.csv.
NumPy linear percentiles và Java histogram percentiles/chặn âm khác nhau.

`../fiji_rerun/reproduction_check.csv` kiểm chứng riêng việc dựng lại plugin:
nhãn Maven/Java mới giống hoàn toàn từng pixel với nhãn Fiji lịch sử.

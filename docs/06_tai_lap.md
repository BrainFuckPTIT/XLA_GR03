# Tái lập từ clone sạch

## Python

1. Cài Python 3.11; tạo/kích hoạt `.venv` như README.
2. `python -m pip install -r requirements-model.txt`.
3. `python -m pip install -e ".[dev]"`.
4. `pytest -q`, `pytest -m integration -q`, `ruff check .`.
5. Chạy lần lượt benchmark, validation ablation, evaluator Fiji, đối chiếu,
   workflow evidence, report data theo README.

CLI/constants của script là nguồn tham số. Mỗi output định lượng ghi lại
tham số hiệu lực; YAML không có đường nạp đã được bỏ.
Không đổi test theo kết quả sweep. `validation_images.csv` cố định 30 ID bằng
seed 42. `dataset_manifest.csv` ghi image/mask SHA256, kích thước và dtype.

## Model và độc lập dữ liệu

Model `2D_versatile_fluo` lấy qua API StarDist chính thức. Hash weight/config/
threshold và phiên bản package được ghi trong provenance. Không có danh sách
ID train đầy đủ của weight trong repo để xác nhận độc lập với test. Không gọi
kết quả này là ước lượng tổng quát hoá độc lập khỏi dữ liệu model đã học.

## Fiji

Java 8 JDK + Maven 3.9 hoặc mới hơn. Đặt `JAVA_HOME`, thêm `mvn` vào PATH.
Chạy `python scripts/run_fiji_reference.py` để dựng classpath từ `fiji/pom.xml`
và sinh nhãn/log mới trong `results/fiji_rerun/`. Runner mặc định từ chối ghi
đè. Tham chiếu gốc vẫn ở `results/fiji_labels/` và log ngày 03/10/2026.

Muốn đo output chạy mới:

```bash
python scripts/evaluate_fiji_reference.py --labels results/fiji_rerun --run-log results/fiji_rerun/run_log.csv --output results/fiji_rerun/evaluation
```

Không so runtime Fiji cold command với runtime Python warm để xếp hạng tốc độ.
Maven tải artifact đã pin và các dependency; manifest JAR/SHA256 nằm cùng log.

## Báo cáo

Chạy `python scripts/build_report_data.py` sau khi có các CSV. Bảng LaTeX và
dữ liệu biểu đồ slide cùng lấy từ đó. Chạy từ thư mục `report`:

```bash
tectonic -X compile report.tex
# Hoặc latexmk -xelatex report.tex nếu dùng TeX Live với các package tương ứng.
```

Font TeX Gyre Termes dùng các file OTF do TeX phân phối để tránh phụ thuộc
Times New Roman của máy Windows. Thư mục dự án LaTeX là gốc repository vì ảnh,
code listing và BibTeX nằm ở các thư mục anh em của `report/`.

## Slide

Bản chính là Beamer 27 trang. Thư mục `slides/latex/` đóng gói đủ nguồn,
font sử dụng từ TeX, ảnh và bảng; không cần môi trường model để biên dịch:

```bash
cd slides/latex
tectonic main.tex
# Hoặc chạy xelatex main.tex hai lần với TeX Live đầy đủ.
```

Đọc `slides/latex/README.md` để tái sinh hình/bảng từ kết quả thực nghiệm.
PPTX cũ và hướng dẫn builder ở `slides/README.md` được giữ làm lựa chọn phụ.

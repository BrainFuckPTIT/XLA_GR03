# StarDist — LaTeX Beamer / Nhóm 03

Bản chính: **main.pdf**, 27 trang, 16:9 (24 nội dung + 3 phụ lục).
Thiết kế dùng TeX Gyre Heros, màu đỏ PTIT, navy và teal; Unicode tiếng Việt.
Công thức, bảng, TikZ và PGFPlots chỉnh trực tiếp trong nguồn, không phải ảnh chụp.

## Biên dịch độc lập

Giải nén toàn bộ gói nguồn, giữ cấu trúc `assets/` và `generated/`.
Từ thư mục chứa `main.tex`:

```bash
tectonic main.tex
# Hoặc XeLaTeX trong TeX Live đầy đủ:
xelatex -interaction=nonstopmode -halt-on-error main.tex
xelatex -interaction=nonstopmode -halt-on-error main.tex
```

Tectonic cần Internet lần đầu để tải package TeX. Không dùng pdfLaTeX.
Overleaf: tải gói ZIP, chọn **XeLaTeX**, main document **main.tex**.
Không cần Python, checkpoint hay dữ liệu DSB2018 để biên dịch nguồn đã đóng gói.
`theme.tex` điều khiển màu, font, footer và kích thước; `main.tex` chứa nội dung.

## Tái sinh hình và dữ liệu (trong repository đầy đủ)

Cài package dự án và `requirements-model.txt`, dùng Python 3.11.
Từ gốc repository:

```bash
python slides/latex/prepare_assets.py --model-maps
```

Script đọc CSV benchmark, validation, cross-platform; tạo bảng TeX và `.dat`
cho PGFPlots. Nhãn prediction được ghép màu với GT tại IoU 0.50; coral là
prediction không khớp. Hai đối tượng Fiji không khớp trong ca low được khoanh
trên ảnh thật. Bản đồ xác suất và tia số 0 là output CNN thật; provenance lưu
trong `generated/model_map_provenance.json`. EDT target tính từ GT đầy đủ,
sau đó cắt, không phải bản đồ xác suất dự đoán.

Nguồn hình: DSB2018 và nhãn thực nghiệm trong repository. Logo PTIT giữ nguyên
asset báo cáo. Kết quả là pretrained inference, không tuyên bố tự train CNN
hay chứng minh test độc lập với dữ liệu huấn luyện của checkpoint.

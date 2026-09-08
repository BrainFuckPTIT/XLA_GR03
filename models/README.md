# Models

Không commit model weight vào Git. Model pretrained được tải qua
`StarDist2D.from_pretrained` và cache trong môi trường người chạy.

Model chính thức hỗ trợ trong CLI:

- `2D_versatile_fluo`;
- `2D_paper_dsb2018`;
- `2D_versatile_he`.

Với custom model, lưu cục bộ một thư mục có `config.json` và weight, sau đó
truyền `--custom-model-dir`. Báo cáo phải ghi nguồn model, checksum và tập dữ
liệu huấn luyện.

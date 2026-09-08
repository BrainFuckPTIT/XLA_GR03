# Đóng góp vào XLA_GR03

## Quy trình nhánh

1. Cập nhật nhánh `main`.
2. Tạo nhánh theo mẫu `feature/<noi-dung>` hoặc `docs/<noi-dung>`.
3. Mỗi commit chỉ nên giải quyết một thay đổi logic.
4. Mở pull request, mô tả dữ liệu/tham số đã dùng và bằng chứng kiểm thử.
5. Chỉ merge khi CI đạt và ít nhất một thành viên khác đã xem lại.

Không commit trực tiếp dataset, model weight hoặc toàn bộ output thô lên Git.

## Quy ước commit

Khuyến nghị Conventional Commits:

- `feat:` tính năng mới;
- `fix:` sửa lỗi;
- `docs:` tài liệu;
- `test:` kiểm thử;
- `refactor:` tái cấu trúc không đổi hành vi;
- `chore:` cấu hình/công việc bảo trì.

Ví dụ:

```text
feat: add marker-controlled watershed baseline
docs: explain StarDist probability target
test: cover empty instance masks
```

## Kiểm tra trước khi tạo pull request

```bash
ruff check .
pytest
```

## Quy tắc thí nghiệm

- Không chọn threshold trên test set.
- Ghi model, seed, normalization, kích thước ảnh và toàn bộ tham số.
- Ground truth/prediction phải là label image integer cùng kích thước.
- Nếu thay đổi thuật toán hoặc metric, bổ sung unit test và giải thích trong
  pull request.
- Không ghi đè kết quả cũ; dùng ID chạy hoặc thư mục ngày giờ khi cần.

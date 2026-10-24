# Danh mục nộp bài

Các đường dẫn dưới đây là bản chính, đồng bộ từ lần chạy cập nhật ngày 24/10/2026.

| Nội dung | Bản chính |
|---|---|
| Báo cáo | `report/report.pdf` |
| Nguồn báo cáo | `report/report.tex`, `report/generated/`, `references/references.bib` |
| Slide | `slides/stardist_presentation_completed.pptx` (27 slide) |
| Nguồn slide | `slides/build_deck.mjs`, `slides/package.json`, `slides/README.md` |
| Code và kiểm thử | `src/xla_gr03/`, `scripts/`, `tests/`, `.github/workflows/ci.yml` |
| Môi trường Python | `requirements-model.txt`, `environment.yml`, freeze trong benchmark |
| Fiji | `fiji/pom.xml`, Java runner, `scripts/run_fiji_reference.py`, log/labels |
| Kết quả chính | `results/dsb2018_benchmark/`, `results/validation_ablation/`, `results/cross_platform/` |
| Hướng dẫn chạy | `README.md`, `docs/06_tai_lap.md` |

`slides/archive/` là lịch sử trước lần cập nhật, không dùng để nộp hoặc trích
số liệu hiện tại. Canva cũ cũng chưa được đồng bộ trong đợt sửa này.

Phạm vi: pretrained inference và các thành phần geometry/metric tự viết.
Không tuyên bố tự train CNN. Kết luận Fiji–Python chỉ áp dụng ba ca cố định và
nêu rõ ca không đạt. Đối chiếu rubric môn học nếu yêu cầu tự huấn luyện mạng.

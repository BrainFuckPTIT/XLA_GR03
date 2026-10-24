# Slide chính

Bản nộp: `stardist_presentation_completed.pptx` (27 slide).
`archive/` giữ các bản cũ để tra cứu, không dùng số liệu của chúng cho lần nộp mới.

Nguồn `build_deck.mjs` giữ thiết kế deck trước, lấy số liệu từ
`report/generated/slide_data.json` do `scripts/build_report_data.py` tạo.
Có thêm bảng đối chiếu Fiji–Python và biểu đồ validation sweep.

## Dựng tự động

Cần Node.js >=22, Artifact Tool **2.8.103** và bộ skill Presentations của Codex
(bundle 26.1022.11436). Đây là dependency runtime riêng của Codex, không phải
package có thể bảo đảm cài từ npm công khai. `package.json` ghi yêu cầu đó.
Mở/chỉnh PPTX bằng PowerPoint/LibreOffice không cần các dependency này.

Đặt ba biến theo đường dẫn runtime của máy, không dùng đường dẫn tài khoản tác giả:

```bash
export ARTIFACT_NODE_MODULES="/path/to/codex-runtime/node/node_modules"
export ARTIFACT_PYTHON="/path/to/codex-runtime/python/bin/python3"
export PRESENTATIONS_SKILL_DIR="/path/to/presentations/skills/presentations"
export RUNTIME_NODE_MODULES="$ARTIFACT_NODE_MODULES"
node slides/build_deck.mjs
```

Output mặc định trong `slides/`; bản nháp, render từng slide và kết quả validation
ở `.slides-build/`. Finalizer từ chối ghi đè file final có sẵn: đổi tên bản cũ trước
khi chủ đích tạo revision mới. Font Arial theo deck nguồn, nội dung bảng/chart
vẫn editable. Không cần môi trường Windows hay ổ D.

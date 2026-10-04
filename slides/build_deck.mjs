import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const workspaceDir = "D:/BTL_XLA";
const SKILL_DIR = "C:/Users/nguye/.codex/plugins/cache/openai-primary-runtime/presentations/26.909.12148/skills/presentations";
const RUNTIME_PYTHON = "C:/Users/nguye/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe";
const buildDir = path.join(workspaceDir, ".slides-build");
const finalPath = path.join(workspaceDir, "slides", "stardist_presentation_submission_v6.pptx");
await fs.mkdir(buildDir, { recursive: true });
await fs.mkdir(path.dirname(finalPath), { recursive: true });
const { resolvePresentationFont, applyPresentationChartFont, finalizePresentation } = await import(pathToFileURL(path.join(SKILL_DIR, "container_tools/artifact_tool_utils.mjs")).href);
const font = resolvePresentationFont();
const deck = Presentation.create({ slideSize: { width: 1280, height: 720 } });
const navy = "#0B1F3A", blue = "#1363DF", cyan = "#48CAE4", ink = "#14213D", gray = "#52616B", pale = "#F3F7FC", white = "#FFFFFF", orange = "#F59E0B";
const qualitativeMedian = new Uint8Array(await fs.readFile(path.join(workspaceDir, "results", "dsb2018_benchmark", "figures", "qualitative_median.png")));
const fijiReferencePanels = new Uint8Array(await fs.readFile(path.join(workspaceDir, "results", "fiji_reference", "fiji_reference_panels.png")));

function box(slide, x, y, w, h, fill = "none", line = "none") {
  return slide.shapes.add({ geometry: "rect", position: { left: x, top: y, width: w, height: h }, fill, line: { fill: line, width: line === "none" ? 0 : 1 } });
}
function text(slide, value, x, y, w, h, size = 22, color = ink, bold = false, align = "left") {
  const s = slide.shapes.add({ geometry: "textbox", position: { left: x, top: y, width: w, height: h }, fill: "none", line: { fill: "none", width: 0 } });
  s.text = value;
  s.text.style = { typeface: font, fontSize: size, color, bold, alignment: align, autoFit: "shrinkText" };
  return s;
}
function title(slide, value, number) {
  text(slide, value, 72, 48, 1030, 54, 34, navy, true);
  box(slide, 72, 112, 90, 5, blue);
  text(slide, String(number).padStart(2, "0"), 1150, 54, 58, 32, 16, gray, true, "right");
}
function footer(slide, note) { text(slide, note, 72, 676, 1136, 22, 12, gray); }
function bullets(slide, items, x, y, w, size = 22, gap = 58) { items.forEach((item, i) => { text(slide, "•", x, y + i * gap, 18, 30, size, blue, true); text(slide, item, x + 28, y + i * gap, w - 28, 42, size, ink); }); }
function step(slide, n, head, body, x, width) { box(slide, x, 255, width, 220, pale, "#CFE0F5"); text(slide, String(n), x + 24, 278, 38, 38, 23, blue, true); text(slide, head, x + 24, 330, width - 48, 34, 23, navy, true); text(slide, body, x + 24, 375, width - 48, 70, 17, gray); }

{ const s = deck.slides.add(); s.background.fill = navy; text(s, "PHÂN ĐOẠN TỪNG ĐỐI TƯỢNG\nBẰNG STARDIST", 78, 154, 850, 150, 47, white, true); text(s, "Đối chiếu Fiji/ImageJ và cài đặt Python", 80, 330, 740, 38, 26, cyan); box(s, 80, 402, 160, 6, orange); text(s, "Bài tập lớn Xử lý ảnh số | Nhóm 03 | PTIT", 80, 450, 720, 30, 20, white); text(s, "Thành viên: điền tên và MSSV trước khi nộp", 80, 492, 720, 26, 16, "#D4E2F4"); s.speakerNotes.textFrame.setText("Nguồn: Schmidt et al. (2018); tài liệu repo."); }
{ const s = deck.slides.add(); title(s, "Bài toán và mục tiêu", 2); text(s, "Instance segmentation", 72, 155, 470, 42, 28, navy, true); bullets(s, ["Không chỉ nhận diện foreground mà còn gán ID riêng cho từng tế bào.", "Cần thiết cho đếm tế bào, diện tích, hình dạng và phân tích sinh học.", "Khó nhất khi các nhân có biên mờ hoặc chạm nhau."], 72, 220, 530, 22); box(s, 690, 150, 450, 300, pale, "#CFE0F5"); text(s, "Mục tiêu", 730, 190, 300, 32, 26, blue, true); text(s, "1. Hiểu StarDist và plugin Fiji\n2. Cài đặt pipeline Python\n3. So sánh với Otsu và Watershed\n4. Đánh giá bằng metric instance", 730, 245, 350, 150, 21, ink); footer(s, "Ground truth là label image: nền = 0, mỗi instance có một ID dương."); }
{ const s = deck.slides.add(); title(s, "StarDist 2D", 3); text(s, "Mạng CNN/U-Net sinh hai trường dự đoán cho từng pixel", 72, 145, 900, 34, 23, gray); step(s, 1, "Probability map", "Score cao ở tâm object, thấp ở biên và nền.", 72, 250); step(s, 2, "Ray distances", "K khoảng cách đến biên theo các hướng cố định.", 360, 250); step(s, 3, "Polygon + NMS", "Giải mã proposal và giữ một polygon cho mỗi object.", 648, 250); step(s, 4, "Label image", "Rasterize polygon thành nhãn instance để đo metric.", 936, 250); footer(s, "StarDist paper dùng 32 tia trong các thí nghiệm 2D. Nguồn: Schmidt et al., 2018."); s.speakerNotes.textFrame.setText("Nguồn: Schmidt et al., Cell Detection with Star-convex Polygons, 2018."); }
{ const s = deck.slides.add(); title(s, "Biểu diễn star-convex", 4); text(s, "Một object star-convex cho phép nối từ tâm đến mọi điểm biên mà không đi ra ngoài object.", 72, 145, 1060, 38, 22, gray); box(s, 115, 250, 250, 250, "#DDEEFF", blue); text(s, "Tâm p", 205, 355, 80, 28, 22, navy, true, "center"); text(s, "Các tia r₀ … rₖ", 130, 520, 230, 28, 18, gray, false, "center"); text(s, "vₖ(p) = p + r̂ₖ(p)(cos θₖ, sin θₖ)", 450, 270, 620, 38, 28, navy, true); text(s, "Mỗi pixel foreground có một vector khoảng cách.\nNối các đầu tia tạo một đa giác đại diện cho instance.", 450, 340, 600, 85, 23, ink); text(s, "Giới hạn: hình vòng, nhiều nhánh hoặc lõm sâu có thể không phù hợp giả thiết.", 450, 460, 630, 52, 19, "#A34A00"); footer(s, "Chi tiết công thức và phân tích sai số: docs/01_ly_thuyet_stardist.md."); }
{ const s = deck.slides.add(); title(s, "Non-Maximum Suppression", 5); text(s, "CNN tạo nhiều proposal trùng cho một object. NMS chọn proposal có score cao trước.", 72, 150, 1080, 36, 23, gray); step(s, 1, "Lọc candidate", "Giữ pixel có probability ≥ ngưỡng.", 72, 255); step(s, 2, "Sắp theo score", "Proposal xác suất cao được xử lý trước.", 360, 255); step(s, 3, "So overlap", "Loại proposal chồng lấn quá ngưỡng NMS.", 648, 255); step(s, 4, "Gán nhãn", "Proposal còn lại trở thành instance cuối.", 936, 255); text(s, "Probability threshold ảnh hưởng recall. NMS threshold ảnh hưởng merge/split. Chọn trên validation, không chọn trên test.", 72, 535, 1100, 32, 20, "#A34A00", true); footer(s, "Phải ghi cả hai threshold trong run log Fiji và metadata Python."); }
{ const s = deck.slides.add(); title(s, "Hai baseline cổ điển", 6); text(s, "Otsu", 115, 175, 330, 35, 30, blue, true, "center"); text(s, "Watershed", 700, 175, 330, 35, 30, blue, true, "center"); box(s, 85, 235, 380, 250, pale, "#CFE0F5"); box(s, 675, 235, 380, 250, pale, "#CFE0F5"); text(s, "Ảnh → Gaussian → Otsu threshold\n→ morphology → connected components", 115, 290, 320, 82, 21, ink, false, "center"); text(s, "Nhanh, đơn giản\nNhược điểm: gộp object chạm nhau", 115, 395, 320, 58, 19, gray, false, "center"); text(s, "Otsu mask → EDT → local-max markers\n→ watershed(−distance)", 705, 290, 320, 82, 21, ink, false, "center"); text(s, "Có thể tách blob\nNhạy marker, nhiễu và min-distance", 705, 395, 320, 58, 19, gray, false, "center"); footer(s, "So sánh công bằng bằng cùng input, ground truth, split và instance metrics."); s.speakerNotes.textFrame.setText("Nguồn: Otsu (1979); Vincent & Soille (1991)."); }
{ const s = deck.slides.add(); title(s, "Fiji/ImageJ: nền tảng tham chiếu", 7); bullets(s, ["Artifact plugin thật: StarDist 0.3.0-scijava, ImageJ 2.9 + legacy 1.53t.", "Model fluorescent nuclei; pmin/pmax 1/99.8; probability .479071; NMS .3.", "Java 8 + TensorFlow 1.12 CPU; xuất Label Image TIFF, log đầy đủ runtime.", "Kiểm chứng trước trên ba ca low/median/high; Python đọc đúng TIFF plugin xuất.", "Không gộp 3 ca Fiji vào benchmark 50 ảnh hoặc dùng để xếp hạng."], 72, 145, 620, 19, 76); box(s, 730, 145, 470, 410, "#EAF6F9", "#9FD8E5"); s.images.add({ blob: fijiReferencePanels, contentType: "image/png", alt: "Ba ca input, ground truth và output StarDist Fiji ImageJ", fit: "contain", position: { left: 744, top: 158, width: 442, height: 354 } }); text(s, "AP@.50 = .801±.244 | PQ = .788±.160 | n = 3", 754, 520, 422, 22, 15, navy, true, "center"); footer(s, "Evidence: results/fiji_labels/, fiji/run_log_dsb2018_reference.csv và results/fiji_reference/."); }
{ const s = deck.slides.add(); title(s, "Cài đặt Python", 8); text(s, "Package xla_gr03 tách rõ phần nhóm tự viết và thư viện pretrained.", 72, 145, 1030, 35, 23, gray); const modules = [["preprocessing.py", "grayscale, percentile normalization"], ["baselines.py", "Otsu + connected components, Watershed"], ["geometry.py", "EDT, ray distances, polygon, NMS"], ["metrics.py", "IoU, Hungarian matching, AP/PQ/Dice"], ["stardist_pipeline.py", "wrapper StarDist pretrained"], ["cli.py", "segment và evaluate"]]; modules.forEach((m, i) => { const col = i % 2, row = Math.floor(i / 2); const x = 72 + col * 560, y = 225 + row * 120; box(s, x, y, 510, 84, pale, "#CFE0F5"); text(s, m[0], x + 20, y + 15, 220, 24, 19, blue, true); text(s, m[1], x + 20, y + 45, 460, 22, 16, ink); }); footer(s, "Chạy: python scripts/run_experiment.py ... | Test/lint: pytest; ruff check ."); }
{ const s = deck.slides.add(); title(s, "Benchmark DSB2018: 50 ảnh test", 9); text(s, "Watershed chọn min-distance = 9 trên 30 ảnh train. StarDist dùng model default threshold, không tune trên test.", 72, 145, 1080, 30, 20, gray); const chart = s.charts.add("bar", { position: { left: 72, top: 210, width: 590, height: 330 }, categories: ["Otsu", "Watershed", "StarDist Python"], series: [{ name: "AP@0.50", values: [0.643, 0.715, 0.853], fill: blue }, { name: "PQ@0.50", values: [0.627, 0.677, 0.785], fill: cyan }], barOptions: { direction: "column", grouping: "clustered" }, hasLegend: true, dataLabels: { showValue: true, position: "outEnd" } }); applyPresentationChartFont(chart, { fontFamily: font }); const rows = [["Method", "AP@.50", "PQ@.50", "Dice", "MAE"], ["Otsu", ".643±.238", ".627±.208", ".895", "14.06"], ["Watershed", ".715±.199", ".677±.166", ".894", "6.94"], ["StarDist Python", ".853±.120", ".785±.110", ".916", "3.44"]]; rows.forEach((row, r) => row.forEach((cell, c) => { const x = [690, 838, 946, 1054, 1156][c]; const w = [144, 104, 104, 96, 52][c]; box(s, x, 225 + r * 65, w, 65, r === 0 ? navy : r === 3 ? "#E7F4EE" : pale, r === 0 ? navy : "#CFE0F5"); text(s, cell, x + 6, 245 + r * 65, w - 12, 25, r === 0 ? 15 : 16, r === 0 ? white : ink, r === 0 || c === 0); })); text(s, "StarDist tăng AP/PQ và giảm sai số đếm; runtime Python CPU 0.112 s/ảnh. Evidence Fiji n=3 trình bày riêng ở slide 7.", 72, 570, 1100, 38, 18, "#A34A00", true); footer(s, "Mean ± SD trên 50 test images. CSV: results/dsb2018_benchmark/summary_metrics.csv."); s.speakerNotes.textFrame.setText("Nguồn: benchmark do nhóm chạy bằng archive DSB2018 do StarDist công bố; Caicedo et al. (2019)."); }
{ const s = deck.slides.add(); title(s, "Kết luận và case định tính trung vị", 10); bullets(s, ["StarDist tăng AP@.50/PQ và giảm MAE đếm trên 50 ảnh test; Dice foreground riêng lẻ không đủ nói lên chất lượng instance.", "Case trung vị bên dưới cho thấy Otsu thường merge nhân chạm nhau, Watershed cải thiện nhờ marker, StarDist bám ground truth sát hơn."], 72, 112, 1120, 20, 57); box(s, 70, 245, 1140, 238, "#F3F7FC", "#CFE0F5"); s.images.add({ blob: qualitativeMedian, contentType: "image/png", alt: "Case DSB2018 trung vị: input, ground truth, Otsu, Watershed va StarDist", fit: "contain", position: { left: 72, top: 247, width: 1136, height: 234 } }); text(s, "Chốt nộp bài: điền tên/MSSV/mã nhóm • PDF, code, 50-image benchmark và evidence Fiji/ImageJ n=3 đã sẵn sàng.", 72, 535, 1100, 28, 18, ink, true); footer(s, "Evidence: results/dsb2018_benchmark/figures/qualitative_median.png và results/fiji_reference/."); }

const candidatePath = path.join(buildDir, "candidate.pptx");
await (await PresentationFile.exportPptx(deck)).save(candidatePath);
const result = await finalizePresentation({
  explicitTotalSlideCount: 10,
  materializeLiteralChartWorkbooks: true,
  workspaceDir,
  candidatePath,
  finalPath,
  pythonExecutable: RUNTIME_PYTHON,
  integrityValidatorPath: path.join(SKILL_DIR, "container_tools/inspect_presentation_package_integrity.py"),
  layoutValidatorPath: path.join(SKILL_DIR, "container_tools/inspect_presentation_layout_geometry.py"),
  layoutArgs: ["--expected-slide-size-emu", "12192000,6858000", "--validate-bullet-geometry", "--validate-heading-fit"],
  fontPolicy: { basis: "design", families: [font] },
  verifyArtifactToolImport: true,
  receiptPath: path.join(buildDir, "validation_submission_v6.json"),
});
const montage = await deck.export({ format: "webp", montage: true, scale: 1 });
await fs.writeFile(path.join(buildDir, "montage.webp"), new Uint8Array(await montage.arrayBuffer()));
console.log(JSON.stringify({ finalPath, result }, null, 2));

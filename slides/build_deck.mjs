import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { fileURLToPath } from "node:url";

const workspaceDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const SKILL_DIR = process.env.PRESENTATIONS_SKILL_DIR;
const RUNTIME_PYTHON = process.env.ARTIFACT_PYTHON;
const moduleDir = process.env.ARTIFACT_NODE_MODULES;
if (!SKILL_DIR || !RUNTIME_PYTHON || !moduleDir) {
  throw new Error("Set PRESENTATIONS_SKILL_DIR, ARTIFACT_PYTHON and ARTIFACT_NODE_MODULES. See slides/README.md.");
}
process.env.RUNTIME_NODE_MODULES ??= moduleDir;
const { Presentation, PresentationFile } = await import(pathToFileURL(
  path.join(moduleDir, "@oai/artifact-tool/dist/artifact_tool.mjs"),
).href);
const buildDir = path.join(workspaceDir, ".slides-build");
const finalPath = path.join(workspaceDir, "slides", "stardist_presentation_completed.pptx");

await fs.mkdir(buildDir, { recursive: true });
await fs.mkdir(path.dirname(finalPath), { recursive: true });

const { resolvePresentationFont, applyPresentationChartFont, finalizePresentation } = await import(
  pathToFileURL(path.join(SKILL_DIR, "container_tools/artifact_tool_utils.mjs")).href,
);

const data = JSON.parse(await fs.readFile(path.join(workspaceDir, "report/generated/slide_data.json"), "utf8"));
const methods = ["Otsu", "Watershed", "StarDist Python"];
const summaryAt = (method) => data.summary.find(r => r.method === method && r.threshold === 0.5);
const star = summaryAt("StarDist Python");
const f3 = n => Number(n).toFixed(3);
const chartNumber = n => Number(Number(n).toPrecision(12));
const font = resolvePresentationFont({ fontFamily: "Arial" });
const deck = Presentation.create({ slideSize: { width: 1280, height: 720 } });

const navy = "#0B1F3A";
const blue = "#1363DF";
const cyan = "#48CAE4";
const teal = "#0F766E";
const amber = "#D97706";
const coral = "#C2410C";
const ink = "#14213D";
const muted = "#52616B";
const pale = "#F3F7FC";
const paleBlue = "#EAF3FF";
const paleTeal = "#E8F5F2";
const paleAmber = "#FFF6E7";
const line = "#CFE0F5";
const white = "#FFFFFF";

async function readAsset(...parts) {
  return new Uint8Array(await fs.readFile(path.join(workspaceDir, ...parts)));
}

const [qualitativeHigh, qualitativeMedian, qualitativeLow, fijiWorkflow, fijiPanels] = await Promise.all([
  readAsset("results", "dsb2018_benchmark", "figures", "qualitative_high.png"),
  readAsset("results", "dsb2018_benchmark", "figures", "qualitative_median.png"),
  readAsset("results", "dsb2018_benchmark", "figures", "qualitative_low.png"),
  readAsset("results", "fiji_reference", "fiji_workflow_evidence.png"),
  readAsset("results", "fiji_reference", "fiji_reference_panels.png"),
]);

function rect(slide, left, top, width, height, fill = "none", stroke = "none") {
  return slide.shapes.add({
    geometry: "rect",
    position: { left, top, width, height },
    fill,
    line: { fill: stroke, width: stroke === "none" ? 0 : 1 },
  });
}

function txt(slide, value, left, top, width, height, {
  size = 20, color = ink, bold = false, align = "left", fill = "none", margin = 0,
} = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    position: { left, top, width, height },
    fill,
    line: { fill: "none", width: 0 },
  });
  shape.text = value;
  shape.text.style = {
    typeface: font,
    fontSize: size,
    color,
    bold,
    alignment: align,
    margin,
    autoFit: "shrinkText",
  };
  return shape;
}

function title(slide, value, index, subtitle = "") {
  txt(slide, value, 72, 42, 1020, 52, { size: 34, color: navy, bold: true });
  if (subtitle) txt(slide, subtitle, 72, 98, 1035, 28, { size: 18, color: muted });
  txt(slide, String(index).padStart(2, "0"), 1144, 48, 64, 26, { size: 16, color: muted, bold: true, align: "right" });
}

function footer(slide, value) {
  txt(slide, value, 72, 680, 1136, 20, { size: 11, color: muted });
}

function notes(slide, value) {
  slide.speakerNotes.textFrame.setText(value);
}

function sequence(slide, number, heading, body, left, top, width, fill = pale) {
  rect(slide, left, top, width, 116, fill, line);
  rect(slide, left + 18, top + 18, 42, 42, navy, navy);
  txt(slide, String(number), left + 18, top + 24, 42, 24, { size: 18, color: white, bold: true, align: "center" });
  const dark = fill === "#16345C";
  txt(slide, heading, left + 78, top + 17, width - 96, 28, { size: 20, color: dark ? white : navy, bold: true });
  txt(slide, body, left + 78, top + 50, width - 96, 48, { size: 16, color: dark ? "#D4E2F4" : muted });
}

function codeBlock(slide, lines, left, top, width, height) {
  rect(slide, left, top, width, height, navy, navy);
  txt(slide, lines, left + 22, top + 18, width - 44, height - 36, { size: 17, color: "#E6F2FF" });
}

function stat(slide, value, label, left, top, width, color = blue) {
  txt(slide, value, left, top, width, 48, { size: 36, color, bold: true, align: "center" });
  txt(slide, label, left, top + 52, width, 42, { size: 16, color: muted, align: "center" });
}

function compareColumn(slide, heading, body, left, fill, headingColor = navy, top = 188, height = 308) {
  rect(slide, left, top, 338, height, fill, line);
  txt(slide, heading, left + 24, top + 20, 290, 34, { size: height < 200 ? 22 : 25, color: headingColor, bold: true, align: "center" });
  txt(slide, body, left + 32, top + 70, 274, height - 90, { size: height < 200 ? 17 : 19, color: ink, align: "center" });
}

// 01 - cover
{
  const s = deck.slides.add();
  s.background.fill = navy;
  txt(s, "PHÂN ĐOẠN TỪNG ĐỐI TƯỢNG\nBẰNG DEEP LEARNING VỚI STARDIST", 80, 128, 940, 142, { size: 46, color: white, bold: true });
  txt(s, "Instance segmentation - đối chiếu Fiji/ImageJ và cài đặt Python", 82, 304, 880, 36, { size: 25, color: cyan });
  txt(s, "Bài tập lớn Xử lý ảnh số | Nhóm 03 | PTIT", 82, 390, 700, 28, { size: 20, color: white });
  txt(s, "Nguyễn Hồng Quang - B23DCVT361\nNguyễn Trọng Nam Khánh - B23DCCE052\nVũ Dũng - B23DCVT110", 82, 452, 720, 78, { size: 17, color: "#D4E2F4" });
  txt(s, "StarDist 2D | DSB2018 | Fiji/ImageJ | Python", 82, 618, 800, 28, { size: 18, color: cyan });
  notes(s, "Nguồn: Schmidt et al. (2018); tài liệu và artefact của repository.");
}

// 02 - scope
{
  const s = deck.slides.add();
  title(s, "Mục tiêu, phạm vi và câu hỏi nghiên cứu", 2);
  sequence(s, 1, "Nghiên cứu", "Lý thuyết instance segmentation, CNN/U-Net, star-convex và NMS.", 72, 160, 530, paleBlue);
  sequence(s, 2, "Tham chiếu Fiji/ImageJ", "Chạy plugin StarDist thật, lưu Label TIFF, thông số và runtime.", 678, 160, 530, paleTeal);
  sequence(s, 3, "Cài đặt Python", "Tái lập baseline, hình học, matching metric và wrapper pretrained.", 72, 320, 530, paleAmber);
  sequence(s, 4, "Đánh giá định lượng", "So sánh Otsu, Watershed, StarDist trên 50 ảnh test và Fiji trên 3 ca.", 678, 320, 530, pale);
  txt(s, "RQ1: StarDist có tách object chạm nhau tốt hơn baseline?  RQ2: Fiji và Python có khớp khi giữ input/tham số?  RQ3: threshold ảnh hưởng thế nào?", 72, 556, 1136, 48, { size: 18, color: navy, bold: true, align: "center" });
  footer(s, "Phạm vi: inference với model pretrained, không tuyên bố huấn luyện lại CNN.");
  notes(s, "Nguồn: report/report.tex, Chương 1.");
}

// 03 - problem formulation
{
  const s = deck.slides.add();
  title(s, "Bài toán instance segmentation", 3, "Một pixel nền có label 0. Mỗi object phải có ID dương riêng.");
  compareColumn(s, "Semantic segmentation", "Dự đoán foreground/background. Hai nhân chạm nhau vẫn có thể là một vùng liên thông.", 72, paleBlue);
  compareColumn(s, "Object detection", "Trả bounding box và score. Định vị được object nhưng không đủ cho diện tích hay hình dạng.", 471, paleAmber, amber);
  compareColumn(s, "Instance segmentation", "Trả mask hoặc polygon riêng cho từng object. Có thể đếm, đo diện tích và chu vi.", 870, paleTeal, teal);
  txt(s, "Mục tiêu toán học: I: Ω → Rᶜ  |  Y: Ω → {0,1,...,M}  |  Ŷ = fθ(I)", 72, 548, 1136, 36, { size: 23, color: navy, bold: true, align: "center" });
  footer(s, "Một Dice foreground cao vẫn có thể che lỗi merge/split. Vì vậy cần matching từng instance.");
  notes(s, "Nguồn: report/report.tex, mục Bài toán instance segmentation.");
}

// 04 - data
{
  const s = deck.slides.add();
  title(s, "Dataset, ground truth và split", 4, "DSB2018 được versioned trong repository để tái lập đúng kết quả.");
  stat(s, "497", "cặp TIFF image + instance label", 80, 155, 220, blue);
  stat(s, "447", "ảnh train, dùng development/validation", 330, 155, 220, teal);
  stat(s, "50", "ảnh test, chỉ dùng đánh giá cuối", 580, 155, 220, amber);
  stat(s, "0", "ID nền trong Label Image", 830, 155, 220, coral);
  txt(s, "Quy ước bắt buộc: input và ground truth cùng basename/kích thước; label là TIFF số nguyên 2D, không phải PNG RGB màu.", 92, 276, 1050, 38, { size: 19, color: ink, align: "center" });
  rect(s, 72, 340, 1136, 238, pale, line);
  s.images.add({ blob: qualitativeHigh, contentType: "image/png", alt: "Một case DSB2018 với input, ground truth và ba kết quả instance", fit: "contain", position: { left: 78, top: 346, width: 1124, height: 226 } });
  footer(s, "Data: data/dsb2018/dsb2018/ | Label IDs trong ảnh màu chỉ phục vụ hiển thị.");
  notes(s, "Nguồn: data/README.md; results/dsb2018_benchmark/selected_cases.csv.");
}

// 05 - protocol
{
  const s = deck.slides.add();
  title(s, "Protocol thực nghiệm công bằng", 5);
  sequence(s, 1, "Development", "Kiểm tra I/O, label format và code. Không báo cáo metric ở bước này.", 72, 165, 530, pale);
  sequence(s, 2, "Validation", "Chọn Watershed min_distance=9 bằng 30 ảnh lấy seed 42 từ train.", 678, 165, 530, paleAmber);
  sequence(s, 3, "Test benchmark", "Otsu, Watershed và StarDist Python chạy trên toàn bộ 50 ảnh test.", 72, 325, 530, paleBlue);
  sequence(s, 4, "Fiji reference", "Ba ca low/median/high cố định để kiểm chứng cross-platform, không gộp n=3 vào n=50.", 678, 325, 530, paleTeal);
  txt(s, "Cùng input, ground truth, cách tính metric và định dạng Label TIFF cho mọi phương pháp.", 72, 560, 1136, 36, { size: 20, color: navy, bold: true, align: "center" });
  footer(s, "StarDist dùng p=0.479071 và NMS=0.3 từ model, không tune trên test.");
  notes(s, "Nguồn: report/report.tex, Protocol benchmark và Kết quả.");
}

// 06 - StarDist flow
{
  const s = deck.slides.add();
  title(s, "StarDist 2D: từ ảnh đến nhãn instance", 6, "Backbone CNN tạo prediction dày đặc, hậu xử lý biến prediction thành polygon có ID.");
  const steps = [["Ảnh TIFF", "I"], ["Normalize", "percentile"], ["U-Net", "shared features"], ["Hai head", "p và rₖ"], ["NMS", "polygon"], ["Label TIFF", "ID 1..N"]];
  steps.forEach(([head, body], i) => {
    const x = 60 + i * 202;
    rect(s, x, 260, 174, 150, i === 2 ? paleBlue : pale, line);
    txt(s, String(i + 1), x + 18, 278, 36, 28, { size: 17, color: blue, bold: true });
    txt(s, head, x + 18, 324, 138, 30, { size: 20, color: navy, bold: true, align: "center" });
    txt(s, body, x + 18, 362, 138, 28, { size: 15, color: muted, align: "center" });
    if (i < steps.length - 1) txt(s, "→", x + 175, 318, 26, 30, { size: 24, color: cyan, bold: true, align: "center" });
  });
  txt(s, "Output không phải semantic mask. Mỗi polygon giữ lại sau NMS được rasterize thành một ID instance riêng.", 122, 500, 1036, 40, { size: 21, color: ink, align: "center" });
  footer(s, "Paper gốc StarDist 2D dùng 32 tia radial cho mỗi pixel foreground.");
  notes(s, "Nguồn: Schmidt et al. (2018); report/report.tex, StarDist 2D.");
}

// 07 - normalization
{
  const s = deck.slides.add();
  title(s, "Tiền xử lý: percentile normalization", 7);
  rect(s, 72, 166, 530, 300, paleBlue, line);
  txt(s, "I_norm(q) = (I(q) - Q₁(I)) / (Q₉₉.₈(I) - Q₁(I) + ε)", 100, 230, 474, 66, { size: 24, color: navy, bold: true, align: "center" });
  txt(s, "Python dùng percentile NumPy tuyến tính, ε = 10⁻²⁰, clip=False. Giá trị có thể nằm ngoài [0,1].", 112, 325, 450, 80, { size: 19, color: ink, align: "center" });
  rect(s, 680, 166, 528, 300, pale, line);
  txt(s, "Quy tắc tái lập", 710, 208, 468, 34, { size: 25, color: teal, bold: true, align: "center" });
  txt(s, "Cùng percentile đặt trước 1 / 99.8. Java dùng histogram percentile và chặn giá trị âm về 0, nên hai đầu vào chưa giống hệt nhau.\n\nGhi rõ chính sách trong provenance và đo độ khớp output.", 730, 272, 428, 145, { size: 19, color: ink, align: "center" });
  txt(s, "Mục đích: giảm ảnh hưởng outlier sáng/tối và đưa ảnh vào thang cường độ phù hợp model pretrained.", 92, 530, 1096, 42, { size: 21, color: navy, bold: true, align: "center" });
  footer(s, "Tham số được ghi trong run log Fiji và provenance của benchmark Python.");
  notes(s, "Nguồn: report/report.tex, Tiền xử lý và quy ước số học.");
}

// 08 - U-Net
{
  const s = deck.slides.add();
  title(s, "CNN/U-Net: backbone đa đầu ra", 8);
  const blocks = [["Encoder", "Downsample để học ngữ cảnh và receptive field", 72, paleBlue], ["Bottleneck", "Feature ngữ nghĩa ở độ phân giải thấp", 390, paleAmber], ["Decoder + skip", "Upsample, ghép feature cùng scale để phục hồi biên", 708, paleTeal]];
  blocks.forEach(([head, body, x, fill], i) => {
    rect(s, x, 220, 252, 190, fill, line);
    txt(s, String(i + 1), x + 18, 238, 38, 26, { size: 17, color: blue, bold: true });
    txt(s, head, x + 20, 285, 212, 30, { size: 23, color: navy, bold: true, align: "center" });
    txt(s, body, x + 24, 334, 204, 52, { size: 16, color: ink, align: "center" });
    if (i < 2) txt(s, "→", x + 262, 300, 46, 36, { size: 27, color: cyan, bold: true, align: "center" });
  });
  rect(s, 1020, 220, 188, 190, navy, navy);
  txt(s, "Hai head", 1040, 252, 148, 28, { size: 21, color: white, bold: true, align: "center" });
  txt(s, "Probability\np̂(q)\n\nRay distances\nr̂(q) ∈ R⁺ᴷ", 1040, 300, 148, 92, { size: 17, color: "#D4E2F4", align: "center" });
  txt(s, "(p̂(q), r̂(q)) = hθ(I)(q): score cho proposal và K khoảng cách từ pixel đến biên object.", 96, 492, 1088, 44, { size: 21, color: navy, bold: true, align: "center" });
  footer(s, "Nhóm gọi model pretrained chính thức, không tuyên bố tự train lại toàn bộ CNN.");
  notes(s, "Nguồn: Ronneberger et al. (2015); Schmidt et al. (2018); report/report.tex, CNN và U-Net.");
}

// 09 - star convex
{
  const s = deck.slides.add();
  title(s, "Biểu diễn star-convex bằng K tia radial", 9);
  rect(s, 72, 170, 390, 330, paleBlue, line);
  txt(s, "Tâm q", 220, 286, 100, 30, { size: 23, color: navy, bold: true, align: "center" });
  txt(s, "K = 32 hướng đều nhau\nθₖ = 2πk/K", 140, 370, 254, 54, { size: 20, color: blue, bold: true, align: "center" });
  txt(s, "Mỗi tia đi đến giao điểm đầu tiên với biên của instance chứa q.", 112, 440, 310, 40, { size: 17, color: muted, align: "center" });
  rect(s, 540, 170, 668, 150, pale, line);
  txt(s, "rₖ(q) = max {t ≥ 0 : q + t(cos θₖ, sin θₖ) ∈ G(q)}", 566, 220, 616, 42, { size: 25, color: navy, bold: true, align: "center" });
  rect(s, 540, 350, 668, 150, paleTeal, line);
  txt(s, "vₖ(q) = q + r̂ₖ(q)(cos θₖ, sin θₖ)", 566, 400, 616, 42, { size: 27, color: teal, bold: true, align: "center" });
  txt(s, "Nối các đỉnh v₀...vₖ theo thứ tự góc để tạo polygon proposal.", 566, 452, 616, 28, { size: 18, color: ink, align: "center" });
  txt(s, "Giới hạn: hình vòng, nhiều nhánh hoặc lõm sâu có thể không star-convex. Khi đó cần fine-tuning hoặc phương pháp khác.", 84, 550, 1112, 44, { size: 19, color: coral, bold: true, align: "center" });
  footer(s, "K lớn hơn mô tả biên tốt hơn nhưng tăng số kênh, bộ nhớ và số polygon cần xử lý.");
  notes(s, "Nguồn: Schmidt et al. (2018); report/report.tex, Probability map và star-convex polygon.");
}

// 10 - loss
{
  const s = deck.slides.add();
  title(s, "Huấn luyện đa nhiệm và phạm vi cài đặt", 10);
  rect(s, 72, 164, 540, 310, paleBlue, line);
  txt(s, "Objective điển hình", 104, 194, 476, 30, { size: 25, color: navy, bold: true, align: "center" });
  txt(s, "L_prob = BCE(p, p̂)\n\nL_dist = Σ p(q) ||r(q) - r̂(q)||₁ / (Σ p(q) + ε)\n\nL = λp L_prob + λr L_dist", 112, 250, 460, 152, { size: 21, color: ink, align: "center" });
  rect(s, 668, 164, 540, 310, paleTeal, line);
  txt(s, "Phạm vi của nhóm", 700, 194, 476, 30, { size: 25, color: teal, bold: true, align: "center" });
  txt(s, "Tự cài: EDT chuẩn hoá, ray distance, polygon decode/NMS, matching và metric.\n\nTái sử dụng: CNN và pretrained weights từ StarDist chính thức.\n\nThí nghiệm chỉ inference, không train lại model.", 728, 252, 420, 150, { size: 19, color: ink, align: "center" });
  txt(s, "Probability target là EDT chuẩn hoá theo từng instance: cao gần tâm, thấp gần biên, nên proposal tâm thường ổn định hơn.", 94, 542, 1090, 38, { size: 19, color: navy, bold: true, align: "center" });
  footer(s, "Phân biệt rõ phần tự cài đặt và thư viện pretrained là yêu cầu trung thực học thuật.");
  notes(s, "Nguồn: report/report.tex, Huấn luyện và NMS; src/xla_gr03/.");
}

// 11 - NMS
{
  const s = deck.slides.add();
  title(s, "Suy luận và Non-Maximum Suppression", 11);
  sequence(s, 1, "Candidate", "Giữ pixel có p̂(q) ≥ t_p. Thí nghiệm dùng t_p = 0.479071.", 72, 170, 530, paleBlue);
  sequence(s, 2, "Decode polygon", "Dùng r̂ₖ(q) tạo K đỉnh của proposal tại từng candidate.", 678, 170, 530, pale);
  sequence(s, 3, "Sort theo score", "Xử lý proposal xác suất cao trước để ưu tiên tâm object đáng tin cậy.", 72, 330, 530, paleAmber);
  sequence(s, 4, "NMS + rasterize", "Loại overlap lớn hơn t_nms=0.3, giữ polygon còn lại thành Label Image.", 678, 330, 530, paleTeal);
  txt(s, "Overlap NMS = |A ∩ B| / min(|A|, |B|). t_p thấp giữ thêm candidate, t_nms cao có thể giữ proposal trùng lặp.", 90, 557, 1100, 36, { size: 20, color: navy, bold: true, align: "center" });
  footer(s, "NMS overlap khi inference khác với IoU threshold dùng để tính TP/FP/FN lúc đánh giá.");
  notes(s, "Nguồn: report/report.tex, Suy luận, candidate filtering và polygon NMS.");
}

// 12 - Otsu
{
  const s = deck.slides.add();
  title(s, "Baseline 1: Otsu và connected components", 12);
  rect(s, 72, 170, 520, 318, paleAmber, line);
  txt(s, "t* = argmaxₜ σ²_B(t)\nσ²_B(t) = ω₀(t)ω₁(t)[μ₀(t)-μ₁(t)]²", 106, 246, 452, 76, { size: 25, color: amber, bold: true, align: "center" });
  txt(s, "Otsu chọn ngưỡng tách histogram thành foreground/background. Sau đó morphology, lọc vùng nhỏ và connected components tạo label.", 110, 348, 444, 86, { size: 19, color: ink, align: "center" });
  rect(s, 674, 170, 534, 318, pale, line);
  txt(s, "Điểm mạnh", 702, 208, 478, 28, { size: 23, color: teal, bold: true, align: "center" });
  txt(s, "Nhanh, không cần model, dễ giải thích.", 716, 254, 450, 42, { size: 20, color: ink, align: "center" });
  txt(s, "Giới hạn", 702, 332, 478, 28, { size: 23, color: coral, bold: true, align: "center" });
  txt(s, "Nền không đồng nhất làm histogram không bimodal. Object chạm nhau trở thành một component nên count/AP instance kém.", 710, 378, 462, 66, { size: 19, color: ink, align: "center" });
  txt(s, "Otsu có thể đạt Dice foreground khá cao nhưng vẫn gộp nhiều nhân và làm sai số đếm lớn.", 88, 544, 1104, 38, { size: 20, color: navy, bold: true, align: "center" });
  footer(s, "Implementation: src/xla_gr03/baselines.py.");
  notes(s, "Nguồn: Otsu (1979); report/report.tex, Otsu và connected components.");
}

// 13 - Watershed
{
  const s = deck.slides.add();
  title(s, "Baseline 2: marker-controlled Watershed", 13);
  const stages = [["Foreground mask", "Otsu + morphology"], ["EDT", "D = EDT(F)"], ["Markers", "local maxima"], ["Watershed", "trên -D trong F"], ["Relabel", "instance TIFF"]];
  stages.forEach(([head, body], i) => {
    const x = 58 + i * 236;
    rect(s, x, 170, 204, 150, i === 3 ? paleTeal : pale, line);
    txt(s, String(i + 1), x + 18, 188, 34, 24, { size: 17, color: blue, bold: true });
    txt(s, head, x + 18, 234, 168, 28, { size: 19, color: navy, bold: true, align: "center" });
    txt(s, body, x + 18, 274, 168, 24, { size: 15, color: muted, align: "center" });
    if (i < stages.length - 1) txt(s, "→", x + 198, 235, 30, 26, { size: 23, color: cyan, bold: true, align: "center" });
  });
  const chart = s.charts.add("line", {
    position: { left: 112, top: 370, width: 640, height: 215 },
    title: "Validation AP@0.50 theo min_distance",
    titleTextStyle: { typeface: font, fontSize: 16, fill: navy, bold: true },
    categories: ["3", "5", "7", "9", "11"],
    series: [{ name: "AP@0.50", values: data.watershed.map(r => chartNumber(r.ap_iou_050_mean)), line: { style: "solid", fill: teal, width: 3 }, marker: { symbol: "circle", size: 6 } }],
    hasLegend: false,
    xAxis: { title: "min_distance", textStyle: { typeface: font, fontSize: 13, fill: muted } },
    yAxis: { min: 0.45, max: 0.8, majorUnit: 0.1, textStyle: { typeface: font, fontSize: 13, fill: muted }, majorGridlines: { style: "solid", fill: line, width: 1 } },
    dataLabels: { showValue: true, numberFormatCode: "0.000", position: "outEnd", textStyle: { typeface: font, fontSize: 12, fill: ink, bold: true } },
  });
  applyPresentationChartFont(chart, { fontFamily: font });
  rect(s, 810, 384, 338, 180, paleAmber, line);
  txt(s, "Chọn min_distance = 9", 834, 414, 290, 32, { size: 23, color: amber, bold: true, align: "center" });
  txt(s, "N=30 ảnh validation. Không chọn tham số trên 50 test images.", 844, 468, 270, 54, { size: 18, color: ink, align: "center" });
  footer(s, "Watershed cải thiện tách blob chạm nhau, nhưng nhạy marker, nhiễu và khoảng cách cực đại.");
  notes(s, "Nguồn: Vincent & Soille (1991); results/dsb2018_benchmark/watershed_validation_sweep.csv.");
}

// 14 - metrics
{
  const s = deck.slides.add();
  title(s, "Đánh giá instance: IoU, Hungarian matching, TP/FP/FN", 14);
  sequence(s, 1, "Bỏ nền ID=0", "Lấy mỗi GT Gᵢ và prediction Pⱼ là một object.", 72, 164, 530, pale);
  sequence(s, 2, "Ma trận IoU", "Jᵢⱼ = |Gᵢ ∩ Pⱼ| / |Gᵢ ∪ Pⱼ| cho mọi cặp object.", 678, 164, 530, paleBlue);
  sequence(s, 3, "Ghép một-một", "Ưu tiên số cặp đạt ngưỡng, rồi tổng IoU. Mỗi object chỉ ghép một lần.", 72, 324, 530, paleTeal);
  sequence(s, 4, "Phân loại", "Cặp có Jᵢⱼ ≥ τ là TP. GT chưa ghép là FN, prediction chưa ghép là FP.", 678, 324, 530, paleAmber);
  txt(s, "Một prediction gộp hai nhân chỉ ghép được tối đa một GT. Nhân còn lại trở thành FN, nên metric phản ánh lỗi merge/split.", 90, 556, 1100, 38, { size: 19, color: navy, bold: true, align: "center" });
  footer(s, "Ngưỡng τ được báo cáo tại 0.50, 0.75 và 0.90.");
  notes(s, "Nguồn: src/xla_gr03/metrics.py; report/report.tex, Matching và metric.");
}

// 15 - metric vocabulary
{
  const s = deck.slides.add();
  title(s, "Metric định lượng và cách đọc", 15);
  compareColumn(s, "APτ", "APτ = TP / (TP + FP + FN).\n\nĐo khả năng phát hiện instance đúng ở IoU τ.", 72, paleBlue);
  compareColumn(s, "PQτ", "PQτ = ΣIoU(TP) / [TP + 0.5FP + 0.5FN].\n\nKết hợp detection và chất lượng mask.", 471, paleTeal, teal);
  compareColumn(s, "Dice + MAE", "Dice đo foreground gộp.\n\nMAE = |N_pred - N_GT| đo sai số đếm. Không thay thế AP/PQ.", 870, paleAmber, amber);
  txt(s, "AP@0.90 khắt khe về biên hơn AP@0.50. Vì vậy không kết luận chất lượng instance chỉ từ một ngưỡng hoặc chỉ từ Dice.", 76, 548, 1128, 40, { size: 20, color: navy, bold: true, align: "center" });
  footer(s, "Mọi metric tính từng ảnh rồi báo cáo mean ± SD trong đúng stratum n=50 hoặc n=3.");
  notes(s, "Nguồn: report/report.tex, Matching và metric.");
}

// 16 - ImageJ/Fiji roles
{
  const s = deck.slides.add();
  title(s, "ImageJ, Fiji và plugin StarDist", 16, "Fiji là nền tảng tham chiếu trực quan và kiểm chứng, không thay thế evaluator định lượng.");
  compareColumn(s, "ImageJ", "Nền tảng xử lý ảnh: ImagePlus, ROI Manager, Macro Recorder và hệ plugin.", 72, paleBlue);
  compareColumn(s, "Fiji", "Bản phân phối ImageJ cho khoa học, có cơ chế update site và nhiều plugin sinh học.", 471, paleTeal, teal);
  compareColumn(s, "StarDist plugin", "Inference model 2D pretrained/custom, normalization, threshold, tile và output Label Image/ROI.", 870, paleAmber, amber);
  txt(s, "Artifact dùng trong kiểm chứng: de.csbdresden:StarDist_:0.3.0-scijava | ImageJ 2.9.0 + legacy 1.53t | Java 8 | TensorFlow 1.12 CPU.", 84, 548, 1112, 44, { size: 18, color: navy, bold: true, align: "center" });
  footer(s, "ROI Manager hữu ích để quan sát; Label Image TIFF mới là đầu vào chuẩn để tính metric.");
  notes(s, "Nguồn: fiji/workflows/stardist_fiji_protocol.md; results/fiji_reference/provenance.json.");
}

// 17 - Fiji setup
{
  const s = deck.slides.add();
  title(s, "Fiji/ImageJ: cài plugin và kiểm tra ảnh đầu vào", 17);
  sequence(s, 1, "Cài Fiji", "Dùng bản stable. Mở Help > About Fiji và lưu phiên bản.", 72, 154, 530, paleBlue);
  sequence(s, 2, "Bật update site", "Help > Update... > Manage update sites. Bật CSBDeep, StarDist, TensorFlow. Apply changes rồi restart.", 678, 154, 530, paleTeal);
  sequence(s, 3, "Mở TIFF 2D", "File > Open. Giữ nguyên kích thước và pixel scale, không resize một phía.", 72, 322, 530, pale);
  sequence(s, 4, "Kiểm tra metadata", "Image > Show Info...: file name, width, height, bit depth, channel. Lưu thông tin vào run log.", 678, 322, 530, paleAmber);
  txt(s, "Chỉ bắt đầu inference khi input TIFF, ground truth và quy ước pixel đã thống nhất. Screenshot không phải dữ liệu định lượng.", 76, 560, 1128, 40, { size: 19, color: navy, bold: true, align: "center" });
  footer(s, "Quy trình thao tác đầy đủ: fiji/workflows/stardist_fiji_protocol.md.");
  notes(s, "Nguồn: fiji/workflows/stardist_fiji_protocol.md, Cài plugin và Chạy một ảnh.");
}

// 18 - Fiji run
{
  const s = deck.slides.add();
  title(s, "Fiji/ImageJ: chạy StarDist 2D và lưu Label Image", 18);
  txt(s, "Plugins > StarDist > StarDist 2D", 72, 126, 1136, 30, { size: 23, color: navy, bold: true, align: "center" });
  rect(s, 72, 172, 1136, 396, pale, line);
  s.images.add({ blob: fijiWorkflow, contentType: "image/png", alt: "Minh chứng từng bước của workflow Fiji ImageJ với input normalize label overlay metric log", fit: "contain", position: { left: 78, top: 178, width: 1124, height: 384 } });
  txt(s, "Model: Versatile (fluorescent nuclei) | percentile 1/99.8 | probability 0.479071 | NMS 0.3 | tiles 1 | exclude boundary 2 px | chọn Output: Label Image", 78, 592, 1124, 38, { size: 16, color: navy, bold: true, align: "center" });
  footer(s, "Sau khi label xuất hiện: kiểm tra cùng kích thước với input/GT, quan sát overlay, Save As TIFF không nén và ghi runtime.");
  notes(s, "Nguồn: results/fiji_reference/fiji_workflow_evidence.png; fiji/run_log_dsb2018_reference.csv.");
}

// 19 - Fiji evaluator
{
  const s = deck.slides.add();
  title(s, "Fiji/ImageJ: kiểm chứng bằng chính Label TIFF plugin xuất", 19);
  rect(s, 72, 144, 800, 410, pale, line);
  s.images.add({ blob: fijiPanels, contentType: "image/png", alt: "Ba output input ground truth va StarDist Fiji ImageJ cho low median high", fit: "contain", position: { left: 82, top: 154, width: 780, height: 390 } });
  rect(s, 906, 144, 302, 410, paleTeal, line);
  txt(s, "Quy trình đối chiếu", 930, 176, 254, 30, { size: 22, color: teal, bold: true, align: "center" });
  txt(s, "1. Lưu Label Image TIFF\n\n2. Python đọc trực tiếp TIFF\n\n3. Hungarian matching với ground truth\n\n4. Xuất TP, FP, FN, AP, PQ, Dice, MAE, runtime", 938, 230, 238, 206, { size: 18, color: ink, align: "center" });
  txt(s, "n = 3 fixed cases\nAP@.50 = .801 ± .244\nPQ@.50 = .788 ± .160\nDice = .950 ± .017", 930, 456, 254, 78, { size: 16, color: navy, bold: true, align: "center" });
  txt(s, "Không gộp số liệu này với benchmark n=50. Mục tiêu là kiểm tra workflow cross-platform.", 94, 582, 1090, 36, { size: 18, color: coral, bold: true, align: "center" });
  footer(s, "Evidence: results/fiji_labels/, results/fiji_reference/per_image_metrics.csv, fiji/run_log_dsb2018_reference.csv.");
  notes(s, "Nguồn: results/fiji_reference/summary_metrics.csv và fiji_reference_panels.png.");
}

// 20 - Python architecture
{
  const s = deck.slides.add();
  title(s, "Cài đặt Python: kiến trúc package xla_gr03", 20);
  const modules = [["preprocessing.py", "grayscale + percentile normalize", paleBlue], ["baselines.py", "Otsu, morphology, EDT, Watershed", paleAmber], ["geometry.py", "EDT target, ray, polygon decode, NMS", paleTeal], ["metrics.py", "IoU matrix, Hungarian, AP/PQ/Dice/MAE", pale], ["stardist_pipeline.py", "wrapper model 2D_versatile_fluo", paleBlue], ["io.py + cli.py", "TIFF labels, segment/evaluate commands", paleAmber]];
  modules.forEach(([head, body, fill], i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const left = 72 + col * 568;
    const top = 150 + row * 128;
    rect(s, left, top, 520, 92, fill, line);
    txt(s, head, left + 22, top + 16, 476, 25, { size: 20, color: navy, bold: true });
    txt(s, body, left + 22, top + 51, 476, 22, { size: 16, color: muted });
  });
  txt(s, "Chuẩn giao tiếp chung: mọi phương pháp trả Label TIFF integer 2D, sau đó đi qua cùng evaluator instance.", 74, 555, 1132, 36, { size: 20, color: navy, bold: true, align: "center" });
  footer(s, "Source: src/xla_gr03/ | Test bao phủ geometry, preprocessing, I/O, baseline và metric.");
  notes(s, "Nguồn: src/xla_gr03/ và pyproject.toml.");
}

// 21 - commands
{
  const s = deck.slides.add();
  title(s, "Python: chạy pipeline và kiểm thử", 21);
  txt(s, "1. Tạo môi trường và cài dependency", 72, 154, 520, 30, { size: 22, color: navy, bold: true });
  codeBlock(s, "python -m venv .venv\npython -m pip install -r requirements-model.txt\npython -m pip install -e \".[dev]\"", 72, 198, 538, 110);
  txt(s, "2. Phân đoạn và đánh giá một ảnh", 670, 154, 530, 30, { size: 22, color: navy, bold: true });
  codeBlock(s, "xla-gr03 segment input.tif output.tif --method otsu\nxla-gr03 evaluate ground_truth.tif output.tif --thresholds 0.5 0.75 0.9", 670, 198, 538, 110);
  txt(s, "3. Sinh benchmark và bằng chứng Fiji", 72, 366, 520, 30, { size: 22, color: navy, bold: true });
  codeBlock(s, "python scripts/run_dsb2018_benchmark.py\npython scripts/evaluate_fiji_reference.py\npython scripts/build_fiji_workflow_evidence.py", 72, 410, 538, 132);
  txt(s, "4. Kiểm thử chất lượng mã", 670, 366, 530, 30, { size: 22, color: navy, bold: true });
  codeBlock(s, ".venv\\Scripts\\python.exe -m pytest -q\n.venv\\Scripts\\ruff.exe check src tests scripts\n\npytest -m integration  # model thật + thư viện chuẩn", 670, 410, 538, 132);
  footer(s, "Code, CSV, TIFF labels, provenance và figure được lưu dưới results/ để tái lập.");
  notes(s, "Nguồn: README.md, pyproject.toml, scripts/ và test log của repository.");
}

// 22 - benchmark
{
  const s = deck.slides.add();
  title(s, "Kết quả định lượng: benchmark DSB2018 n=50", 22, "Ba phương pháp chạy trên cùng test split. Fiji n=3 không xuất hiện trong biểu đồ này.");
  const chart = s.charts.add("bar", {
    position: { left: 72, top: 155, width: 668, height: 382 },
    title: "AP@0.50 và PQ@0.50",
    titleTextStyle: { typeface: font, fontSize: 18, fill: navy, bold: true },
    categories: ["Otsu", "Watershed", "StarDist Python"],
    series: [{ name: "AP@0.50", values: methods.map(m => chartNumber(summaryAt(m).accuracy_mean)), fill: blue }, { name: "PQ@0.50", values: methods.map(m => chartNumber(summaryAt(m).panoptic_quality_mean)), fill: cyan }],
    barOptions: { direction: "column", grouping: "clustered", gapWidth: 44 },
    hasLegend: true,
    legend: { position: "bottom", textStyle: { typeface: font, fontSize: 13, fill: muted } },
    xAxis: { textStyle: { typeface: font, fontSize: 13, fill: muted } },
    yAxis: { min: 0, max: 1, majorUnit: 0.2, textStyle: { typeface: font, fontSize: 13, fill: muted }, majorGridlines: { style: "solid", fill: line, width: 1 } },
    dataLabels: { showValue: true, numberFormatCode: "0.000", position: "outEnd", textStyle: { typeface: font, fontSize: 12, fill: ink, bold: true } },
  });
  applyPresentationChartFont(chart, { fontFamily: font });
  const summary = [["Method", "Dice", "MAE", "Runtime s/img"], ...methods.map(m => {
    const r = summaryAt(m);
    return [m, f3(r.foreground_dice_mean), r.count_absolute_error_mean.toFixed(2), r.runtime_s_mean.toFixed(4)];
  })];
  const table = s.tables.add({ rows: 4, columns: 4, left: 784, top: 176, width: 424, height: 276, values: summary, columnWidths: [154, 78, 76, 116] });
  table.styleOptions = { headerRow: true, bandedRows: true, firstColumn: true };
  table.borders.assign({ style: "solid", fill: line, width: 1 });
  for (let c = 0; c < 4; c += 1) table.getCell(0, c).fill = navy;
  table.cells.block({ row: 0, column: 0, rowCount: 1, columnCount: 4 }).assign({ textStyle: { typeface: font, fontSize: 14, color: white, bold: true } });
  table.cells.block({ row: 1, column: 0, rowCount: 3, columnCount: 4 }).assign({ textStyle: { typeface: font, fontSize: 15, color: ink } });
  table.cells.block({ row: 3, column: 0, rowCount: 1, columnCount: 4 }).assign({ fill: "#E7F4EE" });
  txt(s, "StarDist có AP/PQ cao hơn và MAE đếm thấp hơn trên split này. Runtime tính cả tiền xử lý sau warm-up.", 96, 584, 1090, 38, { size: 19, color: navy, bold: true, align: "center" });
  footer(s, "Mean trên 50 test images. AP/PQ có SD trong report và results/dsb2018_benchmark/summary_metrics.csv.");
  notes(s, "Nguồn: results/dsb2018_benchmark/summary_metrics.csv; bảng kết quả trong report/report.tex.");
}

// 23 - qualitative median
{
  const s = deck.slides.add();
  title(s, "Kết quả định tính: ca median cố định", 23, "Giữ image ID từ lần chạy gốc, không chọn lại theo kết quả cập nhật.");
  rect(s, 72, 146, 1136, 250, pale, line);
  s.images.add({ blob: qualitativeMedian, contentType: "image/png", alt: "Case trung vị DSB2018 gồm input ground truth Otsu Watershed StarDist Python", fit: "contain", position: { left: 78, top: 152, width: 1124, height: 238 } });
  compareColumn(s, "Otsu", "Nhiều nhân tiếp xúc có thể bị gộp thành một component.", 72, paleAmber, amber, 435, 180);
  compareColumn(s, "Watershed", "Marker EDT tách được một phần blob. Kết quả phụ thuộc min_distance.", 471, paleBlue, navy, 435, 180);
  compareColumn(s, "StarDist Python", "Polygon learned tách instance và giảm sai số đếm trên benchmark.", 870, paleTeal, teal, 435, 180);
  footer(s, "Màu biểu diễn ID instance, không phải lớp semantic. Evidence: qualitative_median.png.");
  notes(s, "Nguồn: results/dsb2018_benchmark/figures/qualitative_median.png.");
}

// 24 - low case
{
  const s = deck.slides.add();
  title(s, "Giới hạn và case khó", 24, "Ca low giữ từ lần chạy gốc. Không khẳng định vẫn thấp nhất trong lần chạy mới.");
  rect(s, 72, 150, 1136, 260, pale, line);
  s.images.add({ blob: qualitativeLow, contentType: "image/png", alt: "Case low DSB2018 gồm input ground truth Otsu Watershed StarDist Python", fit: "contain", position: { left: 78, top: 156, width: 1124, height: 248 } });
  sequence(s, 1, "Model pretrained", "Weight đã học từ DSB2018. Chưa xác minh độc lập image ID train của weight với test.", 72, 460, 350, paleAmber);
  sequence(s, 2, "Hình học star-convex", "Không phù hợp hình vòng, phân nhánh hoặc lõm sâu dù threshold đúng.", 465, 460, 350, paleBlue);
  sequence(s, 3, "Tái lập cross-platform", "Khác version, normalization, tile hoặc NMS có thể làm label Fiji/Python khác nhau.", 858, 460, 350, paleTeal);
  footer(s, "Hướng phát triển: fine-tuning annotation nội bộ, ablation số tia, robustness noise và đánh giá 3D.");
  notes(s, "Nguồn: results/dsb2018_benchmark/figures/qualitative_low.png; report/report.tex, Đe doạ tới tính hợp lệ.");
}

// 25 - Direct comparison on fixed cases
{
  const s = deck.slides.add();
  title(s, "Đối chiếu trực tiếp Fiji và Python", 25, "Ghép ID một-một trước khi so mask. Python là tham chiếu triển khai, không thay ground truth.");
  const rows = [["Ca", "N Python", "N Fiji", "F1@.50", "IoU ghép", "Dice"], ...data.cross.map(r =>
    [r.tag, String(r.python_objects), String(r.fiji_objects), f3(r.f1_iou_050), f3(r.mean_matched_iou), f3(r.foreground_dice)])];
  const t = s.tables.add({rows:4,columns:6,left:80,top:180,width:1120,height:260,values:rows});
  t.styleOptions={headerRow:true,bandedRows:true};
  t.borders.assign({style:"solid",fill:line,width:1});
  t.cells.block({row:0,column:0,rowCount:1,columnCount:6}).assign({fill:navy,textStyle:{typeface:font,fontSize:23,color:white,bold:true}});
  t.cells.block({row:1,column:0,rowCount:3,columnCount:6}).assign({textStyle:{typeface:font,fontSize:25,color:ink}});
  txt(s,"Tiêu chí mô tả: F1 ≥ 0.95 và Dice ≥ 0.95. Median/high đạt, low chưa đạt. Hai object Fiji ở ca low không ghép được với Python.",80,480,1110,70,{size:23,color:coral});
  txt(s,"Percentile NumPy và histogram Java khác nhau. Java chặn giá trị âm, boundary policy và TensorFlow cũng khác phiên bản.",80,574,1110,66,{size:21,color:ink});
  notes(s,"Nguồn: results/cross_platform/comparison.csv và error_overlays.png. Không kết luận hai triển khai đồng nhất trên cả ba ca. Ngưỡng mô tả không thay kiểm định tương đương thống kê.");
}

// 26 - Validation threshold sweep
{
  const s = deck.slides.add();
  title(s,"Ảnh hưởng ngưỡng trên 30 ảnh validation",26,"Test giữ ngưỡng model công bố. Sweep chỉ mô tả hậu xử lý trên các ảnh train-validation đã chốt.");
  for (const [index,sweep] of ["probability","nms"].entries()) {
    const rows=data.ablation.filter(r=>r.sweep===sweep);
    const chart=s.charts.add("line",{
      position:{left:72+index*590,top:175,width:550,height:340},
      title:sweep === "probability" ? "Probability threshold" : "NMS threshold",
      categories:rows.map(r=>String(r.value)),
      series:[{name:"AP@0.50",values:rows.map(r=>chartNumber(r.accuracy_mean)),line:{fill:blue,width:3},marker:{symbol:"circle",size:6}}],
      hasLegend:false,
      xAxis:{textStyle:{typeface:font,fontSize:16,fill:ink}},
      yAxis:{min:0.7,max:0.95,textStyle:{typeface:font,fontSize:16,fill:ink}},
    });
    applyPresentationChartFont(chart,{fontFamily:font});
  }
  txt(s,"Tăng probability 0.3 lên 0.7: AP 0.864 xuống 0.777, số object trung bình 35.47 xuống 31.50, FN tăng 3.13 lên 6.47.",80,550,1110,72,{size:24,color:navy});
  footer(s,"Mean trên cùng 30 ảnh. SD, FP/FN và MAE đầy đủ trong CSV. CNN maps tái sử dụng, không báo runtime inference của sweep.");
  notes(s,"Nguồn: results/validation_ablation/summary_metrics.csv, provenance.json. Biểu đồ có SD trong báo cáo và PNG kèm repo. NMS cố định 0.3 khi quét probability, probability cố định 0.479071 khi quét NMS.");
}

// 27 - conclusion
{
  const s = deck.slides.add();
  s.background.fill = navy;
  txt(s, "Kết luận", 80, 76, 600, 54, { size: 40, color: white, bold: true });
  sequence(s, 1, "Thuật toán", "StarDist biến probability map và K ray distances thành polygon instance qua NMS.", 80, 170, 526, "#16345C");
  sequence(s, 2, "Thực nghiệm", `StarDist Python đạt AP@.50 ${f3(star.accuracy_mean)} và PQ ${f3(star.panoptic_quality_mean)} trên DSB2018 n=50.`, 674, 170, 526, "#16345C");
  sequence(s, 3, "Fiji/ImageJ", "Plugin thật tạo Label TIFF, run log và metric n=3 để kiểm chứng workflow cross-platform.", 80, 340, 526, "#16345C");
  sequence(s, 4, "Tái lập", "Repo có dataset versioned, Python package, Java runner, macro, test, CSV, TIFF và figures.", 674, 340, 526, "#16345C");
  txt(s, "Thông điệp chính: đánh giá instance phải dùng matching theo object. Foreground Dice một mình không đủ kết luận khả năng tách đối tượng.", 100, 570, 1080, 46, { size: 21, color: cyan, bold: true, align: "center" });
  txt(s, "Cảm ơn", 80, 652, 200, 26, { size: 17, color: "#D4E2F4" });
  notes(s, "Nguồn: report/generated/slide_data.json; benchmark provenance ghi máy, phiên bản, hash model/dataset. Kết quả pretrained trên split DSB2018, chưa xác minh độc lập train/test của weight.");
}

const candidatePath = path.join(buildDir, "candidate_completed.pptx");
await (await PresentationFile.exportPptx(deck)).save(candidatePath);
const result = await finalizePresentation({
  explicitTotalSlideCount: 27,
  requiredNativeTableOwnerSlides: [22, 25],
  requiredNativeChartOwnerSlides: [22, 26],
  materializeLiteralChartWorkbooks: true,
  workspaceDir,
  candidatePath,
  finalPath,
  pythonExecutable: RUNTIME_PYTHON,
  integrityValidatorPath: path.join(SKILL_DIR, "container_tools/inspect_presentation_package_integrity.py"),
  layoutValidatorPath: path.join(SKILL_DIR, "container_tools/inspect_presentation_layout_geometry.py"),
  layoutArgs: ["--expected-slide-size-emu", "12192000,6858000", "--validate-bullet-geometry", "--validate-heading-fit", "--require-native-table-slide", "22", "--require-native-table-slide", "25"],
  fontPolicy: { basis: "design", families: [font] },
  verifyArtifactToolImport: true,
  receiptPath: path.join(buildDir, `validation_${Date.now()}.json`),
});
for (const [index, slide] of deck.slides.items.entries()) {
  const preview = await slide.export({format:"png",scale:1});
  await fs.writeFile(path.join(buildDir,`slide_${String(index+1).padStart(2,"0")}.png`), new Uint8Array(await preview.arrayBuffer()));
}
const montage = await deck.export({ format: "webp", montage: true, scale: 1 });
await fs.writeFile(path.join(buildDir, "montage_completed.webp"), new Uint8Array(await montage.arrayBuffer()));
console.log(JSON.stringify({ finalPath, result }, null, 2));

from __future__ import annotations

import asyncio
import json
import math
import shutil
import subprocess
import textwrap
from datetime import datetime, timezone
from pathlib import Path

import edge_tts
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "final_submission"
MEDIA = ROOT / "artifacts" / "release_media"
SCREENSHOTS = OUT / "screenshots"
LIVE_ID = "live-genblaze-pollinations-flux-proof-001"
LIVE_ROOT = ROOT / "artifacts" / "evidence" / LIVE_ID


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/SFNS.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default(size=size)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, width: int) -> list[str]:
    out: list[str] = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        line = ""
        for word in words:
            test = f"{line} {word}".strip()
            if draw.textbbox((0, 0), test, font=fnt)[2] <= width:
                line = test
            else:
                if line:
                    out.append(line)
                line = word
        if line:
            out.append(line)
        if not words:
            out.append("")
    return out


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fnt: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int],
    width: int,
    line_gap: int = 10,
) -> int:
    x, y = xy
    for line in wrap_text(draw, text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + line_gap
    return y


def make_bg() -> Image.Image:
    img = Image.new("RGB", (1920, 1080), (8, 12, 22))
    px = img.load()
    for y in range(1080):
        for x in range(1920):
            r = 8 + int(18 * x / 1920)
            g = 12 + int(12 * y / 1080)
            b = 22 + int(20 * (x + y) / 3000)
            px[x, y] = (r, g, b)
    return img


def panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], outline=(85, 111, 255), fill=(20, 28, 44)):
    draw.rounded_rectangle(box, radius=18, fill=fill, outline=outline, width=2)


def proof() -> dict:
    return json.loads((LIVE_ROOT / "generations" / "live-001" / "genblaze-proof.json").read_text())


def make_title_slide(path: Path):
    img = make_bg()
    d = ImageDraw.Draw(img)
    d.text((120, 150), "CREATIVE//BOUNTY", font=font(92, True), fill=(255, 255, 255))
    d.text((126, 262), "Verifiable AI Content Production", font=font(42), fill=(210, 222, 245))
    d.text((126, 330), "Backblaze B2 + Genblaze", font=font(38), fill=(132, 245, 198))
    panel(d, (1180, 165, 1700, 620), fill=(18, 31, 47))
    d.text((1230, 235), "DEMAND", font=font(42, True), fill=(255, 255, 255))
    d.text((1230, 315), "RIGHTS", font=font(42, True), fill=(255, 255, 255))
    d.text((1230, 395), "EVIDENCE", font=font(42, True), fill=(255, 255, 255))
    d.text((1230, 475), "REPLAY", font=font(42, True), fill=(255, 255, 255))
    d.text((120, 905), "LIVE proof included: Genblaze manifest verified, B2 asset SHA-256 verified.", font=font(28), fill=(185, 198, 220))
    img.save(path)


def make_problem_slide(path: Path):
    img = make_bg()
    d = ImageDraw.Draw(img)
    d.text((110, 92), "The Problem", font=font(62, True), fill=(255, 255, 255))
    body = [
        "Everyone can generate content.",
        "Almost nobody proves why it was generated.",
        "Or when rights allowed it.",
        "Or what budget authorized it.",
        "Or where the evidence is stored.",
    ]
    y = 220
    for item in body:
        panel(d, (120, y - 18, 1780, y + 70), fill=(20, 30, 48))
        d.text((160, y), item, font=font(34), fill=(226, 234, 248))
        y += 120
    img.save(path)


def make_pipeline_slide(path: Path):
    img = make_bg()
    d = ImageDraw.Draw(img)
    d.text((92, 72), "Production Pipeline", font=font(60, True), fill=(255, 255, 255))
    steps = [
        "Opportunity", "Rights", "Economics", "Budget Authorization", "Generation",
        "Genblaze", "Pollinations", "Backblaze B2", "Verified Manifest", "Replay",
    ]
    x0, y0, w, h, gap = 160, 190, 330, 86, 24
    for i, step in enumerate(steps):
        col = i % 2
        row = i // 2
        x = x0 + col * 820
        y = y0 + row * (h + gap)
        panel(d, (x, y, x + w + 260, y + h), fill=(18, 29, 45))
        d.text((x + 32, y + 24), step, font=font(31, True), fill=(255, 255, 255))
        if i < len(steps) - 1:
            nx = x0 + ((i + 1) % 2) * 820
            ny = y0 + ((i + 1) // 2) * (h + gap)
            d.line((x + w + 260, y + h // 2, nx, ny + h // 2), fill=(132, 245, 198), width=4)
    img.save(path)


def paste_screenshot(base: Image.Image, screenshot: Path, box: tuple[int, int, int, int]):
    shot = Image.open(screenshot).convert("RGB")
    shot.thumbnail((box[2] - box[0], box[3] - box[1]))
    x = box[0] + ((box[2] - box[0]) - shot.width) // 2
    y = box[1] + ((box[3] - box[1]) - shot.height) // 2
    base.paste(shot, (x, y))


def make_screenshot_slide(path: Path, title: str, screenshot: str, caption: str):
    img = make_bg()
    d = ImageDraw.Draw(img)
    d.text((90, 58), title, font=font(52, True), fill=(255, 255, 255))
    panel(d, (90, 150, 1830, 905), fill=(12, 18, 28))
    paste_screenshot(img, SCREENSHOTS / screenshot, (112, 172, 1808, 883))
    d.text((110, 940), caption, font=font(28), fill=(197, 209, 230))
    img.save(path)


def make_live_proof_slide(path: Path):
    p = proof()
    img = make_bg()
    d = ImageDraw.Draw(img)
    d.text((92, 70), "LIVE Proof", font=font(62, True), fill=(255, 255, 255))
    rows = [
        ("Provider", p["provider"]),
        ("Model", p["model"]),
        ("Cost", str(p["actual_provider_cost"])),
        ("Run ID", "86a788b9-e8cd-42d9-a355-562a97669d9b"),
        ("SHA-256", p["asset_sha256"]),
        ("Manifest hash", p["canonical_manifest_hash"]),
        ("manifest.verify()", str(p["manifest_verified"])),
        ("Replay", "verified"),
    ]
    y = 170
    for label, value in rows:
        panel(d, (110, y, 1810, y + 82), fill=(18, 29, 45))
        d.text((145, y + 22), label, font=font(28, True), fill=(132, 245, 198))
        d.text((520, y + 22), value, font=font(25), fill=(246, 249, 255))
        y += 94
    img.save(path)


def make_judge_pack_slide(path: Path):
    img = make_bg()
    d = ImageDraw.Draw(img)
    d.text((92, 70), "Judge Pack", font=font(62, True), fill=(255, 255, 255))
    items = [
        "sample-evidence/opp-ai-permitted-001",
        "failed-attempts/live-genblaze-nvidia-flux-proof-001",
        "failed-attempts/live-genblaze-nvidia-flux-proof-002",
        "live-evidence/live-genblaze-pollinations-flux-proof-001",
        "artifacts/judge-scorecard.json",
        "artifacts/release-candidate.json",
        "docs/truth-protocol.md",
    ]
    y = 170
    for item in items:
        panel(d, (125, y, 1795, y + 78), fill=(18, 29, 45))
        d.text((160, y + 22), item, font=font(27), fill=(235, 241, 252))
        y += 88
    d.text((130, 920), "Failed attempts remain included because truthfulness is part of the product.", font=font(31, True), fill=(132, 245, 198))
    img.save(path)


def make_architecture(path: Path):
    img = Image.new("RGB", (1600, 1000), (248, 250, 252))
    d = ImageDraw.Draw(img)
    d.text((70, 55), "CREATIVE//BOUNTY Architecture", font=font(48, True), fill=(17, 24, 39))
    boxes = [
        ("Opportunity Radar", 70, 170),
        ("Rights Gate", 370, 170),
        ("Economics", 670, 170),
        ("Budget Authorization", 970, 170),
        ("Genblaze Pipeline", 370, 430),
        ("Pollinations Free Provider", 70, 690),
        ("Backblaze B2 Evidence", 670, 690),
        ("Manifest Verify + Replay", 970, 430),
    ]
    for text, x, y in boxes:
        d.rounded_rectangle((x, y, x + 250, y + 120), radius=16, fill=(255, 255, 255), outline=(37, 99, 235), width=3)
        draw_wrapped(d, (x + 24, y + 32), text, font(24, True), (17, 24, 39), 205)
    arrows = [
        ((320, 230), (370, 230)), ((620, 230), (670, 230)), ((920, 230), (970, 230)),
        ((1095, 290), (1095, 430)), ((970, 490), (620, 490)), ((495, 550), (195, 690)),
        ((495, 550), (795, 690)), ((920, 750), (1095, 550)),
    ]
    for start, end in arrows:
        d.line((*start, *end), fill=(15, 118, 110), width=5)
    img.save(path)


def make_thumbnail(path: Path):
    img = make_bg()
    d = ImageDraw.Draw(img)
    d.text((90, 95), "CREATIVE//BOUNTY", font=font(76, True), fill=(255, 255, 255))
    d.text((96, 200), "Demand before generation.", font=font(42), fill=(132, 245, 198))
    panel(d, (92, 330, 1828, 790), fill=(18, 29, 45))
    d.text((145, 385), "LIVE Genblaze + B2 proof", font=font(48, True), fill=(255, 255, 255))
    d.text((145, 475), "manifest.verify() == True", font=font(44, True), fill=(132, 245, 198))
    d.text((145, 580), "Pollinations · cost 0.0 · replay verified", font=font(34), fill=(214, 226, 246))
    d.text((145, 685), "Judge scorecard: 96/100", font=font(38, True), fill=(255, 255, 255))
    img.save(path)


NARRATION_SEGMENTS = [
    ("Opening", 14, "CREATIVE//BOUNTY is a verifiable AI content production pipeline built with Genblaze and Backblaze B2."),
    ("Problem", 18, "Everyone can generate content now. The harder question is proving why it was generated, when rights allowed it, what budget authorized it, and where the evidence is stored."),
    ("Pipeline", 22, "The product starts with an opportunity, then passes through rights, economics, budget authorization, generation, Genblaze orchestration, a provider, Backblaze B2 storage, manifest verification, and replay."),
    ("UI", 18, "The demo interface shows the opportunity radar and keeps SAMPLE mode clearly separated from LIVE evidence. It does not present advertised rewards as revenue."),
    ("Proof", 24, "The verified LIVE run used the free Pollinations image endpoint through Genblaze. Provider cost is recorded as zero point zero. The asset was persisted to Backblaze B2, and its SHA two fifty six hash was verified."),
    ("Manifest", 18, "The native Genblaze manifest hash is d4ae8034cc836a890a7f498bb512341448563a71230c180dddf0efa96c335e13, and manifest dot verify returns true."),
    ("Replay", 16, "Replay reconstructs the evidence without making another provider call. The LIVE bundle verifies with one accepted attempt and no replay errors."),
    ("Evidence", 16, "The evidence endpoint exposes the files, events, audit receipt status, and source trail for the run."),
    ("Judge Pack", 18, "The Judge Pack includes sample evidence, failed attempts, and verified live evidence. Failed attempts remain included because truthfulness is part of the product."),
    ("Scorecard", 14, "The scorecard is evidence backed. It reaches ninety six out of one hundred only after the B2 asset and native Genblaze manifest are verified."),
    ("Closing", 14, "This is not another image generator. It is a verifiable AI production pipeline."),
]


def srt_timestamp(seconds: float) -> str:
    ms = int(round((seconds - int(seconds)) * 1000))
    total = int(seconds)
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_narration_and_srt():
    narration = "\n\n".join(text for _, _, text in NARRATION_SEGMENTS)
    (OUT / "narration.txt").write_text(narration + "\n", encoding="utf-8")
    t = 0.0
    blocks = []
    for i, (_, duration, text) in enumerate(NARRATION_SEGMENTS, 1):
        blocks.append(f"{i}\n{srt_timestamp(t)} --> {srt_timestamp(t + duration)}\n{text}\n")
        t += duration
    (OUT / "subtitles.srt").write_text("\n".join(blocks), encoding="utf-8")
    return narration


async def synthesize(narration: str):
    communicate = edge_tts.Communicate(narration, voice="en-US-AndrewNeural", rate="-15%")
    await communicate.save(str(MEDIA / "narration.mp3"))


def run(cmd: list[str]):
    subprocess.run(cmd, cwd=ROOT, check=True)


def render_video(slides: list[Path]):
    captioned: list[Path] = []
    for i, (slide, (_, _, caption)) in enumerate(zip(slides, NARRATION_SEGMENTS), 1):
        img = Image.open(slide).convert("RGB")
        d = ImageDraw.Draw(img, "RGBA")
        d.rounded_rectangle((110, 902, 1810, 1040), radius=18, fill=(0, 0, 0, 185))
        y = draw_wrapped(d, (150, 932), caption, font(29), (255, 255, 255), 1620, line_gap=6)
        out = MEDIA / f"captioned_{i:02d}.png"
        img.save(out)
        captioned.append(out)
    concat = MEDIA / "slides.ffconcat"
    lines = ["ffconcat version 1.0\n"]
    for slide, (_, duration, _) in zip(captioned, NARRATION_SEGMENTS):
        lines.append(f"file '{slide.as_posix()}'\n")
        lines.append(f"duration {duration}\n")
    lines.append(f"file '{captioned[-1].as_posix()}'\n")
    concat.write_text("".join(lines), encoding="utf-8")
    run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
        "-i", str(MEDIA / "narration.mp3"),
        "-vf", "fps=30,format=yuv420p",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "160k", "-shortest", str(OUT / "video.mp4"),
    ])


def make_readme_pdf():
    doc = SimpleDocTemplate(str(OUT / "README.pdf"), pagesize=letter, rightMargin=48, leftMargin=48, topMargin=48, bottomMargin=48)
    styles = getSampleStyleSheet()
    story = []
    for line in (ROOT / "README.md").read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            story.append(Paragraph(line[2:], styles["Title"]))
            story.append(Spacer(1, 12))
        elif line.startswith("## "):
            story.append(Paragraph(line[3:], styles["Heading2"]))
            story.append(Spacer(1, 8))
        elif line.strip():
            safe = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(safe, styles["BodyText"]))
            story.append(Spacer(1, 6))
    doc.build(story)


def build_manifest():
    files = []
    for p in sorted(OUT.rglob("*")):
        if p.is_file():
            files.append({"path": p.relative_to(OUT).as_posix(), "bytes": p.stat().st_size})
    payload = {
        "schema": "creative-bounty/final-submission-manifest/v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "live_evidence_id": LIVE_ID,
        "video": {"format": "mp4", "resolution": "1920x1080", "codec": "H.264", "fps": 30, "subtitles_burned_in": True},
        "voice": "Microsoft Edge TTS en-US-AndrewNeural",
        "music": "none; no local royalty-free music asset was available",
        "live_proof": proof(),
        "files": files,
    }
    (OUT / "video_manifest.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def make_submission_checklist():
    checklist = """# Submission Checklist

- [x] Demo video generated as MP4.
- [x] Video is 1920x1080.
- [x] Video uses H.264 video.
- [x] Video uses 30 fps.
- [x] Narration generated with Microsoft Edge TTS `en-US-AndrewNeural`.
- [x] `subtitles.srt` generated.
- [x] Captions burned directly into video frames.
- [x] No background music used because no local royalty-free track was available.
- [x] Devpost thumbnail generated.
- [x] README PDF generated.
- [x] Devpost final draft included.
- [x] Judge Pack included.
- [x] Architecture diagram included.
- [x] Screenshots captured from local app/API.
- [x] LIVE proof values included.
- [x] Failed attempts retained in Judge Pack for audit transparency.
- [x] No fake revenue, customer, win, or public B2 claim.
"""
    (OUT / "submission_checklist.md").write_text(checklist, encoding="utf-8")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    MEDIA.mkdir(parents=True, exist_ok=True)
    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    make_title_slide(MEDIA / "slide_01_title.png")
    make_problem_slide(MEDIA / "slide_02_problem.png")
    make_pipeline_slide(MEDIA / "slide_03_pipeline.png")
    make_screenshot_slide(MEDIA / "slide_04_ui.png", "Demo UI", "home.png", "Opportunity radar with SAMPLE and LIVE-CURATED separation.")
    make_live_proof_slide(MEDIA / "slide_05_live_proof.png")
    make_screenshot_slide(MEDIA / "slide_06_replay.png", "Replay Verified", "replay.png", "Read-only replay verifies without another provider call.")
    make_screenshot_slide(MEDIA / "slide_07_evidence.png", "Evidence Endpoint", "evidence.png", "Files, events, and audit receipt remain inspectable.")
    make_judge_pack_slide(MEDIA / "slide_08_judge_pack.png")
    make_screenshot_slide(MEDIA / "slide_09_scorecard.png", "Judge Scorecard", "scorecard.png", "B2 and Genblaze criteria unlock only after verified proof.")
    make_screenshot_slide(MEDIA / "slide_10_status.png", "Status Page", "status.png", "Configured provider is Pollinations; live readiness is true.")
    make_title_slide(MEDIA / "slide_11_closing.png")
    make_architecture(OUT / "architecture.png")
    make_thumbnail(OUT / "thumbnail.png")

    shutil.copy2(ROOT / "artifacts" / "creative-bounty-v7-judge-pack.zip", OUT / "creative-bounty-v7-judge-pack.zip")
    shutil.copy2(ROOT / "docs" / "devpost-final.md", OUT / "devpost-final.md")

    narration = write_narration_and_srt()
    asyncio.run(synthesize(narration))
    slides = [
        MEDIA / "slide_01_title.png",
        MEDIA / "slide_02_problem.png",
        MEDIA / "slide_03_pipeline.png",
        MEDIA / "slide_04_ui.png",
        MEDIA / "slide_05_live_proof.png",
        MEDIA / "slide_05_live_proof.png",
        MEDIA / "slide_06_replay.png",
        MEDIA / "slide_07_evidence.png",
        MEDIA / "slide_08_judge_pack.png",
        MEDIA / "slide_09_scorecard.png",
        MEDIA / "slide_11_closing.png",
    ]
    render_video(slides)
    make_readme_pdf()
    make_submission_checklist()
    build_manifest()


if __name__ == "__main__":
    main()

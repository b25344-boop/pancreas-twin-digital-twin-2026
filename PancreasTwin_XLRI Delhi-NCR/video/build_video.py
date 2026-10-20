"""
Build a narrated walkthrough video from the deck PDF and VIDEO_SCRIPT_20MIN.md.

Pipeline:
  1. Parse VIDEO_SCRIPT_20MIN.md: every "## " section is one segment. Lines starting with ">" are stage
     directions and are not spoken.
  2. Render each slide of Project_Pancreas_Twin_Deck.pdf to a 1920x1080 PNG (PyMuPDF). The "Live Demo"
     segment uses video/app_demo.png (a dashboard screenshot) when present, otherwise a generated title card.
  3. Synthesise each segment's narration (edge-tts, voice en-IN-PrabhatNeural; fallback Windows SAPI).
  4. ffmpeg each image + audio into an H.264/AAC segment, then concat into Pancreas_Twin_Walkthrough.mp4.

Usage (from anywhere):
  python video/build_video.py --words        # narration word count per segment and total
  python video/build_video.py --timecodes    # rewrite the [mm:ss - mm:ss] timecodes at 140 wpm
  python video/build_video.py                # build the video (needs ffmpeg and ffprobe on PATH)
"""

import argparse
import asyncio
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
SCRIPT = PROJECT / "VIDEO_SCRIPT_20MIN.md"
DECK_PDF = PROJECT / "Project_Pancreas_Twin_Deck.pdf"
WORK = HERE / "_build"
OUT = HERE / "Pancreas_Twin_Walkthrough.mp4"
DEMO_IMG = HERE / "app_demo.png"
VOICE = "en-IN-PrabhatNeural"
FALLBACK_VOICE = "en-US-GuyNeural"
WPM = 140
W, H, FPS = 1920, 1080, 15
LEAD_MS, TAIL_S = 700, 1.3  # silence before and after each segment's narration

HEADER = re.compile(r"^## (?P<title>.+?)(?: \[\d\d:\d\d - \d\d:\d\d\])?\s*$")


def parse_script():
    segments, cur = [], None
    for line in SCRIPT.read_text(encoding="utf-8").splitlines():
        m = HEADER.match(line)
        if m:
            cur = {"title": m.group("title").strip(), "lines": []}
            segments.append(cur)
            continue
        if cur is None:
            continue
        s = line.strip()
        if not s or s.startswith(">") or s == "---":
            continue
        cur["lines"].append(s)
    for seg in segments:
        seg["text"] = "\n\n".join(seg["lines"])
        seg["words"] = len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'.,-]*", seg["text"]))
        m = re.match(r"Slide (\d+):", seg["title"])
        seg["slide"] = int(m.group(1)) if m else None
    return segments


def fmt(sec):
    sec = int(round(sec))
    return f"{sec // 60:02d}:{sec % 60:02d}"


def rewrite_timecodes(segments):
    lines = SCRIPT.read_text(encoding="utf-8").splitlines()
    t, k = 0.0, 0
    for i, line in enumerate(lines):
        m = HEADER.match(line)
        if not m:
            continue
        dur = segments[k]["words"] / WPM * 60.0
        lines[i] = f"## {m.group('title').strip()} [{fmt(t)} - {fmt(t + dur)}]"
        t += dur
        k += 1
    SCRIPT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Timecodes rewritten. Spoken length at {WPM} wpm: {fmt(t)}")


def render_slides():
    import fitz
    WORK.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(DECK_PDF)
    paths = []
    for i, page in enumerate(doc):
        zoom = W / page.rect.width
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
        p = WORK / f"slide_{i + 1:02d}.png"
        pix.save(p)
        paths.append(p)
    return paths


def demo_card():
    if DEMO_IMG.exists():
        return DEMO_IMG
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGB", (W, H), (15, 32, 67))
    d = ImageDraw.Draw(img)
    try:
        big = ImageFont.truetype("arialbd.ttf", 72)
        small = ImageFont.truetype("arial.ttf", 40)
    except OSError:
        big = small = ImageFont.load_default()
    d.text((140, 420), "Live Demo: Streamlit Dashboard", fill=(255, 255, 255), font=big)
    d.text((140, 540), "streamlit run app.py", fill=(0, 168, 204), font=small)
    p = WORK / "demo_card.png"
    img.save(p)
    return p


async def _edge(text, out, voice):
    import edge_tts
    await edge_tts.Communicate(text, voice, rate="-4%").save(str(out))


def tts(text, out_base):
    """Return the path of an audio file for text. Tries edge-tts, then Windows SAPI."""
    mp3 = out_base.with_suffix(".mp3")
    if mp3.exists() and mp3.stat().st_size > 0:
        return mp3, "cached"
    for voice in (VOICE, FALLBACK_VOICE):
        try:
            asyncio.run(_edge(text, mp3, voice))
            if mp3.exists() and mp3.stat().st_size > 1000:
                return mp3, f"edge-tts {voice}"
        except Exception as exc:
            print(f"    edge-tts {voice} failed: {exc}")
    wav = out_base.with_suffix(".wav")
    txt = out_base.with_suffix(".txt")
    txt.write_text(text, encoding="utf-8")
    ps = (
        "Add-Type -AssemblyName System.Speech; "
        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.Rate = -1; "
        f"$s.SetOutputToWaveFile('{wav}'); "
        f"$s.Speak([IO.File]::ReadAllText('{txt}')); $s.Dispose()"
    )
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True)
    return wav, "Windows SAPI"


def duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout
    return float(json.loads(out)["format"]["duration"])


def make_segment(img, audio, out):
    vf = f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:white,format=yuv420p"
    af = f"adelay={LEAD_MS}|{LEAD_MS},apad=pad_dur={TAIL_S},aresample=48000"
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-loop", "1", "-framerate", str(FPS), "-i", str(img), "-i", str(audio),
         "-vf", vf, "-af", af, "-c:v", "libx264", "-preset", "veryfast", "-tune", "stillimage", "-crf", "20",
         "-r", str(FPS), "-c:a", "aac", "-b:a", "160k", "-ac", "2", "-shortest", "-movflags", "+faststart", str(out)],
        check=True,
    )


DEMO_CLIP = HERE / "demo_raw.webm"
DEMO_MARKS = HERE / "demo_marks.json"
DEMO_GAP_S = 0.6  # silence between demo paragraphs; must match record_demo.py GAP


def make_demo_segment(seg, out):
    """Live-demo segment from the real screen recording (record_demo.py), narrated paragraph by paragraph
    so each action on screen lines up with the sentence that describes it."""
    parts = []
    for k, text in enumerate(seg["lines"]):
        audio, _ = tts(text, WORK / f"demo_p{k}")
        parts.append(audio)
    inputs, filt = [], []
    for k, a in enumerate(parts):
        inputs += ["-i", str(a)]
        filt.append(f"[{k}:a]aresample=48000,apad=pad_dur={DEMO_GAP_S}[a{k}]")
    n = len(parts)
    filt.append("".join(f"[a{k}]" for k in range(n)) + f"concat=n={n}:v=0:a=1,adelay={LEAD_MS}|{LEAD_MS},apad=pad_dur={TAIL_S}[aout]")
    narr = WORK / "demo_narration.m4a"
    subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(filt), "-map", "[aout]",
                    "-c:a", "aac", "-b:a", "160k", "-ac", "2", str(narr)], check=True)
    dur = duration(narr)
    start = json.loads(DEMO_MARKS.read_text())["ready"]
    vf = f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:white,fps={FPS},format=yuv420p,tpad=stop_mode=clone:stop_duration=30"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{start:.2f}", "-i", str(DEMO_CLIP), "-i", str(narr),
                    "-map", "0:v", "-map", "1:a", "-vf", vf, "-t", f"{dur:.2f}", "-c:v", "libx264", "-preset", "veryfast",
                    "-crf", "20", "-r", str(FPS), "-c:a", "aac", "-b:a", "160k", "-ac", "2", "-movflags", "+faststart", str(out)],
                   check=True)
    return "screen recording + edge-tts per paragraph"


def build(segments):
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            sys.exit(f"{tool} not found on PATH")
    slides = render_slides()
    demo = demo_card()
    parts = []
    for i, seg in enumerate(segments, 1):
        part = WORK / f"seg_{i:02d}.mp4"
        if not seg["slide"] and DEMO_CLIP.exists() and DEMO_MARKS.exists():
            engine = make_demo_segment(seg, part)
        else:
            img = slides[seg["slide"] - 1] if seg["slide"] else demo
            audio, engine = tts(seg["text"], WORK / f"seg_{i:02d}")
            make_segment(img, audio, part)
        parts.append(part)
        print(f"  [{i:02d}] {seg['title'][:48]:48s} {seg['words']:4d} words  {duration(part):6.1f}s  ({engine})")
    lst = WORK / "concat.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy",
                    "-movflags", "+faststart", str(OUT)], check=True)
    total = duration(OUT)
    print(f"\nWrote {OUT} | duration {fmt(total)} ({total:.1f}s) | size {OUT.stat().st_size / 1e6:.1f} MB")
    return total


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--words", action="store_true")
    ap.add_argument("--timecodes", action="store_true")
    args = ap.parse_args()
    segments = parse_script()
    if args.words:
        for s in segments:
            print(f"{s['words']:5d}  {s['title']}")
        total = sum(s["words"] for s in segments)
        print(f"{total:5d}  TOTAL narration words ({total / WPM:.1f} min at {WPM} wpm)")
        return 0
    if args.timecodes:
        rewrite_timecodes(segments)
        return 0
    total = build(segments)
    return 0 if total >= 20 * 60 else 2


if __name__ == "__main__":
    sys.exit(main())

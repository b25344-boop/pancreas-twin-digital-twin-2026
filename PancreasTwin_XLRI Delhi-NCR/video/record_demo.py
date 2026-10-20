"""Record a real screen capture of the Streamlit dashboard for the video's live-demo segment.

Start the app first:  streamlit run app.py --server.headless true --server.port 8599
Then:                 python video/record_demo.py
Writes video/demo_raw.webm and video/demo_marks.json (seconds from recording start for each step).
build_video.py uses the clip, from the "ready" mark, for the "Live Demo" segment when it exists.
"""
import json
import shutil
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
URL = "http://localhost:8599"
PATIENT = "CGMACROS_CGMacros-005"
TARGET_IDX = 276  # glucose rising after a meal; the twin forecasts > 180 within the hour
LEAD, GAP = 0.7, 0.6  # must match build_video.py (LEAD_MS and the demo paragraph gap)


def main():
    marks = {}
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1600, "height": 900},
                                  record_video_dir=str(HERE / "_rec"), record_video_size={"width": 1600, "height": 900})
        t0 = time.time()
        page = ctx.new_page()
        mark = lambda k: marks.__setitem__(k, round(time.time() - t0, 2))
        page.goto(URL)
        page.get_by_text("Select Patient Twin").wait_for(timeout=180000)
        page.wait_for_timeout(6000)
        mark("ready")
        # Each narration paragraph gets a window of its spoken length plus GAP (see build_video.py demo audio).
        d = [x + GAP for x in json.loads((HERE / "demo_paras.json").read_text())]
        win = lambda k: marks["ready"] + LEAD + sum(d[:k])          # paragraph k starts here
        wait_until = lambda t: page.wait_for_timeout(max(0, (t - (time.time() - t0)) * 1000))

        # P1. Patient selector
        sb = page.locator("[data-testid='stSidebar']")
        wait_until(win(0) + 1.0)
        sb.locator("[data-testid=stSelectbox] [role=combobox]").click()
        page.wait_for_timeout(1200)
        page.get_by_role("option", name=PATIENT).click()
        mark("patient")

        # P2. Day scrubber: jump near the target, then step forward in visible increments
        wait_until(win(1) + 0.5)
        slider = sb.locator("[data-testid=stSlider] input")
        lo, hi = float(slider.get_attribute("min")), float(slider.get_attribute("max"))
        box = sb.locator("[data-testid=stSlider]").bounding_box()
        frac = (TARGET_IDX - 40 - lo) / (hi - lo)
        page.mouse.click(box["x"] + box["width"] * frac, box["y"] + box["height"] / 2)
        page.wait_for_timeout(2000)
        mark("scrub_start")
        for _ in range(60):
            cur = int(float(slider.input_value()))
            if cur == TARGET_IDX:
                break
            slider.focus()
            key = "ArrowRight" if cur < TARGET_IDX else "ArrowLeft"
            for _ in range(min(10, abs(TARGET_IDX - cur))):
                page.keyboard.press(key)
            page.wait_for_timeout(1500)
        marks["final_idx"] = int(float(slider.input_value()))

        # P3. Alert visible for the whole paragraph
        wait_until(win(2))
        mark("alert")

        # P4. What-if walk
        wait_until(win(3) + 1.5)
        sb.get_by_text("Simulate Intervention: 15-min Post-Meal Walk").click()
        mark("walk")

        # P5. Scorecard
        wait_until(win(4) + 0.5)
        main_area = page.locator("[data-testid='stMain']")
        for _ in range(12):
            main_area.hover()
            page.mouse.wheel(0, 450)
            page.wait_for_timeout(500)
        mark("scorecard")
        wait_until(win(5) + 3.0)
        mark("end")
        video = page.video
        ctx.close()
        browser.close()
        src = Path(video.path())
    shutil.move(str(src), HERE / "demo_raw.webm")
    shutil.rmtree(HERE / "_rec", ignore_errors=True)
    (HERE / "demo_marks.json").write_text(json.dumps(marks, indent=2))
    print(marks)


if __name__ == "__main__":
    main()

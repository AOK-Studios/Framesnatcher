import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def make_video(path):
    subprocess.run(
        ["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
         "testsrc=duration=6:size=320x240:rate=10", "-y", str(path)],
        check=True)


def test_extract(tmp_path):
    video = tmp_path / "sample.mp4"
    make_video(video)
    out = tmp_path / "frames"
    r = subprocess.run(
        [sys.executable, "-m", "framesnatcher.cli", "extract", str(video),
         "--at", "1,3", "--count", "2", "--out", str(out), "--json"],
        cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    manifest = json.loads((out / "manifest.json").read_text())
    assert manifest["count"] >= 3
    for frame in manifest["frames"]:
        assert (out / frame["file"]).exists()
        assert frame["width"] == 320 and frame["height"] == 240

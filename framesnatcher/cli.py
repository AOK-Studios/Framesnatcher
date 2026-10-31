"""frameSnatcher CLI. Agent friendly frame extraction from video, powered by ffmpeg."""
import argparse
import json
import subprocess
import sys
from pathlib import Path


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def probe(path):
    r = run(["ffprobe", "-v", "error", "-show_format", "-show_streams",
             "-of", "json", str(path)])
    if r.returncode != 0:
        raise SystemExit(f"ffprobe failed on {path}: {r.stderr.strip()}")
    data = json.loads(r.stdout)
    video = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
    if not video:
        raise SystemExit(f"no video stream found in {path}")
    fmt = data.get("format", {})
    return {
        "file": str(path),
        "duration_seconds": round(float(fmt.get("duration", 0)), 3),
        "width": video.get("width"),
        "height": video.get("height"),
        "codec": video.get("codec_name"),
        "fps": video.get("avg_frame_rate"),
    }


def parse_time(value):
    value = value.strip()
    if ":" in value:
        parts = [float(p) for p in value.split(":")]
        total = 0.0
        for p in parts:
            total = total * 60 + p
        return total
    return float(value)


def stamp(seconds):
    return f"{seconds:010.3f}".replace(".", "_")


def extract_one(video, seconds, out_file):
    r = run(["ffmpeg", "-v", "error", "-ss", f"{seconds:.3f}", "-i", str(video),
             "-frames:v", "1", "-q:v", "2", "-y", str(out_file)])
    return r.returncode == 0 and out_file.exists() and out_file.stat().st_size > 0


def scene_times(video, threshold, duration):
    cmd = ["ffmpeg", "-i", str(video), "-filter:v",
           f"select='gt(scene\\,{threshold})',showinfo", "-f", "null", "-"]
    r = run(cmd)
    times = []
    for line in r.stderr.splitlines():
        if "showinfo" in line and "pts_time:" in line:
            try:
                t = float(line.split("pts_time:")[1].split()[0])
                if 0 < t < duration:
                    times.append(round(t, 3))
            except (ValueError, IndexError):
                pass
    return sorted(set(times))


def cmd_probe(args):
    info = probe(Path(args.video))
    print(json.dumps(info, indent=2) if args.json else
          f"{info['file']}: {info['width']}x{info['height']}, "
          f"{info['duration_seconds']}s, {info['codec']}, fps {info['fps']}")
    return 0


def cmd_extract(args):
    video = Path(args.video)
    info = probe(video)
    duration = info["duration_seconds"]
    wanted = []  # list of (mode, seconds)
    if args.at:
        for raw in args.at.split(","):
            if raw.strip():
                wanted.append(("at", parse_time(raw)))
    if args.every:
        t = float(args.every)
        step = t
        while t < duration:
            wanted.append(("every", round(t, 3)))
            t += step
    if args.count:
        n = int(args.count)
        for i in range(n):
            t = duration * (i + 0.5) / n
            wanted.append(("sample", round(t, 3)))
    if args.scene is not None:
        for t in scene_times(video, float(args.scene), duration):
            wanted.append(("scene", t))
    if not wanted:
        print("nothing to do: give one of --at, --every, --count or --scene", file=sys.stderr)
        return 2
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    frames = []
    seen = set()
    for mode, seconds in sorted(wanted, key=lambda x: x[1]):
        key = round(seconds, 2)
        if key in seen:
            continue
        seen.add(key)
        name = f"frame_{stamp(seconds)}s_{mode}.png"
        target = out_dir / name
        if extract_one(video, seconds, target):
            frames.append({"file": name, "timestamp_seconds": round(seconds, 3),
                           "mode": mode, "width": info["width"], "height": info["height"]})
    manifest = {"source": info, "frames": frames, "count": len(frames)}
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    if args.json:
        print(json.dumps(manifest, indent=2))
    else:
        print(f"snatched {len(frames)} frame(s) into {out_dir}")
        for f in frames:
            print(f"  {f['file']}  at {f['timestamp_seconds']}s  ({f['mode']})")
    return 0 if frames else 1


def main(argv=None):
    p = argparse.ArgumentParser(prog="framesnatcher",
                                description="Snatch high resolution frames from video, built for agents.")
    sub = p.add_subparsers(dest="command", required=True)
    pp = sub.add_parser("probe", help="print video info")
    pp.add_argument("video")
    pp.add_argument("--json", action="store_true")
    pp.set_defaults(func=cmd_probe)
    pe = sub.add_parser("extract", help="extract frames")
    pe.add_argument("video")
    pe.add_argument("--at", help="comma separated timestamps, seconds or HH:MM:SS")
    pe.add_argument("--every", type=float, help="one frame every N seconds")
    pe.add_argument("--count", type=int, help="N frames spread evenly across the video")
    pe.add_argument("--scene", type=float, nargs="?", const=0.4,
                    help="frames where the scene changes (threshold, default 0.4)")
    pe.add_argument("--out", default="frames", help="output directory (default: frames)")
    pe.add_argument("--json", action="store_true", help="print the manifest as JSON")
    pe.set_defaults(func=cmd_extract)
    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

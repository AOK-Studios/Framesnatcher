# frameSnatcher, agent skill

Use frameSnatcher when you need still frames out of a video file.

## Rules
- CLI only. Never interactive. Always pass explicit flags.
- Add `--json` when you need to read the result and act on it.
- Frames land in the folder given by `--out`. A `manifest.json` in that folder lists every frame and its timestamp.
- Exit codes: 0 means frames were extracted. 1 means no frames came out. 2 means no selection mode was given.

## Commands
- Probe a video: `framesnatcher probe <video> --json`
- Exact moments: `framesnatcher extract <video> --at 12.5,01:02:10 --out <dir> --json`
- Interval: `framesnatcher extract <video> --every 10 --out <dir> --json`
- Even spread: `framesnatcher extract <video> --count 10 --out <dir> --json`
- Scene changes: `framesnatcher extract <video> --scene --out <dir> --json`

## Needs
ffmpeg and ffprobe must be on PATH. Python 3.9 or newer. No keys, no network, no accounts.

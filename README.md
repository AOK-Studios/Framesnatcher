# frameSnatcher

FrameSnatcher is an easy way to have your agent cut video. Use long form video and direct it to what you want to see. It scans through all the frames and only pulls out the ones you asked it to. That way you get high resolution frames you can actually use. A great collection of images for your projects, videos, images, anything.

CLI only. Built for agents. No prompts, no clicking around. You give it flags, it gives you frames and a manifest you can read.

## What you need

- Python 3.9 or newer
- ffmpeg and ffprobe on your PATH

That is it. No accounts, no keys, nothing hosted. It runs on your machine, on your files.

## Install

```sh
pip install .
```

Or just run it from the folder:

```sh
python -m framesnatcher.cli --help
```

## Use it

Look at a video first:

```sh
framesnatcher probe video.mp4 --json
```

Pull the exact moments you want:

```sh
framesnatcher extract video.mp4 --at 12.5,01:02:10 --out frames
```

One frame every 10 seconds:

```sh
framesnatcher extract video.mp4 --every 10 --out frames
```

Ten frames spread across the whole video:

```sh
framesnatcher extract video.mp4 --count 10 --out frames
```

Frames where the scene changes:

```sh
framesnatcher extract video.mp4 --scene --out frames
```

Mix them if you want. It sorts everything, skips duplicates and writes `manifest.json` next to the frames. Add `--json` and it prints the manifest too, so an agent can read the result and keep going.

## Output

Frames come out as PNG at the full resolution of the source video. File names carry the timestamp and how the frame was picked, like `frame_0000012_500s_at.png`.

`manifest.json` lists the source video info and every frame it snatched, with timestamps.

## License

MIT. See LICENSE.

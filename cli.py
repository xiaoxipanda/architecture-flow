"""Installed CLI; JSON stores render settings, not arbitrary graph layouts."""
import argparse
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
DEFAULTS = {"duration": 30, "fps": 30, "speed": 160, "spacing": 23, "music": "auto"}
KEYS = set(DEFAULTS) | {"ffmpeg", "atlas", "cn_font", "serif_font", "bold_font", "mono_font"}
PATH_KEYS = {"atlas", "cn_font", "serif_font", "bold_font", "mono_font"}

def run(name, arguments):
    subprocess.run([sys.executable, str(ROOT / "scripts" / name), *map(str, arguments)], check=True)

def settings(args):
    data = dict(DEFAULTS)
    if args.config:
        config_path = args.config.resolve()
        config = json.loads(config_path.read_text())
        if not isinstance(config, dict) or set(config) - KEYS:
            raise ValueError("Config must contain only documented render setting keys")
        for key in PATH_KEYS | {"music"}:
            value = config.get(key)
            if value is not None and not isinstance(value, str):
                raise ValueError(f"{key} must be a string")
            if value and value not in {"auto", "none"}:
                config[key] = str((config_path.parent / value).resolve())
        if "ffmpeg" in config and not isinstance(config["ffmpeg"], str):
            raise ValueError("ffmpeg must be an executable path or name")
        data.update(config)
    for key in KEYS:
        value = getattr(args, key, None)
        if value is not None:
            data[key] = value
    for key in ["duration", "speed", "spacing"]:
        value = data[key]
        if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
            raise ValueError(f"{key} must be a finite number")
    if data["duration"] <= 0 or data["speed"] < 0 or data["spacing"] <= 0:
        raise ValueError("duration/spacing must be positive; speed must be nonnegative")
    if type(data["fps"]) is not int or data["fps"] <= 0:
        raise ValueError("fps must be a positive integer")
    if not isinstance(data["music"], str):
        raise ValueError("music must be auto, none, or an audio file path")
    return data

def main():
    parser = argparse.ArgumentParser(description="Architecture videos: fixed nodes, flowing connectors, original music")
    parser.add_argument("--version", action="version", version="%(prog)s 0.2.0")
    commands = parser.add_subparsers(dest="command", required=True)
    render = commands.add_parser("render", help="Render the editable Hermes architecture template")
    render.add_argument("--out", type=Path, required=True)
    render.add_argument("--config", type=Path)
    for key in ["duration", "speed", "spacing"]:
        render.add_argument("--" + key, type=float)
    render.add_argument("--fps", type=int)
    render.add_argument("--music", help="auto (default), none, or audio file")
    render.add_argument("--ffmpeg")
    for key in PATH_KEYS:
        render.add_argument("--" + key.replace("_", "-"))
    render.add_argument("--poster-only", action="store_true")
    render.add_argument("--force", action="store_true", help="Allow overwriting this output and its assets")
    init = commands.add_parser("init", help="Write a sample render-settings JSON")
    init.add_argument("--out", type=Path, required=True)
    music = commands.add_parser("music", help="Generate original instrumental WAV")
    music.add_argument("--out", type=Path, required=True)
    music.add_argument("--duration", type=float, default=30)
    check = commands.add_parser("check", help="Validate format and decode all frames")
    check.add_argument("video", type=Path)
    check.add_argument("--ffmpeg", default=shutil.which("ffmpeg"))
    check.add_argument("--width", type=int, default=1080)
    check.add_argument("--height", type=int, default=1600)
    check.add_argument("--min-duration", type=float, default=1)
    args = parser.parse_args()
    try:
        if args.command == "init":
            if args.out.exists():
                raise ValueError("Config exists; choose a new path")
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(json.dumps(DEFAULTS, indent=2) + "\n")
            print(args.out.resolve())
        elif args.command == "music":
            if args.out.exists():
                raise ValueError("Music output exists; choose a new path")
            run("make_music.py", ["--output", args.out, "--duration", args.duration])
        elif args.command == "check":
            if not args.ffmpeg:
                raise ValueError("FFmpeg missing; supply --ffmpeg")
            run("validate_video.py", [args.video, "--ffmpeg", args.ffmpeg, "--width", args.width,
                                      "--height", args.height, "--min-duration", args.min_duration])
        else:
            data = settings(args)
            out = args.out.resolve()
            if out.suffix.lower() != ".mp4":
                raise ValueError("--out must end with .mp4")
            assets = out.with_name(out.stem + "-assets")
            if (out.exists() or assets.exists()) and not args.force:
                raise ValueError("Output or assets already exist; use a new path or --force")
            ffmpeg = data.get("ffmpeg") or shutil.which("ffmpeg")
            if not args.poster_only and not ffmpeg:
                raise ValueError("FFmpeg missing; install it or supply --ffmpeg")
            argv = ["--output-dir", assets]
            for key in ["duration", "fps", "speed", "spacing"]:
                argv += ["--" + key, data[key]]
            for key in PATH_KEYS:
                if data.get(key):
                    argv += ["--" + key.replace("_", "-"), data[key]]
            if ffmpeg:
                argv += ["--ffmpeg", ffmpeg]
            if args.poster_only:
                argv += ["--poster-only"]
            elif data["music"] == "auto":
                assets.mkdir(parents=True, exist_ok=True)
                audio = assets / "music.wav"
                run("make_music.py", ["--output", audio, "--duration", data["duration"]])
                argv += ["--music", audio]
            elif data["music"] != "none":
                audio = Path(data["music"]).resolve()
                if not audio.is_file():
                    raise ValueError(f"Music file not found: {audio}")
                argv += ["--music", audio]
            run("render_hermes_template.py", argv)
            if not args.poster_only:
                (assets / "architecture.mp4").replace(out)
                run("validate_video.py", [out, "--ffmpeg", ffmpeg, "--width", 1080,
                                          "--height", 1600, "--min-duration", max(.01, data["duration"] - .1)])
                print(f"Video: {out}")
            print(f"Cover and source frames: {assets}")
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Error: {error}\n")

if __name__ == "__main__":
    main()

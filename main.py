#!/usr/bin/env python3
"""YouTube Downloader - GUI por defecto, CLI con argumentos."""

import sys
import argparse
from pathlib import Path
from config import DEFAULT_OUTPUT_DIR, DEFAULT_QUALITY, QUALITY_MAP, Colors
from downloader import YouTubeDownloader


def format_size(size_bytes):
    if not size_bytes:
        return "?"
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f}TB"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode("ascii", "replace").decode("ascii"))


def progress_hook(d):
    if d["status"] == "downloading":
        downloaded = d.get("downloaded_bytes", 0)
        total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
        speed = d.get("speed", 0)
        if total > 0:
            pct = (downloaded / total) * 100
            bar_len = 30
            filled = int(bar_len * pct / 100)
            bar = "#" * filled + "-" * (bar_len - filled)
            spd = f"{format_size(speed)}/s" if speed else "?"
            print(f"\r[{bar}] {pct:.1f}% {format_size(downloaded)}/{format_size(total)} @ {spd}  ", end="", flush=True)
    elif d["status"] == "finished":
        print("\n[OK] Fusionando...")


def cli_main():
    parser = argparse.ArgumentParser(description="YouTube Downloader")
    parser.add_argument("url", nargs="?", help="URL de YouTube")
    parser.add_argument("-q", "--quality", default=DEFAULT_QUALITY, choices=list(QUALITY_MAP.keys()))
    parser.add_argument("-o", "--output", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("-a", "--audio-only", action="store_true")
    args = parser.parse_args()

    if not args.url:
        parser.print_help()
        return 1

    if "youtube.com" not in args.url and "youtu.be" not in args.url:
        print("Error: URL no es de YouTube")
        return 1

    dl = YouTubeDownloader(output_dir=args.output, quality=args.quality, progress_hook=progress_hook)
    result = dl.download(args.url, audio_only=args.audio_only)

    if result:
        title = result["title"] or "video"
        filepath = str(result["filepath"]) or "?"
        print(f"\n[OK] Descarga exitosa!")
        safe_print(f"  Titulo: {title}")
        safe_print(f"  Archivo: {filepath}")
        return 0
    else:
        print(f"\n[ERROR] {dl.last_error}")
        return 1


if __name__ == "__main__":
    try:
        if len(sys.argv) > 1:
            sys.exit(cli_main())
        else:
            from gui import run
            run()
    except KeyboardInterrupt:
        print("\nCancelado")
        sys.exit(130)

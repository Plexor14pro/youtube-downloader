import json
import os
import subprocess
import yt_dlp
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from config import DEFAULT_OUTPUT_DIR, DEFAULT_QUALITY, QUALITY_MAP, Colors


class YouTubeDownloader:
    def __init__(
        self,
        output_dir: Optional[Path] = None,
        quality: str = DEFAULT_QUALITY,
        progress_hook: Optional[Callable] = None,
    ):
        self.output_dir = output_dir or DEFAULT_OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.quality = quality
        self.progress_hook = progress_hook
        self.last_error = None

    @staticmethod
    def _verify_file(filepath: str) -> Dict[str, Any]:
        """Verifica que el archivo MP4 tenga video y audio usando ffprobe."""
        result = {"valid": False, "has_video": False, "has_audio": False, "error": None}
        ffmpeg_bin = None
        for p in os.environ.get("PATH", "").split(";"):
            probe = os.path.join(p, "ffprobe.exe")
            if os.path.isfile(probe):
                ffmpeg_bin = p
                break

        if not ffmpeg_bin:
            result["error"] = "ffprobe no encontrado en PATH"
            return result

        ffprobe = os.path.join(ffmpeg_bin, "ffprobe.exe")
        try:
            proc = subprocess.run(
                [ffprobe, "-v", "quiet", "-show_streams", "-print_format", "json", filepath],
                capture_output=True, text=True, timeout=30,
            )
            probe = json.loads(proc.stdout)
            streams = probe.get("streams", [])
            result["has_video"] = any(s.get("codec_type") == "video" for s in streams)
            result["has_audio"] = any(s.get("codec_type") == "audio" for s in streams)
            result["valid"] = result["has_video"] and result["has_audio"]
            if not result["valid"]:
                missing = []
                if not result["has_video"]:
                    missing.append("video")
                if not result["has_audio"]:
                    missing.append("audio")
                result["error"] = f"Archivo sin {' y '.join(missing)}"
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
            result["error"] = str(e)

        return result

    def _build_opts(self, audio_only: bool = False) -> dict:
        """Construye las opciones de yt-dlp."""
        if audio_only:
            fmt = "bestaudio[ext=m4a]/bestaudio"
        else:
            fmt = QUALITY_MAP.get(self.quality, QUALITY_MAP[DEFAULT_QUALITY])

        opts = {
            "format": fmt,
            "merge_output_format": "mp4",
            "outtmpl": str(self.output_dir / "%(title)s.%(ext)s"),
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "retries": 5,
            "fragment_retries": 5,
            "socket_timeout": 30,
            "nocheckcertificate": True,
            "progress_hooks": [self._on_progress] if self.progress_hook else [],
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            },
        }

        if audio_only:
            opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "m4a",
                "preferredquality": "192",
            }]

        return opts

    def _on_progress(self, d: Dict[str, Any]) -> None:
        if self.progress_hook:
            self.progress_hook(d)

    def download(self, url: str, audio_only: bool = False) -> Optional[Dict[str, Any]]:
        """Descarga un video de YouTube. Retorna dict con info o None."""
        self.last_error = None
        opts = self._build_opts(audio_only)

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if info:
                    filepath = ydl.prepare_filename(info)
                    # Check if merged to .mp4
                    if not os.path.exists(filepath):
                        filepath = filepath.rsplit(".", 1)[0] + ".mp4"

                    result = {
                        "title": info.get("title"),
                        "filepath": filepath,
                        "duration": info.get("duration"),
                        "uploader": info.get("uploader"),
                    }

                    # Verify audio+video if not audio_only
                    if not audio_only and os.path.isfile(filepath):
                        verification = self._verify_file(filepath)
                        if not verification["valid"]:
                            self.last_error = verification.get("error", "Archivo invalido")
                            return None

                    return result
                return None
        except yt_dlp.utils.DownloadError as e:
            self.last_error = f"Error de descarga: {e}"
        except Exception as e:
            self.last_error = f"Error inesperado: {e}"
        return None

    def list_formats(self, url: str) -> list:
        """Lista formatos disponibles."""
        opts = {"quiet": True, "no_warnings": True, "skip_download": True}
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info.get("formats", [])
        except Exception as e:
            self.last_error = str(e)
            return []

    def get_info(self, url: str) -> Optional[Dict[str, Any]]:
        """Obtiene info del video sin descargar."""
        opts = {"quiet": True, "no_warnings": True, "skip_download": True}
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    "title": info.get("title"),
                    "duration": info.get("duration"),
                    "uploader": info.get("uploader"),
                    "view_count": info.get("view_count"),
                }
        except Exception as e:
            self.last_error = str(e)
            return None

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
        else:
            opts["postprocessors"] = [{
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4",
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
                    return {
                        "title": info.get("title"),
                        "filepath": ydl.prepare_filename(info),
                        "duration": info.get("duration"),
                        "uploader": info.get("uploader"),
                    }
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

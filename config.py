import os
import sys
from pathlib import Path

# Agregar rutas de deno y ffmpeg al PATH (necesario en Windows)
_WINGET_PATHS = [
    r"C:\Users\LENOVO\AppData\Local\Microsoft\WinGet\Packages\DenoLand.Deno_Microsoft.Winget.Source_8wekyb3d8bbwe",
    r"C:\Users\LENOVO\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.2-full_build\bin",
]
for p in _WINGET_PATHS:
    if os.path.isdir(p) and p not in os.environ.get("PATH", ""):
        os.environ["PATH"] = p + ";" + os.environ.get("PATH", "")

# Configuracion por defecto
DEFAULT_OUTPUT_DIR = Path.home() / "Downloads" / "YouTube"
DEFAULT_QUALITY = "480p"

# Mapa de formatos por calidad
# Prioridad: bestvideo+bestaudio para garantizar merge correcto con ffmpeg
# Format 18 = 360p single-stream (fallback universal)
QUALITY_MAP = {
    "2160p": "bestvideo[height<=2160][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=2160]+bestaudio/best",
    "1440p": "bestvideo[height<=1440][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1440]+bestaudio/best",
    "1080p": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best",
    "720p":  "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best",
    "480p":  "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=480]+bestaudio/best",
    "360p":  "18/best[height<=360][ext=mp4]/best",
    "audio": "bestaudio[ext=m4a]/bestaudio",
}

# Colores ANSI
class Colors:
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    END = "\033[0m"
    BOLD = "\033[1m"

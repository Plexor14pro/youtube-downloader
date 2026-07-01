# YouTube Downloader

Descargador de videos de YouTube con interfaz grafica (GUI) y linea de comandos (CLI). Escrito en Python con `yt-dlp`.

## Caracteristicas

- Interfaz grafica intuitiva con Tkinter
- Descarga videos en MP4 con calidad seleccionable (2160p a 360p)
- Solo audio (M4A)
- Barra de progreso en tiempo real
- Compatible con Windows, Linux y macOS

## Instalacion

```bash
git clone https://github.com/Plexor14pro/youtube-downloader.git
cd youtube-downloader
pip install -r requirements.txt
```

### Requisitos

- **Python 3.8+**
- **FFmpeg** - Para fusionar video y audio
- **Deno** (opcional) - Para resolver challenges JS de YouTube

## Uso

### Interfaz grafica (GUI)

```bash
python main.py
```

### Linea de comandos (CLI)

```bash
python main.py "https://youtube.com/watch?v=VIDEO_ID"
python main.py "https://youtube.com/watch?v=VIDEO_ID" -q 720p
python main.py "https://youtube.com/watch?v=VIDEO_ID" -a
```

| Opcion | Descripcion |
|--------|-------------|
| `-q` | Calidad: 2160p, 1440p, 1080p, 720p, 480p, 360p, audio |
| `-a` | Solo audio (M4A) |
| `-o` | Carpeta de salida |

## Screenshot

```
+------------------------------------------+
|         YouTube Downloader               |
|                                          |
|  URL: [________________________]         |
|  Calidad: [480p v]   [ ] Solo audio     |
|  Guardar en: [~/Downloads/YouTube] [Browse]|
|                                          |
|  [======== DESCARGAR ===========]        |
|  [####################--------] 78.3%   |
|                                          |
|  [OK] Mi video favorito                  |
+------------------------------------------+
```

## Licencia

MIT License

## Creado por

Desarrollado por **@panarabe14** en X (Twitter).

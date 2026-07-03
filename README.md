<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-0078D4?style=for-the-badge" alt="Platform"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License"/>
</p>

<h1 align="center">YouTube Downloader</h1>

<p align="center">
  Download YouTube videos with a clean GUI or via CLI. Built in Python.
</p>

---

### About

A lightweight desktop application that allows you to download YouTube videos quickly. Supports both a graphical interface (Tkinter) and a command-line interface for power users.

### Features

- Download videos in multiple resolutions
- GUI interface for easy use
- CLI mode for automation
- Progress tracking
- Cross-platform (Windows, Linux, macOS)

### Tech Stack

- **Python 3.x**
- **Tkinter** — GUI framework
- **yt-dlp** — Video extraction

### Installation

```bash
# Clone the repository
git clone https://github.com/Plexor14pro/youtube-downloader.git

# Navigate to the directory
cd youtube-downloader

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Usage

**GUI Mode:**
```bash
python main.py
```

**CLI Mode:**
```bash
python main.py --url "https://youtube.com/watch?v=..." --quality 720
```

### Roadmap

- [ ] Playlist download support
- [ ] Audio-only extraction
- [ ] Download queue
- [ ] Quality selection menu

### License

Distributed under the MIT License. See `LICENSE` for more information.

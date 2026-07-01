import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import queue
from pathlib import Path
from config import DEFAULT_OUTPUT_DIR, DEFAULT_QUALITY, QUALITY_MAP
from downloader import YouTubeDownloader


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YouTube Downloader")
        self.geometry("620x520")
        self.resizable(False, False)
        self.configure(bg="#1e1e2e")
        self.msg_queue = queue.Queue()
        self.downloading = False
        self._build_ui()
        self._poll_queue()

    def _build_ui(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TLabel", background="#1e1e2e", foreground="#cdd6f4", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
        style.configure("TCheckbutton", background="#1e1e2e", foreground="#cdd6f4", font=("Segoe UI", 10))
        style.configure("TCombobox", font=("Segoe UI", 10))
        style.configure("Accent.TButton", font=("Segoe UI", 12, "bold"), padding=10)
        style.configure("Horizontal.TProgressbar", troughcolor="#313244", background="#89b4fa")

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        # Title
        ttk.Label(frame, text="YouTube Downloader", font=("Segoe UI", 16, "bold"), foreground="#89b4fa").pack(pady=(0, 15))

        # URL
        ttk.Label(frame, text="URL del video:").pack(anchor="w")
        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(frame, textvariable=self.url_var, font=("Segoe UI", 11))
        url_entry.pack(fill="x", pady=(2, 10))
        url_entry.insert(0, "Pega el link de YouTube aqui...")
        url_entry.bind("<FocusIn>", lambda e: self._clear_placeholder(url_entry))
        url_entry.bind("<FocusOut>", lambda e: self._add_placeholder(url_entry))

        # Quality + Audio
        opts_frame = ttk.Frame(frame)
        opts_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(opts_frame, text="Calidad:").pack(side="left")
        self.quality_var = tk.StringVar(value=DEFAULT_QUALITY)
        q_combo = ttk.Combobox(opts_frame, textvariable=self.quality_var, values=list(QUALITY_MAP.keys()),
                               state="readonly", width=10)
        q_combo.pack(side="left", padx=(5, 20))

        self.audio_var = tk.BooleanVar()
        ttk.Checkbutton(opts_frame, text="Solo audio (M4A)", variable=self.audio_var).pack(side="left")

        # Output folder
        out_frame = ttk.Frame(frame)
        out_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(out_frame, text="Guardar en:").pack(side="left")
        self.output_var = tk.StringVar(value=str(DEFAULT_OUTPUT_DIR))
        ttk.Entry(out_frame, textvariable=self.output_var, font=("Segoe UI", 9)).pack(side="left", fill="x", expand=True, padx=(5, 5))
        ttk.Button(out_frame, text="Examinar", command=self._browse).pack(side="right")

        # Download button
        self.dl_btn = ttk.Button(frame, text="DESCARGAR", style="Accent.TButton", command=self._start_download)
        self.dl_btn.pack(fill="x", pady=(5, 10))

        # Progress
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(frame, variable=self.progress_var, maximum=100, style="Horizontal.TProgressbar")
        self.progress_bar.pack(fill="x", pady=(0, 5))

        self.status_var = tk.StringVar(value="Listo")
        ttk.Label(frame, textvariable=self.status_var, font=("Segoe UI", 9), foreground="#a6adc8").pack(anchor="w")

        # Log area
        self.log_text = tk.Text(frame, height=8, bg="#181825", fg="#cdd6f4", font=("Consolas", 9),
                                state="disabled", wrap="word", relief="flat", bd=0)
        self.log_text.pack(fill="both", expand=True, pady=(10, 0))

    def _clear_placeholder(self, entry):
        if entry.get() == "Pega el link de YouTube aqui...":
            entry.delete(0, "end")

    def _add_placeholder(self, entry):
        if not entry.get():
            entry.insert(0, "Pega el link de YouTube aqui...")

    def _browse(self):
        folder = filedialog.askdirectory(initialdir=self.output_var.get())
        if folder:
            self.output_var.set(folder)

    def _log(self, msg):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _poll_queue(self):
        try:
            while True:
                kind, data = self.msg_queue.get_nowait()
                if kind == "log":
                    self._log(data)
                elif kind == "status":
                    self.status_var.set(data)
                elif kind == "progress":
                    self.progress_var.set(data)
                elif kind == "done":
                    self.downloading = False
                    self.dl_btn.configure(state="normal")
        except queue.Empty:
            pass
        self.after(100, self._poll_queue)

    def _start_download(self):
        url = self.url_var.get().strip()
        if not url or url == "Pega el link de YouTube aqui...":
            messagebox.showwarning("Aviso", "Pega un link de YouTube primero")
            return
        if "youtube.com" not in url and "youtu.be" not in url:
            messagebox.showerror("Error", "La URL no parece ser de YouTube")
            return
        if self.downloading:
            return

        self.downloading = True
        self.dl_btn.configure(state="disabled")
        self.progress_var.set(0)
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

        output = Path(self.output_var.get())
        quality = self.quality_var.get()
        audio_only = self.audio_var.get()

        threading.Thread(target=self._download_worker, args=(url, output, quality, audio_only), daemon=True).start()

    def _download_worker(self, url, output, quality, audio_only):
        q = self.msg_queue

        def hook(d):
            if d["status"] == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
                downloaded = d.get("downloaded_bytes", 0)
                if total > 0:
                    pct = (downloaded / total) * 100
                    q.put(("progress", pct))
                    q.put(("status", f"Descargando... {pct:.1f}%"))
            elif d["status"] == "finished":
                q.put(("status", "Fusionando formatos..."))
                q.put(("progress", 100))

        dl = YouTubeDownloader(output_dir=output, quality=quality, progress_hook=hook)
        q.put(("log", f"URL: {url}"))
        q.put(("log", f"Calidad: {quality}"))
        q.put(("status", "Iniciando descarga..."))

        result = dl.download(url, audio_only=audio_only)

        if result:
            title = result.get("title", "?")
            filepath = str(result.get("filepath", "?"))
            q.put(("log", f"[OK] {title}"))
            q.put(("log", f"Guardado: {filepath}"))
            q.put(("status", "Descarga completada!"))
            q.put(("progress", 100))
        else:
            err = dl.last_error or "Error desconocido"
            q.put(("log", f"[ERROR] {err}"))
            q.put(("status", "Error en la descarga"))

        q.put(("done", None))


def run():
    app = App()
    app.mainloop()

# ###################################################################
#           🎯 Projeto: Baixar Vídeo do X/Twitter (Dia 11)          #
# ###################################################################
# 📁 Caminho: dia-11/dia11_x_downloader.py
# Desafio 30 dias com Python por Victor Beal
# ###################################################################
# 📚 Bibliotecas: yt-dlp (baixar conteúdo)
# 🔗 Instalação: pip install yt-dlp
# ###################################################################
import os
import threading
import queue
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from yt_dlp import YoutubeDL

ROOT = os.path.dirname(__file__)
TARGET_DIR = os.path.join(ROOT, 'downloaded')
os.makedirs(TARGET_DIR, exist_ok=True)


def download_worker(url, result_q):
    opts = {
        'outtmpl': os.path.join(TARGET_DIR, '%(upload_date)s_%(id)s.%(ext)s'),
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'writethumbnail': False,
        'writeinfojson': False,
        'nocheckcertificate': True,
        'quiet': True,
        'progress_hooks': [lambda d: None],
    }
    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            fn = ydl.prepare_filename(info)
            result_q.put((True, {'file': fn, 'info': info}))
    except Exception as e:
        result_q.put((False, str(e)))


class App:
    def __init__(self, root):
        self.root = root
        root.title('Dia 11 — X / Twitter Video Downloader')
        root.geometry('600x200')

        top = tk.Frame(root)
        top.pack(fill='x', padx=8, pady=8)
        tk.Label(top, text='URL do Tweet/X:').pack(side='left')
        self.entry = tk.Entry(top, width=60)
        self.entry.pack(side='left', padx=6)
        self.btn = tk.Button(top, text='Download', command=self.start_download)
        self.btn.pack(side='left')

        self.progress = ttk.Progressbar(root, mode='indeterminate')
        self.progress.pack(fill='x', padx=8)
        self.status = tk.Label(root, text='Aguardando ação...')
        self.status.pack(fill='x', padx=8, pady=(4, 8))

        self.result_q = queue.Queue()

    def start_download(self):
        url = self.entry.get().strip()
        if not url:
            messagebox.showwarning('Aviso', 'Informe a URL do post/Tweet')
            return
        self.progress.start(10)
        self.status.config(text='Baixando...')
        self.btn.config(state='disabled')
        t = threading.Thread(target=download_worker, args=(url, self.result_q), daemon=True)
        t.start()
        self.root.after(200, self.check_result)

    def check_result(self):
        try:
            ok, data = self.result_q.get_nowait()
        except queue.Empty:
            self.root.after(200, self.check_result)
            return
        self.progress.stop()
        self.btn.config(state='normal')
        if not ok:
            messagebox.showerror('Erro', f'Erro ao baixar: {data}')
            self.status.config(text='Erro durante o download')
            return
        # OK: show location
        filepath = data['file']
        self.status.config(text=f'Download concluído: {os.path.basename(filepath)}')
        messagebox.showinfo('Concluído', f'Arquivo salvo em:\n{filepath}')
        self.entry.delete(0, 'end')


if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()

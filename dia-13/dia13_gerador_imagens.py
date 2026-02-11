# ###################################################################
#           🎯 Projeto: Gerador de Imagens (Dia 13)                 #
# ###################################################################
# 📁 Caminho: dia-13/dia13_gerador_imagens.py
# Desafio 30 dias com Python por Victor Beal
# ###################################################################
# 📚 Bibliotecas: requests, Pillow, tkinter, python-dotenv
# 🔗 Instalação: pip install requests Pillow python-dotenv
# ###################################################################
# API: https://api.openai.com/v1/images/generations
# Como usar:
# 1) Copie `.env.example` para `.env` dentro de dia-13/ e defina 
#       `OPENAI_KEY` (obrigatório) e `OPENAI_IMAGE_MODEL` (opcional, padrão gpt-image-1).
# 2) Execute: python dia-13/dia13_gerador_imagens.py
# ###################################################################

import os
import io
import time
import threading
import queue
from datetime import datetime
import base64
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
import requests
from dotenv import load_dotenv

# Carrega .env local
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

OUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUT_DIR, exist_ok=True)

OPENAI_IMAGE_MODEL = os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-1")

REQUESTED_API_SIZE = {
    "512x512": "1024x1024",
    "1024x1024": "1024x1024",
    "1024x1536": "1024x1536",
    "1536x1024": "1536x1024",
    "auto": "auto",
}

class ImageGeneratorApp:
    def __init__(self, root):
        # Overlay de carregando
        self.loading_overlay = None
        self.root = root
        root.title("Dia 13 — Gerador de Imagens com Inteligência Artificial")

        self.root.minsize(650, 520)
        main = ttk.Frame(root, padding=12)
        main.pack(fill=tk.BOTH, expand=True)

        row = 0
        ttk.Label(main, text="Prompt:").grid(column=0, row=row, sticky=tk.W)
        self.prompt_entry = tk.Text(main, width=64, height=4, wrap=tk.WORD)
        self.prompt_entry.insert("1.0", "Uma paisagem surreal, pôr do sol vibrante")
        self.prompt_entry.grid(column=1, row=row, columnspan=3, sticky=tk.W)

        row += 1
        ttk.Label(main, text="Tamanho:").grid(column=0, row=row, sticky=tk.W)
        # Adiciona opção de tamanho menor para economizar tokens
        self.size_var = tk.StringVar(value="512x512")
        sizes = ["512x512", "1024x1024", "1024x1536", "1536x1024", "auto"]
        self.size_menu = ttk.OptionMenu(main, self.size_var, self.size_var.get(), *sizes)
        self.size_menu.grid(column=1, row=row, sticky=tk.W)

        self.generate_btn = ttk.Button(main, text="Gerar imagem", command=self.on_generate)
        self.generate_btn.grid(column=0, row=row, sticky=tk.W)

        self.save_btn = ttk.Button(main, text="Salvar atual", command=self.on_save, state=tk.DISABLED)
        self.save_btn.grid(column=1, row=row, sticky=tk.W)

        self.status_var = tk.StringVar(value="Pronto")
        ttk.Label(main, textvariable=self.status_var).grid(column=2, row=row, columnspan=2, sticky=tk.W)

        row += 1
        main.rowconfigure(row, weight=1)
        preview_container = ttk.Frame(main, padding=12, relief=tk.SOLID)
        preview_container.grid(column=0, row=row, columnspan=4, pady=(12, 0), padx=(0, 12), sticky=tk.NSEW)
        preview_container.rowconfigure(0, weight=1)
        preview_container.columnconfigure(0, weight=1)
        self.preview_lbl = ttk.Label(preview_container)
        self.preview_lbl.grid(column=0, row=0, sticky=tk.NSEW)

        self._img = None
        self._tkimg = None

        self.q = queue.Queue()
        self.root.after(100, self._poll_queue)

    def on_generate(self):
        prompt = self.prompt_entry.get("1.0", tk.END).strip()
        if not prompt:
            messagebox.showwarning("Prompt vazio", "Por favor escreva um prompt para gerar a imagem.", parent=self.root)
            return

        requested_size = self.size_var.get()
        size = REQUESTED_API_SIZE.get(requested_size, requested_size)
        self.generate_btn.config(state=tk.DISABLED)
        self.save_btn.config(state=tk.DISABLED)
        self.status_var.set("Gerando...")
        self._show_loading_overlay()
        thread = threading.Thread(target=self._generate_worker, args=(prompt, size, requested_size), daemon=True)
        thread.start()

    def _generate_worker(self, prompt, size, requested_size):
        try:
            print(f"[ImageGenerator] Gerando prompt '{prompt[:40]}...' size={size}")
            openai_key = os.environ.get("OPENAI_KEY", "").strip()
            if not openai_key:
                raise RuntimeError("Abra uma conta no OpenAI e configure OPENAI_KEY no .env")
            img = self._generate_openai(prompt, size, openai_key)
            self.q.put(("ok", (img, requested_size)))
        except Exception as e:
            print("[ImageGenerator] Erro:", e)
            self.q.put(("err", str(e)))

    def _generate_placeholder(self, prompt, w, h):
        # Gera uma imagem simples com gradiente e texto do prompt
        img = Image.new("RGB", (w, h), color=(30, 30, 30))
        draw = ImageDraw.Draw(img)
        for i in range(h):
            r = int(30 + (i / h) * 140)
            g = int(30 + (i / h) * 70)
            b = int(60 + (i / h) * 120)
            draw.line([(0, i), (w, i)], fill=(r, g, b))

        # Texto central
        try:
            font = ImageFont.truetype("arial.ttf", size=max(14, w // 24))
        except Exception:
            font = ImageFont.load_default()

        text = prompt[:200]
        margin = 12
        draw.multiline_text((margin, margin), text, fill=(255, 255, 255), font=font)
        return img

    def _generate_openai(self, prompt, size, key):
        print(f"[OpenAI] Gerando '{prompt[:40]}...' size={size}")
        url = "https://api.openai.com/v1/images/generations"
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
        payload = {
            "prompt": prompt,
            "n": 1,
            "size": size,
            "model": OPENAI_IMAGE_MODEL,
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=120)
        if resp.status_code != 200:
            raise RuntimeError(f"OpenAI erro: {resp.status_code} - {resp.text}")

        data = resp.json()
        if not isinstance(data.get("data"), list) or not data["data"]:
            raise RuntimeError("Resposta inesperada da OpenAI")
        b64 = data["data"][0].get("b64_json")
        if not b64:
            raise RuntimeError("OpenAI retornou resposta sem b64_json")
        img_bytes = base64.b64decode(b64)
        return Image.open(io.BytesIO(img_bytes)).convert("RGB")

    def _poll_queue(self):
        try:
            while True:
                kind, payload = self.q.get_nowait()
                self._hide_loading_overlay()
                if kind == "ok":
                    img, requested_size = payload
                    self._img = img
                    self._show_preview(img, requested_size)
                    # Salva automaticamente a imagem menor ao gerar
                    self._auto_save(img, requested_size)
                    self.status_var.set("Pronto — imagem gerada e salva!")
                    self.save_btn.config(state=tk.NORMAL)
                else:
                    self.status_var.set(f"Erro: {payload}")
                    messagebox.showerror("Erro", str(payload), parent=self.root)

                self.generate_btn.config(state=tk.NORMAL)

        except queue.Empty:
            pass

        self.root.after(100, self._poll_queue)

    def _show_loading_overlay(self):
        if self.loading_overlay is not None:
            return
        self.loading_overlay = tk.Toplevel(self.root)
        self.loading_overlay.title("")
        self.loading_overlay.geometry("300x100")
        self.loading_overlay.transient(self.root)
        self.loading_overlay.grab_set()
        self.loading_overlay.resizable(False, False)
        tk.Label(self.loading_overlay, text="Aguarde enquanto geramos a imagem...", font=("Arial", 12)).pack(expand=True, fill=tk.BOTH, pady=30)
        self.loading_overlay.update()
        self._center_overlay(self.loading_overlay)

    def _hide_loading_overlay(self):
        if self.loading_overlay:
            self.loading_overlay.destroy()
            self.loading_overlay = None

    def _parse_requested_size(self, requested_size: str):
        if requested_size == "auto":
            return None
        try:
            w, h = requested_size.split("x")
            return (int(w), int(h))
        except ValueError:
            return None

    def _downscale_if_needed(self, img: Image.Image, requested_size: str):
        target = self._parse_requested_size(requested_size)
        if target and img.size != target:
            return img.resize(target, Image.LANCZOS)
        return img

    def _center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() - width) // 2
        y = (self.root.winfo_screenheight() - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _center_overlay(self, overlay):
        overlay.update_idletasks()
        ow = overlay.winfo_width()
        oh = overlay.winfo_height()
        rx = self.root.winfo_x()
        ry = self.root.winfo_y()
        rw = self.root.winfo_width()
        rh = self.root.winfo_height()
        x = rx + (rw - ow) // 2
        y = ry + (rh - oh) // 2
        overlay.geometry(f"{ow}x{oh}+{x}+{y}")

    def _auto_save(self, img, requested_size: str):
        mini = self._downscale_if_needed(img, requested_size)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"img_{ts}_mini.png"
        path = os.path.join(OUT_DIR, filename)
        mini.save(path)
        # Não mostra messagebox para não interromper o fluxo

    def _show_preview(self, img: Image.Image, requested_size: str):
        display_img = self._downscale_if_needed(img, requested_size)
        w, h = display_img.size
        max_w = 840
        scale = min(1.0, max_w / w)
        disp = display_img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        self._tkimg = ImageTk.PhotoImage(disp)
        self.preview_lbl.config(image=self._tkimg)

    def on_save(self):
        if self._img is None:
            return
        # Pergunta ao usuário o tamanho desejado
        tamanhos = [
            ("512x512", (512, 512)),
            ("1024x1024", (1024, 1024)),
            ("1536x1536", (1536, 1536)),
        ]
        # Simples dialog tkinter para escolha
        top = tk.Toplevel(self.root)
        top.title("Salvar imagem em tamanho...")
        tk.Label(top, text="Escolha o tamanho para salvar:").pack(padx=10, pady=10)
        var = tk.StringVar(value="1024x1024")
        for nome, _ in tamanhos:
            tk.Radiobutton(top, text=nome, variable=var, value=nome).pack(anchor=tk.W, padx=20)

        def salvar():
            escolha = var.get()
            tam = dict(tamanhos)[escolha]
            img_salvar = self._img.resize(tam, Image.LANCZOS)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"img_{ts}_{escolha.replace('x','_')}.png"
            path = os.path.join(OUT_DIR, filename)
            img_salvar.save(path)
            messagebox.showinfo("Salvo", f"Imagem salva em: {path}")
            top.destroy()

        tk.Button(top, text="Salvar", command=salvar).pack(pady=10)
        top.transient(self.root)
        top.grab_set()
        self.root.wait_window(top)


def main():
    root = tk.Tk()
    app = ImageGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

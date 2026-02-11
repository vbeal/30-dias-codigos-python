# ###################################################################
#           🎯 Projeto: Gerador de QR Code (Dia 12)                 #
# ###################################################################
# 📁 Caminho: dia-12/dia12_qrcode.py
# Desafio 30 dias com Python por Victor Beal
# ###################################################################
# 📚 Bibliotecas:  qrcode (gerar QR Code), 
#                   tkinter (interface gráfica), 
#                   Pillow (manipular imagens)
# 🔗 Instalação: pip install qrcode Pillow
# ###################################################################

import os
import threading
import queue
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import qrcode
from PIL import Image, ImageTk

ROOT = os.path.dirname(__file__)
TARGET_DIR = os.path.join(ROOT, 'qrcodes')
os.makedirs(TARGET_DIR, exist_ok=True)


def generate_qr_worker(texto, result_q):
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'qrcode_{timestamp}.png'
        filepath = os.path.join(TARGET_DIR, filename)
        img = qrcode.make(texto)
        img.save(filepath)
        result_q.put((True, filepath))
    except Exception as e:
        result_q.put((False, str(e)))


class App:
    def __init__(self, root):
        self.root = root
        root.title('Dia 12 — Gerador de QR Code')
        root.geometry('600x400')  # Aumentado para mostrar imagem

        top = tk.Frame(root)
        top.pack(fill='x', padx=8, pady=8)
        tk.Label(top, text='Texto ou Link:').pack(side='left')
        self.entry = tk.Entry(top, width=60)
        self.entry.pack(side='left', padx=6)
        self.btn = tk.Button(top, text='Gerar QR Code', command=self.start_generate)
        self.btn.pack(side='left')

        self.progress = ttk.Progressbar(root, mode='indeterminate')
        self.progress.pack(fill='x', padx=8)
        self.status = tk.Label(root, text='Aguardando ação...')
        self.status.pack(fill='x', padx=8, pady=(4, 8))

        self.image_label = tk.Label(root)
        self.image_label.pack(pady=10)

        self.result_q = queue.Queue()

    def start_generate(self):
        texto = self.entry.get().strip()
        if not texto:
            messagebox.showwarning('Aviso', 'Informe o texto ou link para gerar o QR Code')
            return
        self.progress.start(10)
        self.status.config(text='Gerando QR Code...')
        self.btn.config(state='disabled')
        self.image_label.config(image='')  # Limpar imagem anterior
        t = threading.Thread(target=generate_qr_worker, args=(texto, self.result_q), daemon=True)
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
            messagebox.showerror('Erro', f'Erro ao gerar QR Code: {data}')
            self.status.config(text='Erro durante a geração')
            return
        # Sucesso: mostrar localização e imagem
        filepath = data
        self.status.config(text=f'QR Code gerado: {os.path.basename(filepath)}')
        messagebox.showinfo('Concluído', f'QR Code salvo em:\n{filepath}')
        # Mostrar imagem na tela
        img = Image.open(filepath)
        img = img.resize((200, 200), Image.Resampling.LANCZOS)  # Redimensionar para caber
        self.photo = ImageTk.PhotoImage(img)
        self.image_label.config(image=self.photo)
        self.entry.delete(0, 'end')


if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()

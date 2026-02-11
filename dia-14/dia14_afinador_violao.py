# ###################################################################
#           🎯 Projeto: Afinador de Violão (Dia 14)                 #
# ###################################################################
# 📁 Caminho: dia-14/dia14_afinador_violao.py
# Desafio 30 dias com Python por Victor Beal
# ###################################################################
# 📚 Bibliotecas:  sounddevice (captura áudio),
#                   numpy (processamento FFT),
#                   tkinter (interface gráfica)
# 🔗 Instalação: pip install sounddevice numpy
# ###################################################################

import sounddevice as sd
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import threading
import queue

# Frequências padrão das cordas do violão (afinação padrão EADGBE)
notas = {
    "E2 (Mi grave)": 82.41,
    "A2 (Lá)": 110.00,
    "D3 (Ré)": 146.83,
    "G3 (Sol)": 196.00,
    "B3 (Si)": 246.94,
    "E4 (Mi agudo)": 329.63
}

def detectar_frequencia(amostra, taxa):
    # tentativa robusta: autocorrelação para encontrar o fundamental
    # remover DC e aplicar janela
    x = amostra - np.mean(amostra)
    if len(x) < 2:
        return 0.0
    win = np.hamming(len(x))
    x = x * win

    # Band-pass simples via FFT (filtrar fora da faixa de interesse)
    try:
        min_freq = 60.0
        max_freq = 1200.0
        X = np.fft.rfft(x)
        freqs_r = np.fft.rfftfreq(len(x), 1 / taxa)
        mask = (freqs_r >= min_freq) & (freqs_r <= max_freq)
        X[~mask] = 0
        x = np.fft.irfft(X, n=len(x))
    except Exception:
        # se o filtro falhar, continuar com sinal original
        pass

    # autocorrelação (usa np.correlate)
    corr = np.correlate(x, x, mode='full')
    corr = corr[corr.size // 2:]

    # também estimativa por FFT para robustez (encontra pico de magnitude)
    f_fft = 0.0
    try:
        X = np.fft.rfft(x)
        mags = np.abs(X)
        freqs_r = np.fft.rfftfreq(len(x), 1 / taxa)
        mask = (freqs_r >= 60.0) & (freqs_r <= 1200.0)
        if np.any(mask):
            mags_masked = mags.copy()
            mags_masked[~mask] = 0
            idx = np.argmax(mags_masked)
            f_fft = freqs_r[idx]
            # medir força do pico relativa à mediana
            med = np.median(mags_masked[mags_masked > 0]) if np.any(mags_masked > 0) else 0
            peak_strength = (mags_masked[idx] / med) if med > 0 else 0
        else:
            peak_strength = 0
    except Exception:
        f_fft = 0.0
        peak_strength = 0

    # definir faixa de frequência esperada (guitarra E2..E4 +/- margem)
    min_freq = 65.0   # Hz
    max_freq = 1200.0 # Hz (capacidade de detectar harmônicos altos)
    min_lag = int(taxa / max_freq) if max_freq > 0 else 1
    max_lag = int(taxa / min_freq) if min_freq > 0 else len(corr) - 1
    if max_lag >= len(corr):
        max_lag = len(corr) - 1

    # procurar pico no intervalo de lags
    segment = corr[min_lag:max_lag]
    if segment.size == 0:
        return 0.0

    peak = np.argmax(segment) + min_lag

    # afinar posição do pico por interpolação parabólica para melhor precisão
    if 1 <= peak < len(corr) - 1:
        y0, y1, y2 = corr[peak-1], corr[peak], corr[peak+1]
        denom = (y0 - 2 * y1 + y2)
        if denom != 0:
            shift = 0.5 * (y0 - y2) / denom
        else:
            shift = 0.0
        peak = peak + shift

    freq_ac = taxa / peak if peak != 0 else 0.0

    # escolher entre autocorrelação e FFT com base na confiança
    # preferência para FFT quando o pico for forte (peak_strength > 5)
    if f_fft > 0 and peak_strength > 5:
        chosen = f_fft
    else:
        chosen = freq_ac

    # fallback para FFT puro se escolhido inválido
    if not np.isfinite(chosen) or chosen <= 0.0:
        try:
            fft = np.fft.fft(amostra)
            freqs = np.fft.fftfreq(len(fft), 1/taxa)
            idx = np.argmax(np.abs(fft))
            chosen = abs(freqs[idx])
        except Exception:
            chosen = 0.0

    return float(chosen)


def recuperar_fundamental_aproximado(freq):
    """Tenta recuperar um possível fundamental a partir de um harmônico detectado.
    Divide por inteiros e escolhe o candidato cujo valor fica mais próximo de
    alguma nota padrão do violão.
    """
    if freq <= 0 or not np.isfinite(freq):
        return freq

    notas_vals = list(notas.values())

    melhor = (freq, 1e9, 1)
    # priorizar pequenos divisores (1..8) — harmônicos baixos são mais prováveis
    for k in range(1, 9):
        cand = freq / k
        if cand < 20:
            break
        dist = min(abs(cand - nv) for nv in notas_vals)
        if dist < melhor[1]:
            melhor = (cand, dist, k)

    # caso não encontre bom candidato, testar divisores maiores até 30 com penalidade
    if melhor[1] > 5.0:
        for k in range(9, 31):
            cand = freq / k
            if cand < 20:
                break
            dist = min(abs(cand - nv) for nv in notas_vals)
            penalty = k * 0.1
            if dist + penalty < melhor[1]:
                melhor = (cand, dist + penalty, k)

    # retornar candidato se reduz consideravelmente a distância
    # (ou seja, encontramos um sub-harmônico bem mais próximo das notas)
    orig_dist = min(abs(freq - nv) for nv in notas_vals)
    if melhor[1] + 1e-9 < orig_dist:
        print(f"[DEBUG] recuperar_fundamental: {freq:.2f} -> {melhor[0]:.2f} (k={melhor[2]}) dist {melhor[1]:.2f} origdist {orig_dist:.2f}")
        return melhor[0]
    return freq

class AfinadorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎸 Afinador de Violão - Dia 14")
        # janela maior para caber a imagem e controles
        self.root.geometry("1000x600")
        self.root.resizable(True, True)

        # Estilo
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 12), padding=10)
        style.configure("TLabel", font=("Arial", 10))

        # Canvas com imagem de fundo (se existir)
        # Painel superior com controles (fixo) — ficará acima da imagem
        self.top_frame = ttk.Frame(root, padding=(12,8))
        self.top_frame.pack(side="top", fill="x")

        # Canvas abaixo exibirá somente a imagem do violão (sem elementos sobrepostos)
        self.canvas = tk.Canvas(root, highlightthickness=0)
        self.canvas.pack(side="top", fill="both", expand=True)

        self.bg_image = None
        self.bg_image_id = None
        img_path = "dia-14/image.png"
        try:
            self.orig_img = Image.open(img_path).convert("RGBA")
        except Exception:
            self.orig_img = None

        # redesenhar background quando a janela mudar de tamanho
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Usar top_frame para conter widgets (não sobrepor a imagem)
        self.frame = ttk.Frame(self.top_frame)
        self.frame.pack(fill="x")

        self.label_instrucoes = ttk.Label(self.frame, text="Escolha a corda e clique para afinar. Ou clique em 'Auto' para detectar qualquer nota.")
        self.label_instrucoes.grid(row=0, column=0, columnspan=6, pady=(4,10))

        # Botões por corda (6ª -> 1ª)
        self.string_buttons = {}
        ordem = ["E2 (Mi grave)", "A2 (Lá)", "D3 (Ré)", "G3 (Sol)", "B3 (Si)", "E4 (Mi agudo)"]
        labels = ["MI (6ª)", "LÁ (5ª)", "RÉ (4ª)", "SOL (3ª)", "SI (2ª)", "MI (1ª)"]
        for i, nome in enumerate(ordem):
            b = ttk.Button(self.frame, text=labels[i], command=lambda n=nome: self.selecionar_corda(n), width=12)
            b.grid(row=1, column=i, padx=6, pady=6, sticky="nsew")
            self.string_buttons[nome] = b
            self.frame.grid_columnconfigure(i, weight=1)

        self.botao_auto = ttk.Button(self.frame, text="Auto", command=self.iniciar_afinacao, width=12)
        self.botao_auto.grid(row=2, column=0, columnspan=2, pady=(6,12), sticky="w")

        self.label_frequencia = ttk.Label(self.frame, text="Frequência detectada: -- Hz")
        self.label_frequencia.grid(row=3, column=0, columnspan=3, pady=4, sticky="w")

        self.label_nota = ttk.Label(self.frame, text="Nota/Alvo: --")
        self.label_nota.grid(row=3, column=3, columnspan=3, pady=4, sticky="e")

        # quadro grande de status com fonte maior
        status_frame = ttk.Frame(self.top_frame)
        status_frame.pack(fill="x", pady=(4,8))
        self.label_status = ttk.Label(status_frame, text="Status: --", font=("Segoe UI", 14), foreground="black", anchor="center")
        self.label_status.pack(fill="x", padx=12)

        # estilo dos botões e labels para visual mais consistente
        style = ttk.Style()
        style.configure("TButton", padding=8, font=("Segoe UI", 11))
        style.configure("TLabel", background="#ffffff")

        # forçar um primeiro redimensionamento para posicionar elementos
        self.root.update_idletasks()
        self._on_canvas_configure()

        # Queue para comunicação entre threads
        self.queue = queue.Queue()

        # Nota alvo quando o usuário escolhe uma corda
        self.alvo = None

        # Verificar queue periodicamente
        self.root.after(100, self.verificar_queue)

    def iniciar_afinacao(self):
        # auto-detect (sem alvo)
        self.alvo = None
        # desabilita botões
        for b in self.string_buttons.values():
            b.config(state="disabled")
        self.botao_auto.config(state="disabled")
        self.label_frequencia.config(text="Frequência detectada: Gravando...")
        self.label_nota.config(text="Nota/Alvo: Auto")
        self.label_status.config(text="Status: --")

        thread = threading.Thread(target=self.gravar_e_detectar, daemon=True)
        thread.start()
        # watchdog para caso a gravação trave/leve tempo demais
        try:
            if hasattr(self, '_reenable_job') and self._reenable_job is not None:
                self.root.after_cancel(self._reenable_job)
        except Exception:
            pass
        self._reenable_job = self.root.after(8000, self._force_reenable)

    def gravar_e_detectar(self):
        try:
            duracao = 2  # segundos (melhor precisão)
            taxa = 44100  # Hz
            # debug: verificar dispositivos de entrada
            try:
                devs = sd.query_devices()
                has_input = any(d.get('max_input_channels', 0) > 0 for d in devs)
                default_dev = sd.default.device
                print(f"[DEBUG] default device: {default_dev}")
                # listar dispositivos de entrada mínimos
                inputs = [d for d in devs if d.get('max_input_channels', 0) > 0]
                print(f"[DEBUG] input devices count: {len(inputs)}")
            except Exception as e:
                has_input = True
                print(f"[DEBUG] sd.query_devices() falhou: {e}")

            if not has_input:
                self.queue.put("Erro: nenhum dispositivo de entrada disponível")
                return

            print("[DEBUG] iniciando gravação")
            amostra = sd.rec(int(duracao * taxa), samplerate=taxa, channels=1, dtype='float64')
            sd.wait()
            print("[DEBUG] gravação finalizada")
            data = amostra.flatten()
            # estatísticas rápidas para diagnóstico
            maxabs = float(np.max(np.abs(data)))
            rms = float(np.sqrt(np.mean(data**2)))
            print(f"[DEBUG] sample maxabs={maxabs:.6f} rms={rms:.6f}")
            if maxabs < 1e-5 or rms < 1e-6:
                print("[DEBUG] sinal muito baixo ou ausente no microfone")
            freq = detectar_frequencia(data, taxa)
            print(f"[DEBUG] frequência detectada (raw): {freq}")
            # tentar recuperar fundamental caso detecte um harmônico
            try:
                freq_rec = recuperar_fundamental_aproximado(freq)
            except Exception as e:
                print(f"[DEBUG] recuperar_fundamental falhou: {e}")
                freq_rec = freq
            if abs(freq_rec - freq) > 0.5:
                print(f"[DEBUG] frequência ajustada para: {freq_rec}")
            freq = freq_rec
            # se houver alvo, envia tupla (freq, alvo)
            self.queue.put((freq, self.alvo))
        except Exception as e:
            self.queue.put(f"Erro: {str(e)}")

    def _force_reenable(self):
        # chamado se a gravação demorar muito ou travar
        self._reenable_job = None
        for b in self.string_buttons.values():
            try:
                b.config(state="normal")
            except Exception:
                pass
        try:
            self.botao_auto.config(state="normal")
        except Exception:
            pass
        self.label_status.config(text="Status: Erro - tempo excedido", foreground="red")

    def verificar_queue(self):
        try:
            resultado = self.queue.get_nowait()
            if isinstance(resultado, tuple):
                freq, alvo = resultado
                self.label_frequencia.config(text=f"Frequência detectada: {freq:.2f} Hz")
                if alvo is None:
                    # auto-detect: mostra nota mais próxima
                    mais_proxima = min(notas, key=lambda n: abs(notas[n] - freq))
                    freq_padrao = notas[mais_proxima]
                    diferenca = freq - freq_padrao
                    self.label_nota.config(text=f"Nota mais próxima: {mais_proxima} ({freq_padrao:.2f} Hz)")
                else:
                    freq_padrao = notas[alvo]
                    diferenca = freq - freq_padrao
                    self.label_nota.config(text=f"Nota alvo: {alvo} ({freq_padrao:.2f} Hz)")

                # Status
                tolerancia = 2.0  # Hz
                if abs(diferenca) <= tolerancia:
                    status = "🎯 Afinado!"
                    cor = "green"
                elif diferenca > 0:
                    status = f"⬆️ Aperte a corda ({diferenca:.2f} Hz acima)"
                    cor = "red"
                else:
                    status = f"⬇️ Afrouxe a corda ({abs(diferenca):.2f} Hz abaixo)"
                    cor = "red"

                self.label_status.config(text=f"Status: {status}", foreground=cor)
                # reabilita botões
                for b in self.string_buttons.values():
                    try:
                        b.config(state="normal")
                    except Exception:
                        pass
                try:
                    self.botao_auto.config(state="normal")
                except Exception:
                    pass
                # cancelar watchdog se existir
                try:
                    if hasattr(self, '_reenable_job') and self._reenable_job is not None:
                        self.root.after_cancel(self._reenable_job)
                        self._reenable_job = None
                except Exception:
                    pass
            else:
                messagebox.showerror("Erro", resultado)
        except queue.Empty:
            pass

        self.root.after(100, self.verificar_queue)

    def selecionar_corda(self, nome):
        # define alvo e inicia gravação para comparar com a nota selecionada
        self.alvo = nome
        for b in self.string_buttons.values():
            b.config(state="disabled")
        self.botao_auto.config(state="disabled")
        self.label_frequencia.config(text="Frequência detectada: Gravando...")
        self.label_nota.config(text=f"Nota/Alvo: {nome}")
        self.label_status.config(text="Status: --")
        thread = threading.Thread(target=self.gravar_e_detectar, daemon=True)
        thread.start()

    def _on_canvas_configure(self, event=None):
        # Debounce o redimensionamento para evitar trabalho pesado em eventos repetidos
        try:
            if hasattr(self, '_resize_job') and self._resize_job is not None:
                self.root.after_cancel(self._resize_job)
        except Exception:
            pass
        self._resize_job = self.root.after(150, self._do_resize)

    def _do_resize(self):
        # redesenha background de acordo com o tamanho atual do canvas
        self._resize_job = None
        w = self.canvas.winfo_width() or 1000
        h = self.canvas.winfo_height() or 600

        if self.orig_img is None:
            # sem imagem, pinta cor neutra
            self.canvas.configure(background="#f0f0f0")
            return

        # ajustar imagem para cobrir o canvas (cover) e cortar centro
        iw, ih = self.orig_img.size
        scale = max(w/iw, h/ih)
        new_w = int(iw * scale)
        new_h = int(ih * scale)
        # redimensionamento pode ser custoso; feito apenas após debounce
        img = self.orig_img.resize((new_w, new_h), Image.LANCZOS)
        left = max((new_w - w) // 2, 0)
        top = max((new_h - h) // 2, 0)
        img = img.crop((left, top, left + w, top + h))
        try:
            self.bg_image = ImageTk.PhotoImage(img)
        except Exception:
            return

        if self.bg_image_id is None:
            self.bg_image_id = self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
        else:
            self.canvas.itemconfig(self.bg_image_id, image=self.bg_image)

        # garantir que o background fique atrás dos controles (top_frame)
        try:
            self.canvas.tag_lower(self.bg_image_id)
        except Exception:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = AfinadorApp(root)
    root.mainloop()
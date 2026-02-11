# ###################################################################
#           🎯 Projeto: Baixar Postagem do Instagram (Dia 20)       #
# ###################################################################
# 📁 Caminho: dia-20/dia20_instagram_desktop.py
# Desafio 30 dias com Python por Victor Beal
# ###################################################################
# 📚 Bibliotecas: instaloader, Pillow, tkinter
# 🔗 Instalação: pip install instaloader pillow
# ###################################################################
import os           # Operações de sistema de arquivos e caminhos
import threading    # Thread para download em background
import queue        # Fila para comunicação entre thread e interface
import instaloader  # Biblioteca para baixar posts do Instagram
import re           # Expressões regulares para extrair shortcode
from datetime import datetime, timedelta  # Manipular datas
from tkinter import Tk, Frame, Label, Entry, Button, Scrollbar, Canvas, LEFT, RIGHT, Y, TOP, X, BOTH  # Componentes da interface Tkinter
from tkinter import ttk, messagebox   # Widgets avançados (barra de progresso) e caixas de mensagem
from PIL import Image, ImageTk        # Manipulação e exibição de imagens

def extract_shortcode(url):
    match = re.search(r'/(?:p|reel)/([A-Za-z0-9_-]+)', url)
    return match.group(1) if match else None

def parse_date_from_filename(fn):
    # Tenta extrair data no formato YYYY-MM-DD_HH-MM-SS (UTC em muitos casos)
    m = re.search(r'(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})', fn)
    if m:
        try:
            dt = datetime.strptime(m.group(1), '%Y-%m-%d_%H-%M-%S')
            # Ajusta de UTC para horário do Brasil (UTC-3) se o filename indicar UTC explícito
            if 'utc' in fn.lower():
                dt = dt - timedelta(hours=3)
            return dt
        except Exception:
            pass
    # Tenta extrair apenas a data YYYY-MM-DD
    m = re.search(r'(\d{4}-\d{2}-\d{2})', fn)
    if m:
        try:
            dt = datetime.strptime(m.group(1), '%Y-%m-%d')
            # Sem hora; use meia-noite como horário base e ajuste se necessário
            if 'utc' in fn.lower():
                dt = dt - timedelta(hours=3)
            return dt
        except Exception:
            pass
    # Fallback para modificação do arquivo
    try:
        return datetime.fromtimestamp(os.path.getmtime(fn))
    except Exception:
        return datetime.min

SCRIPT_DIR = os.path.dirname(__file__)
TARGET_DIR = os.path.join(SCRIPT_DIR, 'downloaded')
os.makedirs(TARGET_DIR, exist_ok=True)


class DownloaderThread(threading.Thread):
    def __init__(self, url, result_q):
        super().__init__(daemon=True)
        self.url = url
        self.result_q = result_q

    def run(self):
        try:
            print(f"URL recebida: {self.url}")
            shortcode = extract_shortcode(self.url)
            if not shortcode:
                raise ValueError("URL inválida: não foi possível extrair shortcode")
            print(f"Shortcode: {shortcode}")
            print(f"TARGET_DIR: {TARGET_DIR}")
            L = instaloader.Instaloader()
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            # Sempre salva em 'downloaded' relativo ao script
            # Detectar arquivos que serão criados: snapshot antes/depois
            before = set()
            for r, _, files in os.walk(TARGET_DIR):
                for f in files:
                    before.add(os.path.join(r, f))
            L.download_post(post, target='downloaded')
            after = set()
            for r, _, files in os.walk(TARGET_DIR):
                for f in files:
                    after.add(os.path.join(r, f))
            created = after - before
            print("Arquivos criados:", created)
            # Remove arquivos .json.xz
            for root, _, files in os.walk(TARGET_DIR):
                for f in files:
                    if f.endswith('.json.xz'):
                        try:
                            os.remove(os.path.join(root, f))
                        except Exception:
                            pass
            # Procura recursivamente por arquivos relacionados ao shortcode
            img = None
            vid = None
            txt = None
            # Procura nos arquivos criados primeiro
            for fp in created:
                f = os.path.basename(fp)
                lf = f.lower()
                if lf.endswith('.jpg') and img is None:
                    img = fp
                elif lf.endswith('.mp4') and vid is None:
                    vid = fp
                elif lf.endswith('.txt') and txt is None:
                    txt = fp
            # Se não encontrar, procura recursivamente em toda a pasta (fallback para arquivos antigos)
            if not any((img, vid, txt)):
                for root, _, files in os.walk(TARGET_DIR):
                    for f in files:
                        lf = f.lower()
                        fp = os.path.join(root, f)
                        if lf.endswith('.jpg') and img is None:
                            img = fp
                        elif lf.endswith('.mp4') and vid is None:
                            vid = fp
                        elif lf.endswith('.txt') and txt is None:
                            txt = fp
            # Salva um arquivo .info.txt com dados básicos do post para garantir disponibilidade
            info_path = None
            try:
                if img:
                    base = os.path.splitext(os.path.basename(img))[0]
                    info_path = os.path.join(os.path.dirname(img), base + '.info.txt')
                elif vid:
                    base = os.path.splitext(os.path.basename(vid))[0]
                    info_path = os.path.join(os.path.dirname(vid), base + '.info.txt')
                else:
                    base = shortcode
                    info_path = os.path.join(TARGET_DIR, f'{base}.info.txt')
                # Determine a date to store: prefer parsed date from filename or file mtime
                date_to_store = None
                candidate_for_date = img or vid or txt
                if candidate_for_date and os.path.exists(candidate_for_date):
                    date_to_store = parse_date_from_filename(candidate_for_date)
                else:
                    try:
                        src = candidate_for_date or info_path
                        date_to_store = datetime.fromtimestamp(os.path.getmtime(src))
                    except Exception:
                        date_to_store = None
                downloaded_time = datetime.now()
                with open(info_path, 'w', encoding='utf-8') as f:
                    f.write(f'URL: {self.url}\n')
                    f.write(f'Base: {base}\n')
                    f.write(f'Shortcode: {shortcode}\n')
                    f.write(f"Imagem: {img if img else ''}\n")
                    f.write(f"Vídeo: {vid if vid else ''}\n")
                    if date_to_store:
                        f.write(f'Date: {date_to_store.isoformat()}\n')
                    if downloaded_time:
                        f.write(f'Downloaded: {downloaded_time.isoformat()}\n')
                    if txt and os.path.exists(txt):
                        with open(txt, encoding='utf-8') as ft:
                            legenda = ft.read().strip()
                        f.write(f'Legenda: {legenda}\n')
                    else:
                        f.write('Legenda: (sem legenda)\n')
            except Exception:
                info_path = None
            self.result_q.put((True, {'url': self.url, 'img': img, 'vid': vid, 'txt': txt, 'info': info_path}))
        except Exception as e:
            print(f"Erro no download: {e}")
            import traceback
            traceback.print_exc()
            self.result_q.put((False, str(e)))


class App:
    def __init__(self, root):
        self.root = root
        root.title('Downloader de Vídeos - Instagram')
        root.geometry('760x520')
        # Ícone simples embutido (1x1 pixel colorido) - substitua por um .png mais bonito se quiser
        try:
            import base64
            from tkinter import PhotoImage
            icon_data = b'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII='
            img = PhotoImage(data=icon_data)
            root.iconphoto(True, img)
        except Exception:
            pass

        top = Frame(root)
        top.pack(side=TOP, fill=X, padx=8, pady=8)

        Label(top, text='URL do post:').pack(side=LEFT)
        self.entry = Entry(top, width=60)
        self.entry.pack(side=LEFT, padx=6)
        self.btn = Button(top, text='Download', command=self.start_download)
        self.btn.pack(side=LEFT)

        self.progress = ttk.Progressbar(root, mode='indeterminate')
        self.progress.pack(fill=X, padx=8)

        self.canvas = Canvas(root)
        self.scrollbar = Scrollbar(root, orient='vertical', command=self.canvas.yview, width=20)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.items_frame = Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.items_frame, anchor='nw')
        self.items_frame.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        # Bind mouse wheel events (Windows/Linux/Mac)
        self.canvas.bind_all('<MouseWheel>', self._on_mousewheel)
        self.canvas.bind_all('<Button-4>', self._on_mousewheel)
        self.canvas.bind_all('<Button-5>', self._on_mousewheel)

        self.result_q = queue.Queue()
        self.thumbs = []
        self.refresh_items()

    def start_download(self):
        url = self.entry.get().strip()
        if not url:
            messagebox.showwarning('Aviso', 'Informe a URL do post')
            return
        self.progress.start(10)
        self.btn.config(state='disabled')
        thread = DownloaderThread(url, self.result_q)
        thread.start()
        self.root.after(200, self.check_result)

    def check_result(self):
        try:
            ok, data = self.result_q.get_nowait()
        except queue.Empty:
            self.root.after(200, self.check_result)
            return
        self.progress.stop()
        self.btn.config(state='normal')
        # Limpa o campo URL após o download terminar
        try:
            self.entry.delete(0, 'end')
        except Exception:
            pass
        if not ok:
            messagebox.showerror('Erro', f'Falha no download:\n{data}')
            return
        self.refresh_items()

    def add_item(self, info):
        frame = Frame(self.items_frame, bd=1, relief='solid', padx=6, pady=6)
        frame.pack(fill=X, padx=6, pady=6)
        # Imagem
        if info['img'] and os.path.exists(info['img']):
            try:
                img = Image.open(info['img'])
                img.thumbnail((160, 120))
                photo = ImageTk.PhotoImage(img)
                lbl = Label(frame, image=photo)
                lbl.image = photo
                lbl.pack(side=LEFT)
                self.thumbs.append(photo)
            except Exception:
                Label(frame, text='(erro na imagem)').pack(side=LEFT, padx=8)
        else:
            Label(frame, text='(sem imagem)').pack(side=LEFT, padx=8)
        # Info
        right = Frame(frame)
        right.pack(side=LEFT, fill=X, expand=True, padx=8)
        # Link do post e legenda (prioriza .info.txt se existir)
        url_text = info.get('url', '')
        caption = '(sem legenda)'
        info_path = info.get('info')
        if info_path and os.path.exists(info_path):
            try:
                with open(info_path, encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('URL:'):
                            url_text = line.replace('URL:', '').strip()
                        elif line.startswith('Legenda:'):
                            caption = line.replace('Legenda:', '').strip()
            except Exception:
                pass
        else:
            if info.get('txt') and os.path.exists(info.get('txt')):
                try:
                    with open(info['txt'], encoding='utf-8') as f:
                        raw = f.read().strip()
                        # Remove linhas de metadados se algum .info.txt tiver sido usado como txt
                        cleaned = []
                        for ln in raw.splitlines():
                            if not ln.strip():
                                continue
                            low = ln.strip().lower()
                            if low.startswith('url:') or low.startswith('imagem:') or low.startswith('vídeo:') or low.startswith('video:') or low.startswith('legenda:'):
                                continue
                            cleaned.append(ln)
                        caption = '\n'.join(cleaned).strip() or '(sem legenda)'
                except Exception:
                    caption = '(não foi possível ler legenda)'
        display_url = url_text.split('?')[0] if url_text else ''
        Label(right, text=f'URL: {display_url}', anchor='w', fg='blue').pack(fill=X)
        # Botão para abrir link no navegador (se houver)
        if url_text:
            try:
                import webbrowser
                btn_link = Button(right, text='Abrir link', command=lambda u=url_text: webbrowser.open(u))
                btn_link.pack(anchor='e')
            except Exception:
                pass
        # Data do post (exibir em formato DD/MM/AAAA HH:MM:SS - horário BR) e mostrar data de download
        if info.get('date'):
            try:
                # Ajuste: já convertemos UTC->BR no parse de filename; aqui apenas formatamos
                lbl_date = Label(right, text=f"Data do Post: {info['date'].strftime('%d/%m/%Y %H:%M:%S')}", anchor='w')
                lbl_date.pack(fill=X)
            except Exception:
                pass
        # Mostrar data de download (se existir)
        downloaded_text = None
        if info.get('downloaded'):
            try:
                downloaded_text = info['downloaded'].strftime('%d/%m/%Y %H:%M:%S')
            except Exception:
                downloaded_text = str(info.get('downloaded'))
        if downloaded_text:
            Label(right, text=f"Download: {downloaded_text}", anchor='w').pack(fill=X)
        lblcap = Label(right, text=caption, anchor='w', justify='left', wraplength=460)
        lblcap.pack(fill=X, pady=(6, 4))
        # Botões
        controls = Frame(right)
        controls.pack(anchor='e')
        if info['vid'] and os.path.exists(info['vid']):
            btn_play = Button(controls, text='Play', command=lambda p=info['vid']: os.startfile(p))
            btn_play.pack(side=LEFT, padx=4)
        if info['img'] and os.path.exists(info['img']):
            btn_view = Button(controls, text='Abrir Imagem', command=lambda p=info['img']: os.startfile(p))
            btn_view.pack(side=LEFT, padx=4)
        if info['txt'] and os.path.exists(info['txt']):
            btn_show = Button(controls, text='Legenda', command=lambda t=info['txt']: self.show_caption(t))
            btn_show.pack(side=LEFT, padx=4)

    def refresh_items(self):
        # Limpa lista
        for widget in self.items_frame.winfo_children():
            widget.destroy()
        # Busca todos os conjuntos de arquivos por shortcode
        posts = {}
        for root, _, files in os.walk(TARGET_DIR):
            for f in files:
                if f.endswith('.json.xz'):
                    try:
                        os.remove(os.path.join(root, f))
                    except Exception:
                        pass
                # Group files by base filename (without extension) to handle timestamp names
                base = os.path.splitext(f)[0]
                fp = os.path.join(root, f)
                if base not in posts:
                    posts[base] = {'url': '', 'img': None, 'vid': None, 'txt': None, 'info': None}
                if f.lower().endswith('.jpg'):
                    posts[base]['img'] = fp
                elif f.lower().endswith('.mp4'):
                    posts[base]['vid'] = fp
                elif f.lower().endswith('.txt') and not f.lower().endswith('.info.txt'):
                    # .txt pode ser legenda; armazena como legenda
                    posts[base]['txt'] = fp
                elif f.lower().endswith('.info.txt'):
                    posts[base]['info'] = fp
        # Se existirem .info.txt baseados em shortcode que não batem com o base do nome do arquivo,
        # junte (merge) esses dados no registro que tem o base correto (timestamp-based).
        keys = list(posts.keys())
        for k in keys:
            p = posts.get(k)
            if not p:
                continue
            info_file = p.get('info')
            if info_file and os.path.exists(info_file):
                try:
                    base_from_info = None
                    shortcode_from_info = None
                    with open(info_file, encoding='utf-8') as f:
                        for line in f:
                            if line.startswith('Base:'):
                                base_from_info = line.replace('Base:', '').strip()
                            elif line.startswith('Shortcode:'):
                                shortcode_from_info = line.replace('Shortcode:', '').strip()
                                break
                    if base_from_info and base_from_info != k:
                        # merge into base_from_info
                        if base_from_info in posts:
                            dest = posts[base_from_info]
                            for field in ('img', 'vid', 'txt', 'info', 'url'):
                                if not dest.get(field) and p.get(field):
                                    dest[field] = p[field]
                            # remove duplicate
                            try:
                                posts.pop(k, None)
                                print(f"Merged {k} into {base_from_info} via Base from .info.txt")
                            except Exception:
                                pass
                        else:
                            # rename key
                            posts[base_from_info] = posts.pop(k)
                            print(f"Renamed/merged key {k} -> {base_from_info} via Base from .info.txt")
                    elif shortcode_from_info and shortcode_from_info != k:
                        # fallback: try to find a base in posts that contains the shortcode in any file
                        target = None
                        for other_base, other_post in list(posts.items()):
                            if other_base == k:
                                continue
                            found = False
                            for field in ('img', 'vid', 'txt', 'info'):
                                pth = other_post.get(field)
                                if pth and os.path.basename(pth).find(shortcode_from_info) != -1:
                                    found = True
                                    break
                            if found:
                                target = other_base
                                break
                        if target:
                            dest = posts[target]
                            for field in ('img', 'vid', 'txt', 'info', 'url'):
                                if not dest.get(field) and p.get(field):
                                    dest[field] = p[field]
                            posts.pop(k, None)
                            print(f"Merged {k} into {target} via Shortcode match")
                except Exception:
                    pass
        # Merge by URL: if an .info.txt has URL that matches other post, combine entries
        url_map = {}
        for k, p in list(posts.items()):
            u = p.get('url')
            if u:
                url_map[u] = k
        for k, p in list(posts.items()):
            u = p.get('url')
            if u and u in url_map and url_map[u] != k:
                target = url_map[u]
                # merge p into target
                dest = posts.get(target)
                if dest:
                    for field in ('img', 'vid', 'txt', 'info', 'url'):
                        if not dest.get(field) and p.get(field):
                            dest[field] = p[field]
                    posts.pop(k, None)
        # Calcula data de cada post (prioriza imagem/video, depois info.txt, por fim mtime)
        for base, post in posts.items():
            date = None
            candidate = post.get('img') or post.get('vid') or post.get('info') or post.get('txt')
            if candidate and os.path.exists(candidate):
                date = parse_date_from_filename(candidate)
            else:
                # tenta pegar a data por qualquer arquivo no diretório do post
                try:
                    for root, _, files in os.walk(TARGET_DIR):
                        for f in files:
                            if f.startswith(base):
                                pathf = os.path.join(root, f)
                                date = parse_date_from_filename(pathf)
                                break
                        if date:
                            break
                except Exception:
                    date = datetime.min
            post['date'] = date or datetime.min
            # Lê URL do arquivo .info.txt se existir
            if post.get('info') and os.path.exists(post['info']):
                try:
                    with open(post['info'], encoding='utf-8') as f:
                        for line in f:
                            if line.startswith('URL:'):
                                post['url'] = line.replace('URL:', '').strip()
                                break
                    # also read Date if present
                    with open(post['info'], encoding='utf-8') as f:
                        for line in f:
                            if line.startswith('Date:'):
                                try:
                                    post['date'] = datetime.fromisoformat(line.replace('Date:', '').strip())
                                except Exception:
                                    pass
                                break
                    # also read 'Downloaded:'
                    with open(post['info'], encoding='utf-8') as f:
                        for line in f:
                            if line.startswith('Downloaded:'):
                                try:
                                    post['downloaded'] = datetime.fromisoformat(line.replace('Downloaded:', '').strip())
                                except Exception:
                                    pass
                                break
                except Exception:
                    pass
        # Ordena por data de download decrescente (mais recente primeiro); se não houver, usa a data do post
        posts_list = sorted(posts.values(), key=lambda x: x.get('downloaded') or x.get('date') or datetime.min, reverse=True)
        for post in posts_list:
            self.add_item(post)

    def show_caption(self, path):
        try:
            with open(path, encoding='utf-8') as f:
                txt = f.read()
            messagebox.showinfo('Legenda', txt)
        except Exception:
            messagebox.showerror('Erro', 'Não foi possível ler a legenda')

    def _on_mousewheel(self, event):
        try:
            if hasattr(event, 'delta'):
                # Windows / Mac
                self.canvas.yview_scroll(int(-1*(event.delta/120)), 'units')
            elif event.num == 4:
                # Linux scroll up
                self.canvas.yview_scroll(-1, 'units')
            elif event.num == 5:
                # Linux scroll down
                self.canvas.yview_scroll(1, 'units')
        except Exception:
            pass


if __name__ == '__main__':
    root = Tk()
    app = App(root)
    root.mainloop()

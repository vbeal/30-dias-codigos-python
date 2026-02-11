# ###################################################################
#           🎯 Projeto: Baixar Postagem do Instagram (Dia 10)        #
# ###################################################################
# 📁 Caminho: dia-10/dia10_instagram_downloader.py
# Desafio 30 dias com Python por Victor Beal
# ###################################################################
# 📚 Bibliotecas: instaloader (baixar conteúdo)
# 🔗 Instalação: pip install instaloader
# ###################################################################

import instaloader
import os
import re
import getpass

def extract_shortcode(url):
    match = re.search(r'/(?:p|reel)/([A-Za-z0-9_-]+)', url)
    return match.group(1) if match else None

loader = instaloader.Instaloader()
post_url = input("Insira a URL do post público do Instagram: ")
print(f"URL inserida: {post_url}")
shortcode = extract_shortcode(post_url)
if not shortcode:
    print("URL inválida. Não foi possível extrair o shortcode.")
    exit(1)

print(f"Shortcode extraído: {shortcode}")

# Opção de login para evitar bloqueios
login_op = input("Deseja fazer login no Instagram? (s/n): ").strip().lower()
if login_op == 's':
    usuario = input("Usuário: ")
    senha = getpass.getpass("Senha: ")
    try:
        loader.login(usuario, senha)
        print("Login realizado com sucesso.")
    except Exception as e:
        print(f"Erro no login: {e}")
        exit(1)

try:
    post = instaloader.Post.from_shortcode(loader.context, shortcode)
    pasta = "downloaded_videos"
    loader.download_post(post, target=pasta)

    # Descobre arquivos baixados (procura recursivamente dentro de subpastas criadas pelo Instaloader)
    img_path = None
    video_path = None
    legenda_path = None
    for root, _, files in os.walk(pasta):
        for f in files:
            lf = f.lower()
            if shortcode in f:
                fp = os.path.join(root, f)
                if lf.endswith('.jpg') and img_path is None:
                    img_path = fp
                elif lf.endswith('.mp4') and video_path is None:
                    video_path = fp
                elif lf.endswith('.txt') and legenda_path is None:
                    legenda_path = fp

    print("\nDownload concluído!")
    print(f"Capa: {os.path.basename(img_path) if img_path else 'Não encontrado'}")
    print(f"Vídeo: {os.path.basename(video_path) if video_path else 'Não encontrado'}")
    print(f"Legenda: {os.path.basename(legenda_path) if legenda_path else 'Não encontrado'}")

    # Remove arquivo .json.xz gerado pelo Instaloader
    # Remove arquivos .json.xz em toda a árvore de download
    for root, _, files in os.walk(pasta):
        for f in files:
            if f.endswith('.json.xz'):
                try:
                    os.remove(os.path.join(root, f))
                except Exception:
                    pass

    while True:
        print("\nO que deseja abrir?")
        print("1 - Ver capa")
        print("2 - Ver vídeo")
        print("3 - Ver legenda (exibir texto)")
        print("4 - Sair")
        escolha = input("Escolha: ").strip()
        if escolha == "1" and img_path:
            os.startfile(img_path)
        elif escolha == "2" and video_path:
            os.startfile(video_path)
        elif escolha == "3" and legenda_path:
            try:
                with open(legenda_path, encoding='utf-8') as f:
                    print("\nLegenda:\n" + f.read())
            except Exception:
                print("Não foi possível exibir a legenda.")
        elif escolha == "4":
            print("Saindo...")
            break
        else:
            print("Opção inválida ou arquivo não encontrado.")
except Exception as e:
    print(f"Erro ao fazer download: {e}")
    print("Detalhes do erro:", str(e))
    import traceback
    traceback.print_exc()
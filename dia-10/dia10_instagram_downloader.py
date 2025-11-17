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

loader = instaloader.Instaloader()
post_url = input("Insira a URL do post público do Instagram: ")
shortcode = post_url.split("/")[-2]

try:
    post = instaloader.Post.from_shortcode(loader.context, shortcode)
    pasta = "downloaded_videos"
    loader.download_post(post, target=pasta)

    # Descobre arquivos baixados
    img = next((f for f in os.listdir(pasta) if f.endswith(".jpg")), None)
    video = next((f for f in os.listdir(pasta) if f.endswith(".mp4")), None)
    legenda = next((f for f in os.listdir(pasta) if f.endswith(".txt")), None)

    print("\nDownload concluído!")
    print(f"Capa: {img if img else 'Não encontrado'}")
    print(f"Vídeo: {video if video else 'Não encontrado'}")
    print(f"Legenda: {legenda if legenda else 'Não encontrado'}")

    # Remove arquivo .json.xz gerado pelo Instaloader
    for f in os.listdir(pasta):
        if f.endswith('.json.xz'):
            try:
                os.remove(os.path.join(pasta, f))
            except Exception:
                pass

    while True:
        print("\nO que deseja abrir?")
        print("1 - Ver capa")
        print("2 - Ver vídeo")
        print("3 - Ver legenda (exibir texto)")
        print("4 - Sair")
        escolha = input("Escolha: ").strip()
        if escolha == "1" and img:
            os.startfile(os.path.join(pasta, img))
        elif escolha == "2" and video:
            os.startfile(os.path.join(pasta, video))
        elif escolha == "3" and legenda:
            try:
                with open(os.path.join(pasta, legenda), encoding='utf-8') as f:
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
# ################################################
# 🎯 Projeto: Baixar Vídeo do YouTube com Escolha de Formato
# ################################################
# 📁 Caminho: dia-3/dia03_baixar_video_youtube.py
# Desafio 30 dias com Python por Victor Beal
# ################################################

import os
from pytubefix import YouTube

def baixar_video():
    url = input('🔗 Cole o link do YouTube: ').strip()
    if not url:
        print('Link vazio. Saindo.')
        return
    
    print('\nEscolha a resolução:')
    print('1. 360p (vídeo+áudio - sempre disponível)')
    print('2. 720p (vídeo+áudio - se disponível)')
    print('3. Melhor qualidade disponível (pode ser só 360p)')
    escolha = input('Digite 1, 2 ou 3: ').strip()
    
    try:
        yt = YouTube(url)
        print(f'\n📺 {yt.title}')
        
        # Listar streams progressivos (vídeo+áudio juntos)
        progressive_streams = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()
        
        print('\n📋 Resoluções com vídeo+áudio disponíveis:')
        for s in progressive_streams:
            print(f'   - {s.resolution} ({s.filesize // (1024*1024)}MB)')
        
        if escolha == '2':
            stream = progressive_streams.filter(res='720p').first()
            if not stream:
                print('\n⚠️  720p com áudio não está disponível.')
                print('💡 Para 720p+ é necessário baixar vídeo e áudio separados e juntar com ffmpeg.')
                print('   Baixando melhor qualidade disponível (progressive)...')
                stream = progressive_streams.first()
        elif escolha == '3':
            stream = progressive_streams.first()
        else:
            stream = progressive_streams.filter(res='360p').first()
            if not stream:
                stream = progressive_streams.first()
        
        if not stream:
            print('❌ Nenhum formato com vídeo+áudio encontrado.')
            return
        
        print(f'\n⬇️  Baixando {stream.resolution} ({stream.filesize // (1024*1024)}MB) com áudio...')
        caminho_arquivo = stream.download(output_path='./dia-3')
        print('✅ Download concluído! Arquivo salvo em: dia-3/')
        
        # Opção de abrir o arquivo
        print('\n0 - Sair')
        print('1 - Abrir o arquivo baixado')
        opcao = input('Digite sua escolha: ').strip()
        
        if opcao == '1':
            if os.path.exists(caminho_arquivo):
                print(f'🎬 Abrindo {os.path.basename(caminho_arquivo)}...')
                os.startfile(caminho_arquivo)
            else:
                print('❌ Arquivo não encontrado.')
        else:
            print('👋 Até logo!')
        
    except Exception as e:
        print(f'❌ Erro: {e}')

if __name__ == '__main__':
    baixar_video()
# ################################################

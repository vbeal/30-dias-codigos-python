# 30 Dias de Código em Python 🚀

Bem-vindo ao meu desafio pessoal de **30 dias programando em Python**! Este repositório contém códigos simples e práticos desenvolvidos diariamente como parte de um estudo contínuo.

## 📅 Sobre o Projeto

- **Autor**: Victor Beal
- **Objetivo**: Aprender e praticar Python de forma rápida e acessível
- **Formato**: Um código novo por dia, sempre simples e direto
- **Conteúdo**: Projetos variados como conversores, filtros, interfaces gráficas, etc.
- **Vídeos**: Todos os dias são filmados e compartilhados (links em breve)

## 📁 Estrutura dos Dias

Cada pasta `dia-X/` contém:

- O código principal em Python
- Comentários explicativos no código
- Exemplos de uso

### Dias e Projetos concluídos:

- **Dia 1**: Filtro de câmera estilo Instagram (OpenCV)
- **Dia 2**: Conversor de texto para voz com estilo (pyttsx3)
- **Dia 3**: Baixar vídeo do YouTube com escolha de formato (pytubefix)
- **Dia 4**: Cartão de visita digital com ícones e logo (Pillow)
- **Dia 5**: Fogos de artifício com Turtle
- **Dia 6**: Conversor de moedas com API (requests)
- **Dia 7**: Conversor de moedas com interface gráfica (Tkinter)
- **Dia 8**: Conversor de moedas web com Flask
- **Dia 9**: Gráfico de Cotação de Moeda
- **Dia 10**: Baixar post do Instagram (Instaloader)
- **Dia 11**: Baixar vídeo do X/Twitter com interface gráfica (yt-dlp + Tkinter)
- **Dia 12**: Gerador de QR Code com interface gráfica (qrcode + Tkinter + Pillow)
- **Dia 14**: Afinador de Violão com interface gráfica (sounddevice + numpy + Tkinter)

## Dia 10 - Baixar post do Instagram

Este projeto permite baixar o conteúdo (imagem, vídeo e legenda) de um post público do Instagram informando a URL. O download é feito via Instaloader e os arquivos são organizados na pasta `dia-10/downloaded_videos`.

- O usuário informa a URL do post.
- O script baixa a capa (imagem), vídeo (se houver) e legenda (exibida no terminal).
- Arquivos auxiliares (.json.xz) são removidos automaticamente.
- Menu interativo para abrir capa, vídeo ou exibir legenda.

**Bibliotecas usadas:**

- instaloader
- os

Arquivo principal: `dia-10/dia10_instagram_downloader.py`

## Dia 11 - Baixar vídeo do X/Twitter

Este projeto permite baixar vídeos de posts públicos do X (antigo Twitter) informando a URL do tweet. Usa interface gráfica com Tkinter para uma experiência desktop.

- O usuário informa a URL do tweet na interface.
- O script baixa o vídeo em background usando yt-dlp.
- Barra de progresso e status durante o download.
- Vídeo salvo na pasta `dia-11/downloaded/`.
- Mensagem de confirmação com localização do arquivo.

**Bibliotecas usadas:**

- yt-dlp
- tkinter
- threading
- queue

Arquivo principal: `dia-11/dia11_x_downloader.py`

## Dia 12 - Gerador de QR Code

Este projeto gera QR Codes a partir de texto ou links informados pelo usuário, com interface gráfica bonita.

- O usuário digita o texto/link na interface Tkinter.
- Geração em background com barra de progresso.
- QR Code exibido diretamente na tela (redimensionado).
- Arquivo salvo em `dia-12/qrcodes/` com nome único (timestamp) para evitar sobrescrever.
- Mensagem de confirmação com caminho do arquivo.

**Bibliotecas usadas:**

- qrcode
- tkinter
- Pillow
- threading
- queue

Arquivo principal: `dia-12/dia12_qrcode.py`

## Dia 14 - Afinador de Violão

Este projeto é um afinador de violão com interface gráfica desktop. Detecta a frequência da corda tocada ou som emitido e compara com as notas padrão do violão (afinação EADGBE).

- O usuário clica em "Afinar" para iniciar a detecção.
- Gravação de áudio por 2 segundos e análise via FFT.
- Exibe frequência detectada, nota mais próxima e status (afinado, apertar ou afrouxar).
- Interface bonita com Tkinter, usando threading para não travar a GUI.

**Bibliotecas usadas:**

- sounddevice
- numpy
- tkinter
- threading
- queue

Arquivo principal: `dia-14/dia14_afinador_violao.py`

## 🛠️ Como Usar

1. **Clone o repositório**:

2. **Crie um ambiente virtual** (recomendado):

   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   ```

3. **Instale dependências** (se necessário):

   ```bash
   pip install -r requirements.txt
   ```

   python dia-1/dia01_filtro_camera.py

## 📚 Tecnologias e Bibliotecas

- **Python 3.x**
- **Tkinter** (interfaces gráficas)
- **Requests** (APIs)
- **OpenCV** (visão computacional)
- **Pytube/Pytubefix** (YouTube)
- **Matplotlib** (gráficos)
- **Instaloader** (Instagram)
- **yt-dlp** (X/Twitter e multi-site downloader)
- **qrcode** (gerar QR Codes)
- **Pillow** (manipulação de imagens)

## 📖 Licença

Este projeto é **100% livre** para uso, modificação e distribuição. Sinta-se à vontade para:

- Copiar os códigos
- Adaptar para seus projetos
- Compartilhar com amigos
- Usar como base para estudos

**Não há restrições** - use como quiser! 😊

## 🎥 Vídeos

Os vídeos diários são publicados em [YouTube](https://youtube.com/@victorbeal) (link em breve).

## 🤝 Contribuições

Sugestões e melhorias são bem-vindas! Abra uma issue ou envie um pull request.

## 📞 Contato

- **GitHub**: https://github.com/vbeal
- **LinkedIn**: https://www.linkedin.com/in/victorbeal/
- **Email**: victorbeal@gmail.com

---

**Vamos codar juntos!** 💻✨

#30DiasDeCodigo #Python #Aprendizado</content>
<parameter name="filePath">d:\projetos Python\30-dias-codigos-python\README.md

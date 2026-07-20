# 30 Dias de Código em Python 🚀

Bem-vindo ao meu desafio pessoal de **30 dias programando em Python**! Este repositório contém códigos simples e práticos desenvolvidos diariamente como parte de um estudo contínuo.

## 📅 Sobre o Projeto

- **Autor**: Victor Beal
- **Objetivo**: Aprender e praticar Python de forma rápida e acessível
- **Formato**: Um código novo por dia, sempre simples e direto
- **Conteúdo**: Projetos variados como conversores, filtros, interfaces gráficas, web apps, etc.
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
- **Dia 9**: Gráfico de cotação de moeda (Matplotlib)
- **Dia 10**: Baixar post do Instagram (Instaloader — terminal)
- **Dia 11**: Baixar vídeo do X/Twitter com interface gráfica (yt-dlp + Tkinter)
- **Dia 12**: Gerador de QR Code com interface gráfica (qrcode + Tkinter + Pillow)
- **Dia 13**: Gerador de imagens com IA (OpenAI Image API + Tkinter)
- **Dia 14**: Gerador de assinatura digital com mouse (Tkinter + Pillow)
- **Dia 15**: Top dividendos B3 — versão terminal (yfinance)
- **Dia 16**: Top dividendos B3 — versão Windows (Tkinter + yfinance)
- **Dia 17**: Top dividendos B3 — versão web (Flask + Bootstrap + Chart.js)
- **Dia 20**: Baixar postagem do Instagram — versão desktop (Instaloader + Tkinter)
- **Dia 21**: Sistema de login com SQLite (Flask + Bootstrap + sessões)
- **Dia 22**: Perfil do usuário (CRUD + foto) — continua o Dia 21
- **Dia 23**: Top 10 dividendos no painel (scraper ao vivo + gráficos)
- **Dia 24**: Detalhe de FII e Ação (scrape sob demanda + busca)
- **Dia 25**: Busca com lista fixa + calculadora de dividendos (Brapi light)
- **Dia 26**: Carteiras do investidor — várias por usuário + lançamentos (CRUD)
- **Dia 27**: Carteira completa — posições, resumo e gráfico mensal (Yahoo)
- **Dia 28**: InvestidorWeb — proventos, cache Yahoo, número mágico, lista completa B3 (~1200 ativos)

> **Extra:** O projeto **Afinador de Violão** (sounddevice + numpy + Tkinter) está em `dia-31-outraidea/dia14_afinador_violao.py`.

---

## Dia 1 - Filtro de Câmera Estilo Instagram

Aplica filtros em tempo real na webcam usando OpenCV, simulando efeitos de apps de foto.

- Abre a câmera do computador automaticamente.
- Filtros disponíveis: preto e branco, sépia, negativo e azul neon.
- Teclas `1` a `4` trocam o filtro; `0` remove o filtro; `q` encerra.
- Exibição em janela ao vivo com `cv2.imshow`.

**Bibliotecas usadas:** opencv-python, numpy

**Arquivo principal:** `dia-1/dia01_filtro_camera.py`

```bash
python dia-1/dia01_filtro_camera.py
```

---

## Dia 2 - Conversor de Texto para Voz

Converte texto digitado pelo usuário em fala sintetizada com voz robótica.

- Entrada de texto pelo terminal.
- Configuração de voz, velocidade e volume.
- Reprodução imediata com pyttsx3.

**Bibliotecas usadas:** pyttsx3

**Arquivo principal:** `dia-2/dia02_texto_para_voz.py`

```bash
python dia-2/dia02_texto_para_voz.py
```

---

## Dia 3 - Baixar Vídeo do YouTube

Baixa vídeos do YouTube com escolha de resolução via terminal.

- O usuário cola o link do vídeo.
- Opções: 360p, 720p ou melhor qualidade disponível.
- Exibe título do vídeo antes do download.
- Salva o arquivo na pasta do projeto.

**Bibliotecas usadas:** pytubefix, os

**Arquivo principal:** `dia-3/dia03_baixar_video_youtube.py`

```bash
python dia-3/dia03_baixar_video_youtube.py
```

---

## Dia 4 - Cartão de Visita Digital

Gera um cartão de visita em PNG a partir de dados informados pelo usuário.

- Coleta nome, profissão, e-mail, telefone e LinkedIn.
- Monta layout com ícones (e-mail, celular, LinkedIn) e logo Python.
- Salva imagem `cartao_nome.png` na pasta `dia-4/`.

**Bibliotecas usadas:** Pillow

**Arquivo principal:** `dia-4/dia04_cartao_visita_digital.py`

```bash
python dia-4/dia04_cartao_visita_digital.py
```

---

## Dia 5 - Fogos de Artifício com Turtle

Animação gráfica de fogos de artifício usando a biblioteca Turtle do Python.

- Tela preta com fogos coloridos em posições aleatórias.
- Sequência automática de 5 explosões com intervalo de 1 segundo.
- Cores variadas: vermelho, amarelo, laranja, azul, magenta, branco e verde.

**Bibliotecas usadas:** turtle (nativa do Python), random

**Arquivo principal:** `dia-5/dia05_fogos_artificio_turtle.py`

```bash
python dia-5/dia05_fogos_artificio_turtle.py
```

---

## Dia 6 - Conversor de Moedas (Terminal)

Conversor de BRL para outras moedas usando cotação em tempo real da AwesomeAPI.

- Moedas: USD, EUR, GBP, JPY e CAD.
- Menu interativo no terminal.
- Exibe valor convertido, taxa e data da última atualização.

**Bibliotecas usadas:** requests, datetime

**API:** `https://economia.awesomeapi.com.br/last/{moeda}-BRL`

**Arquivo principal:** `dia-6/dia06_conversor_moedas.py`

```bash
python dia-6/dia06_conversor_moedas.py
```

---

## Dia 7 - Conversor de Moedas (Interface Gráfica)

Versão desktop do Dia 6 com interface Tkinter.

- Campo para valor em BRL com suporte a formato brasileiro (vírgula).
- Seleção de moeda de destino em combobox.
- Exibe resultado da conversão com taxa e data de atualização.
- Mensagens de erro amigáveis via `messagebox`.

**Bibliotecas usadas:** tkinter, requests, datetime

**Arquivo principal:** `dia-7/dia07_conversor_moedas_gui.py`

```bash
python dia-7/dia07_conversor_moedas_gui.py
```

---

## Dia 8 - Conversor de Moedas (Web)

Versão web do conversor de moedas com Flask e formulário HTML.

- Formulário para valor em BRL e moeda de destino.
- Consulta a AwesomeAPI e exibe resultado na página.
- Tratamento de erros (valor inválido, falha na API).
- Template HTML em `dia-8/templates/index.html`.

**Bibliotecas usadas:** flask, requests, datetime

**Arquivo principal:** `dia-8/dia08_conversor_moedas_web.py`

```bash
cd dia-8
python dia08_conversor_moedas_web.py
```

Acesse: **http://127.0.0.1:5000**

---

## Dia 9 - Gráfico de Cotação de Moeda

Gera gráfico interativo da cotação histórica de moedas com Matplotlib.

- Moedas: USD, EUR, GBP, JPY e CAD.
- O usuário escolhe a moeda e quantidade de dias de histórico.
- Gráfico com hover mostrando data e valor ao passar o mouse.
- Salva imagem JPG automaticamente (`grafico_MOEDA_data.jpg`).

**Bibliotecas usadas:** matplotlib, requests, datetime, Pillow

**API:** `https://economia.awesomeapi.com.br/json/daily/{MOEDA}-BRL/{DIAS}`

**Arquivo principal:** `dia-9/dia09_grafico_moeda.py`

```bash
python dia-9/dia09_grafico_moeda.py
```

---

## Dia 10 - Baixar post do Instagram

Este projeto permite baixar o conteúdo (imagem, vídeo e legenda) de um post público do Instagram informando a URL. O download é feito via Instaloader e os arquivos são organizados na pasta `dia-10/downloaded_videos`.

- O usuário informa a URL do post.
- O script baixa a capa (imagem), vídeo (se houver) e legenda (exibida no terminal).
- Arquivos auxiliares (.json.xz) são removidos automaticamente.
- Menu interativo para abrir capa, vídeo ou exibir legenda.

**Bibliotecas usadas:** instaloader, os

**Arquivo principal:** `dia-10/dia10_instagram_downloader.py`

---

## Dia 11 - Baixar vídeo do X/Twitter

Este projeto permite baixar vídeos de posts públicos do X (antigo Twitter) informando a URL do tweet. Usa interface gráfica com Tkinter para uma experiência desktop.

- O usuário informa a URL do tweet na interface.
- O script baixa o vídeo em background usando yt-dlp.
- Barra de progresso e status durante o download.
- Vídeo salvo na pasta `dia-11/downloaded/`.
- Mensagem de confirmação com localização do arquivo.

**Bibliotecas usadas:** yt-dlp, tkinter, threading, queue

**Arquivo principal:** `dia-11/dia11_x_downloader.py`

---

## Dia 12 - Gerador de QR Code

Este projeto gera QR Codes a partir de texto ou links informados pelo usuário, com interface gráfica bonita.

- O usuário digita o texto/link na interface Tkinter.
- Geração em background com barra de progresso.
- QR Code exibido diretamente na tela (redimensionado).
- Arquivo salvo em `dia-12/qrcodes/` com nome único (timestamp) para evitar sobrescrever.
- Mensagem de confirmação com caminho do arquivo.

**Bibliotecas usadas:** qrcode, tkinter, Pillow, threading, queue

**Arquivo principal:** `dia-12/dia12_qrcode.py`

---

## Dia 13 - Gerador de Imagens com Inteligência Artificial

- Cria imagens a partir de prompts via OpenAI Image API (gpt-image-1 por padrão).
- Interface simples, suporta salvar automaticamente miniaturas e também gerar versões maiores.
- Permite escolher tamanho (512x512, 1024x1024, 1024x1536, 1536x1024 ou auto) e usa um overlay de aguarde.
- Salva imagens em `dia-13/outputs/` e oferece um diálogo para salvar versões maiores via Pillow.

**Dependências:** requests, Pillow, tkinter, python-dotenv

**Pré-requisitos:** Python 3.13.1 (recomendado)

**Configuração:**

1. Crie o `.venv` e ative:

   ```bash
   python -m venv .venv
   .venv\Scripts\Activate.ps1  # PowerShell
   ```

2. Instale o requisito geral (caso ainda não tenha):

   ```bash
   pip install -r requirements.txt
   ```

3. Copie `dia-13/.env.example` para `dia-13/.env`, configure `OPENAI_KEY` (obrigatório) e, se quiser, `OPENAI_IMAGE_MODEL`.

4. Execute o gerador:

   ```bash
   python dia-13/dia13_gerador_imagens.py
   ```

**Arquivo principal:** `dia-13/dia13_gerador_imagens.py`

---

## Dia 14 - Gerador de Assinatura

Este projeto permite desenhar uma assinatura com o mouse e exportá-la como PNG com fundo transparente, pronta para uso em documentos.

- Área de desenho com pré-visualização em tempo real.
- Escolha de cor (Preta e Azul BIC clássico `#005BAC`).
- Ajuste de espessura da ponta e seleção de 3 modelos de caneta (fina, normal, marcador).
- Botões para limpar, salvar PNG transparente e gerenciar assinaturas.

**Bibliotecas usadas:** tkinter, Pillow

**Arquivo principal:** `dia-14/dia14_gerador_assinatura.py`

Observação: `tkinter` geralmente já vem com o Python; a dependência externa necessária é `Pillow` (`pip install pillow`).

---

## Dia 15 - Top Dividendos B3 (Terminal)

Consulta o **dividend yield mensal estimado (DYm)** de ações e FIIs da B3 via Yahoo Finance, com menu interativo no terminal.

- Top 5 ações pagadoras do mês.
- Top 5 FIIs pagadores do mês.
- Top 5 geral (ações + FIIs).
- Lista de ativos configurável em `config.py` (`ACOES_LIST`, `FIIS_LIST`, `TOP_N`).

**Bibliotecas usadas:** yfinance

**Arquivo principal:** `dia-15/dia15_top_dividendos_b3.py`

```bash
cd dia-15
python dia15_top_dividendos_b3.py
```

---

## Dia 16 - Top Dividendos B3 (Windows)

Versão desktop do Dia 15 com interface gráfica Tkinter, barra de progresso e painel de logs em tempo real.

- Botões: Top 5 Ações, Top 5 FIIs e Top 5 Geral.
- Barra de progresso durante a busca nos ativos.
- Painel de logs e painel de resultados lado a lado.
- Logo personalizada na janela (`logo_escura.png`).
- Mesma configuração de ativos em `config.py` (lista reduzida para gravação mais rápida).

**Bibliotecas usadas:** tkinter, yfinance, threading, queue

**Arquivo principal:** `dia-16/dia16_top_dividendos_b3_windows.py`

```bash
cd dia-16
python dia16_top_dividendos_b3_windows.py
```

---

## Dia 17 - Top Dividendos B3 (Web)

Versão web do Dia 15/16 com Flask, Bootstrap e gráficos interativos no navegador.

- Interface web com Bootstrap 5 (via CDN).
- Barra de progresso animada e logs em tempo real (polling AJAX).
- Tabela com DYm%, preço e dividendo mensal estimado.
- Gráfico de barras (DYm% por ativo) e gráfico de pizza (distribuição do dividendo mensal) com Chart.js.
- Logo na navbar e favicon.

**Bibliotecas usadas:** flask, yfinance, threading

**Frontend (CDN):** Bootstrap 5, Chart.js

**Arquivo principal:** `dia-17/dia17_top_dividendos_b3_web.py`

```bash
cd dia-17
python dia17_top_dividendos_b3_web.py
```

Acesse: **http://127.0.0.1:5000**

---

## Dia 20 - Baixar Postagem do Instagram (Desktop)

Versão desktop e mais completa do downloader de Instagram, com interface gráfica Tkinter.

- Download de post por URL (imagem, vídeo e legenda).
- Barra de progresso e execução em background (threading).
- Galeria de downloads anteriores na própria interface.
- Pré-visualização de imagens com Pillow.
- Arquivos salvos em `dia-20/downloaded/`.
- Remove automaticamente arquivos auxiliares `.json.xz`.

**Bibliotecas usadas:** instaloader, Pillow, tkinter, threading, queue

**Arquivo principal:** `dia-20/dia20_instagram_desktop.py`

```bash
cd dia-20
python dia20_instagram_desktop.py
```

---

## Dia 21 - Login com SQLite

Sistema web de cadastro e login com banco de dados local SQLite e senhas protegidas por hash.

- Cadastro de usuário (nome, e-mail e senha).
- Login com sessão Flask (`session`) e área protegida (painel).
- Senha salva com hash via `werkzeug.security` — nunca em texto puro.
- Banco SQLite em `dia-21/database/app.db` (criado automaticamente na primeira execução).
- Interface com Bootstrap 5 (via CDN): login, cadastro e painel.
- Logout encerra a sessão e redireciona para o login.

**Bibliotecas usadas:** flask (inclui werkzeug para hash de senha)

**Padrão do Python (sem pip install):** sqlite3

**Frontend (CDN):** Bootstrap 5

**Arquivos principais:**

- `dia-21/dia21_app_login.py` — rotas Flask
- `dia-21/db.py` — conexão SQLite e funções de usuário
- `dia-21/config.py` — `SECRET_KEY` e caminho do banco

```bash
cd dia-21
python dia21_app_login.py
```

Acesse: **http://127.0.0.1:5000**

> **Dica:** se a API do Dia 20 estiver rodando na porta 5000, encerre-a antes ou altere a porta no `app.run()`.

---

## Dia 22 - Perfil do Usuário (CRUD + Foto)

Continua o Dia 21 e adiciona a área de **atualizar perfil**.

- Editar nome e e-mail.
- Atualizar senha (exige a senha atual).
- Cadastrar, trocar e remover foto de perfil.
- Fotos em `dia-22/static/uploads/` (pasta criada automaticamente).
- Nova coluna `foto` no SQLite (migração automática se o banco já existir).
- Avatar na navbar e no painel.

**Bibliotecas usadas:** flask (werkzeug: hash + `secure_filename`)

**Padrão do Python (sem pip install):** sqlite3

**Frontend (CDN):** Bootstrap 5

**Arquivos principais:**

- `dia-22/dia22_app_login.py` — rotas Flask + upload
- `dia-22/db.py` — banco + CRUD de perfil/senha/foto
- `dia-22/config.py` — `SECRET_KEY`, banco e regras de upload
- `dia-22/templates/perfil.html` — página de atualizar perfil

```bash
cd dia-22
python dia22_app_login.py
```

Acesse: **http://127.0.0.1:5000** → login → **Perfil**

---

## Dia 23 - Top Dividendos no Painel

Continua o Dia 22 e integra o scraper do Investidor10 **em tempo real** (sem salvar ranking no SQLite).

- Ao abrir o painel: **spinner Bootstrap** + carga via AJAX (`/api/top10`).
- **Top 10** = Top 5 FIIs + Top 5 Ações (só a 1ª página de cada ranking), ordenados por DY.
- Colunas: ativo, nome completo, tipo, DY e DY mensal estimado (anual / 12).
- Gráfico Chart.js ao lado; tooltip mostra ticker + tipo (FII/Ação).
- Meta: data no padrão BR (`14/07/2026 09:20:20`) + tempo de carregamento.
- Botões **Ver todos FIIs** / **Ver todas Ações**: scrape completo, busca e gráfico Top 15.
- Login, perfil e foto continuam iguais ao Dia 22.

**Bibliotecas usadas:** flask, requests, beautifulsoup4

**Padrão do Python (sem pip install):** sqlite3 (só usuários/perfil)

**Frontend (CDN):** Bootstrap 5, Bootstrap Icons, Chart.js

**Arquivos principais:**

- `dia-23/dia23_app.py` — app Flask (login + APIs + rankings)
- `dia-23/scraper/` — client + parser de rankings
- `dia-23/services/top_dividendos.py` — Top 10 misto e ranking completo
- `dia-23/templates/painel.html` / `rankings.html` — UI + gráficos

```bash
cd dia-23
python dia23_app.py
```

Acesse: **http://127.0.0.1:5000** (faça login; o Top 10 carrega sozinho)

---

## Dia 24 - Detalhe de FII e Ação

Continua o Dia 23 e adiciona a página de **detalhe do ativo** com scrape ao vivo.

- Clique no **ticker** nas tabelas (Top 10 e rankings) abre o detalhe.
- **Busca na navbar**: tipo (FII/Ação) + ticker → `/ativo/fii/HGLG11` ou `/ativo/acao/PETR4`.
- Layout diferente por tipo (cotação + informações do fundo **ou** empresa/ação).
- Spinner, data BR e tempo de carregamento (igual ao Dia 23).
- **Somente usuário logado** — não há API pública nem chave externa; `/api/ativo/...` exige sessão.

**Bibliotecas usadas:** flask, requests, beautifulsoup4

**Arquivos principais:**

- `dia-24/dia24_app.py` — rotas de detalhe e busca
- `dia-24/scraper/detalhe_fii.py` / `detalhe_acao.py` — scrapers
- `dia-24/services/detalhe_ativo.py` — monta resposta + tempo
- `dia-24/templates/ativo.html` — tela de detalhe

```bash
cd dia-24
python dia24_app.py
```

Acesse: **http://127.0.0.1:5000** (login obrigatório)

---

## Dia 25 - Busca com lista fixa de ativos

Continua o Dia 24. A busca na navbar usa uma **lista fixa** de FIIs e Ações (4 páginas de cada ranking do Investidor10).

- Digite o ticker ou nome → a lista filtra na hora.
- Clique (ou Enter) → abre o detalhe do ativo.
- Lista gerada uma vez em `ativos_lista.py` (não scrapa a cada busca).
- Para renovar a lista: `python temp/gerar_lista_ativos_dia25.py`
- **Calculadora de dividendos** (estilo Brapi light): aporte inicial/mensal, período, reinvestir, comparação IPCA+; DY e preço via scrape ao simular.

**Bibliotecas usadas:** flask, requests, beautifulsoup4

**Arquivos principais:**

- `dia-25/dia25_app.py` — app + busca + calculadora
- `dia-25/ativos_lista.py` — 460 ativos (FIIs + Ações)
- `dia-25/services/calculadora_dividendos.py` — simulação
- `dia-25/templates/calculadora.html` — tela da calculadora
- `dia-25/templates/base.html` — autocomplete da navbar

```bash
cd dia-25
python dia25_app.py
```

Acesse: **http://127.0.0.1:5000** (login obrigatório) · Calculadora: **/calculadora**

---

## Dia 26 - Carteiras (CRUD)

Continua o Dia 25. O usuário pode ter **várias carteiras** e registrar **lançamentos** (compra/venda).

- Criar / renomear / apagar carteira
- Adicionar lançamento: tipo (FII/Ação), ativo da lista fixa, data, quantidade, preço, outros custos
- Remover lançamento
- Venda não pode ultrapassar a quantidade líquida (compras − vendas)
- **Ainda sem** cotação ao vivo, gráfico, proventos ou % ideal (próximas etapas)

**Bibliotecas usadas:** flask, sqlite3

**Arquivos principais:**

- `dia-26/dia26_app.py` — rotas da carteira
- `dia-26/db_carteira.py` — tabelas `carteiras` + `lancamentos`
- `dia-26/templates/carteiras.html` — lista de carteiras
- `dia-26/templates/carteira_detalhe.html` — lançamentos + modal

```bash
cd dia-26
python dia26_app.py
```

Acesse: **http://127.0.0.1:5000** · Carteiras: **/carteiras**

---

## Dia 27 - Carteira completa (resumo + gráfico)

Continua o Dia 26. A carteira passa a **acompanhar** as posições com dados do Yahoo Finance.

- Cards: patrimônio, valor investido, lucro/prejuízo, rentabilidade %
- Tabela de **posições** (qtd, preço médio, preço atual, saldo, variação)
- Gráfico mensal: valor aplicado × patrimônio (Chart.js)
- Botão **Atualizar cotações**
- API: `/api/carteiras/<id>/acompanhamento`

**Bibliotecas usadas:** flask, yfinance, Chart.js

**Arquivos principais:**

- `dia-27/dia27_app.py`
- `dia-27/services/carteira_resumo.py`
- `dia-27/services/preco_yahoo.py`
- `dia-27/templates/carteira_detalhe.html`

```bash
cd dia-27
python dia27_app.py
```

Acesse: **http://127.0.0.1:5000** · Carteiras: **/carteiras**

---

## Dia 28 - Proventos, cache e painel

Continua o Dia 27.

- **Cache SQLite** (`cotacoes_historico`, `proventos_historico`, `mercado_sync`) — sync incremental Yahoo (só o que falta; 1 checagem/dia por ticker)
- **Dividendos recebidos** = qtd na data-ex × valor (Yahoo)
- Resumo: ganho de capital + dividendos (total e último) + lucro total
- **Gráficos**: evolução mensal (com dividendos do mês) + donut por valor investido
- Tabela **Proventos** na carteira (R$/cota com 4–6 casas)
- Avisos quando ativo ainda não gerou provento após a compra
- **Painel**: carteira padrão com resumo e gráficos; senão só Top 10
- Atalho **Inserir na carteira** (rankings, detalhe do ativo, Top 10)
- Botão **Atualizar cotações** força novo sync (`?forcar=1`)
- **Calculadora**: número mágico (cotas em que o dividendo do mês compra 1 cota nova)
- **Lista de ativos** completa (~587 FIIs + ~608 ações) via Status Invest — `ativos_lista.py` (script: `temp/tests/gerar_ativos_lista.py`)

**Arquivos principais:**

- `dia-28/dia28_app.py`
- `dia-28/db_mercado.py`
- `dia-28/ativos_lista.py`
- `dia-28/services/proventos_carteira.py`
- `dia-28/services/carteira_resumo.py`
- `dia-28/services/calculadora_dividendos.py`
- `dia-28/templates/painel.html` / `base.html` / `carteira_detalhe.html` / `calculadora.html` / `rankings.html` / `ativo.html`

```bash
cd dia-28
python dia28_app.py
```

**Segurança (antes de publicar):** bancos `.db`, `.env`, uploads de foto e pastas `outputs/` / `downloaded/` / `assinaturas/` ficam no `.gitignore`. As `SECRET_KEY` nos `config.py` são placeholders de estudo — troque no Dia 30 (deploy).

**Dia 29–30:** servidor e deploy (não novas features grandes).

---

## 🛠️ Como Usar

1. **Clone o repositório**

2. **Crie um ambiente virtual** (recomendado):

   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   ```

3. **Instale dependências**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Execute o projeto desejado**:

   ```bash
   python dia-1/dia01_filtro_camera.py
   python dia-2/dia02_texto_para_voz.py
   python dia-3/dia03_baixar_video_youtube.py
   python dia-4/dia04_cartao_visita_digital.py
   python dia-5/dia05_fogos_artificio_turtle.py
   python dia-6/dia06_conversor_moedas.py
   python dia-7/dia07_conversor_moedas_gui.py
   python dia-8/dia08_conversor_moedas_web.py
   python dia-9/dia09_grafico_moeda.py
   python dia-10/dia10_instagram_downloader.py
   python dia-11/dia11_x_downloader.py
   python dia-12/dia12_qrcode.py
   python dia-13/dia13_gerador_imagens.py
   python dia-14/dia14_gerador_assinatura.py
   python dia-15/dia15_top_dividendos_b3.py
   python dia-16/dia16_top_dividendos_b3_windows.py
   python dia-17/dia17_top_dividendos_b3_web.py
   python dia-20/dia20_instagram_desktop.py
   python dia-21/dia21_app_login.py
   python dia-22/dia22_app_login.py
   python dia-23/dia23_app.py
   python dia-24/dia24_app.py
   python dia-25/dia25_app.py
   python dia-26/dia26_app.py
   python dia-27/dia27_app.py
   python dia-28/dia28_app.py
   ```

## 📚 Tecnologias e Bibliotecas

- **Python 3.x**
- **Tkinter** (interfaces gráficas desktop)
- **Flask** (aplicações web)
- **SQLite / sqlite3** (usuários/perfil — Dias 21–23; rankings do Dia 23 são ao vivo)
- **Werkzeug** (hash de senha + upload — instalado automaticamente com o Flask)
- **Requests** (APIs HTTP)
- **OpenCV** (visão computacional)
- **Pytubefix** (YouTube)
- **Matplotlib** (gráficos desktop)
- **Chart.js / Bootstrap / Bootstrap Icons** (interface web — CDN; Dias 17 e 21–23)
- **BeautifulSoup4** (scraper HTML — Dias 18–20 e 23)
- **yfinance** (cotações e dividendos B3)
- **Instaloader** (Instagram)
- **yt-dlp** (X/Twitter e multi-site downloader)
- **qrcode** (gerar QR Codes)
- **Pillow** (manipulação de imagens)
- **sounddevice / numpy** (afinador de violão — pasta extra)
- **pyttsx3** (texto para voz)

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

#30DiasDeCodigo #Python #Aprendizado

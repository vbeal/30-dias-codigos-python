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

## Dia 9 - Gráfico de Cotação de Moeda

Este projeto gera um gráfico interativo da cotação de moedas (USD, EUR, GBP, JPY, CAD) em relação ao Real (BRL) usando dados da AwesomeAPI.

- O usuário escolhe a moeda e o período (em dias) para consulta.
- O gráfico exibe os valores históricos, com tooltip ao passar o mouse sobre cada ponto.
- O arquivo do gráfico é salvo automaticamente em JPG com nome único (moeda + data/hora).
- Para salvar em JPG, é necessário ter o Pillow instalado (`pip install pillow`).
- O botão "Salvar" do matplotlib pode não mostrar JPG/JPEG em alguns sistemas; use o PNG ou salve via código.

**Bibliotecas usadas:**

- matplotlib
- requests
- datetime
- pillow

**API:**

- https://economia.awesomeapi.com.br/json/daily/{MOEDA}-BRL/{DIAS}

Arquivo principal: `dia-9/dia09_grafico_moeda.py`

## 🛠️ Como Usar

1. **Clone o repositório**:

   ```bash
   git clone https://github.com/vbeal/30-dias-codigos-python.git
   cd 30-dias-codigos-python
   ```

2. **Crie um ambiente virtual** (recomendado):

   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   ```

3. **Instale dependências** (se necessário):

   ```bash
   pip install -r requirements.txt
   ```

4. **Execute um código**:
   ```bash
   python dia-1/dia01_filtro_camera.py
   ```

## 📚 Tecnologias e Bibliotecas

- **Python 3.x**
- **Tkinter** (interfaces gráficas)
- **Requests** (APIs)
- **OpenCV** (visão computacional)
- **Pytube/Pytubefix** (YouTube)
- **Matplotlib** (gráficos)

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

# ################################################
# 🎯 Projeto: Cartão de Visita Digital com Ícones e Logo
# ################################################
# 📁 Caminho: dia-4/dia04_cartao_visita_digital.py
# Desafio 30 dias com Python por Victor Beal
# ################################################

from PIL import Image, ImageDraw, ImageFont
import os

# Diretórios
base_dir = os.path.dirname(__file__)
icones_dir = os.path.join(base_dir, "icones")

# Dados do cartão
nome = input("Digite seu nome: ")
profissao = input("Digite sua profissão: ")
email = input("Digite seu e-mail: ")
telefone = input("Digite seu telefone: ")
linkedin = input("Digite seu LinkedIn (ex: linkedin.com/in/seunome): ")

# Criar imagem base
largura, altura = 600, 350
cor_fundo = (255, 255, 255)
cor_texto = (0, 0, 0)
cor_borda = (0, 0, 0)

imagem = Image.new("RGB", (largura, altura), cor_fundo)
desenho = ImageDraw.Draw(imagem)

# Borda
desenho.rectangle([(0, 0), (largura - 1, altura - 1)], outline=cor_borda, width=3)

# Fontes
try:
    fonte_titulo = ImageFont.truetype("arial.ttf", 28)
    fonte_texto = ImageFont.truetype("arial.ttf", 20)
except:
    fonte_titulo = ImageFont.load_default()
    fonte_texto = ImageFont.load_default()

# Ícones com tratamento de transparência
def carregar_icone(nome_arquivo, tamanho):
    caminho = os.path.join(icones_dir, nome_arquivo)
    imagem = Image.open(caminho).resize(tamanho)
    return imagem.convert("RGBA")

icon_email = carregar_icone("email.png", (24, 24))
icon_phone = carregar_icone("celular.png", (24, 24))
icon_linkedin = carregar_icone("linkedin.png", (24, 24))
logo_python = carregar_icone("python.png", (80, 80))

# Inserir logo com máscara de transparência
imagem.paste(logo_python, (30, 30), logo_python)

# Inserir textos e ícones
desenho.text((130, 40), nome, font=fonte_titulo, fill=cor_texto)
desenho.text((130, 90), profissao, font=fonte_texto, fill=cor_texto)

imagem.paste(icon_email, (130, 150), icon_email)
desenho.text((165, 150), email, font=fonte_texto, fill=cor_texto)

imagem.paste(icon_phone, (130, 190), icon_phone)
desenho.text((165, 190), telefone, font=fonte_texto, fill=cor_texto)

imagem.paste(icon_linkedin, (130, 230), icon_linkedin)
desenho.text((165, 230), linkedin, font=fonte_texto, fill=cor_texto)

# Salvar imagem no mesmo diretório
nome_arquivo = os.path.join(base_dir, f"cartao_{nome.lower().replace(' ', '_')}.png")
imagem.save(nome_arquivo)
print(f"✅ Cartão salvo como: {nome_arquivo}")
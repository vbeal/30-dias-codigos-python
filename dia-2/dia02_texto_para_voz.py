# ################################################
# 🎯 Projeto: Conversor de Texto para Voz com Estilo
# ################################################
# 📁 Caminho: dia-2/dia02_texto_para_voz.py
# Desafio 30 dias com Python por Victor Beal
# ################################################

import pyttsx3

# Inicializa o motor de síntese de voz
engine = pyttsx3.init()

# Configuração de voz
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id) # Troque para voices[1].id para voz feminina
engine.setProperty('rate', 150) # Velocidade da fala
engine.setProperty('volume', 1.0) # Volume (0.0 a 1.0)


# Entrada do Usuário

text = input("Digite o texto que você quer ouvir em voz robótica:   ")

#fala o texto
engine.say(text)
engine.runAndWait()
engine.stop()

# Fim do código
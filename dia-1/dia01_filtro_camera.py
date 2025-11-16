# ################################################
# 🎯 Projeto: Filtro de Câmera Estilo Instagram
# ################################################
# 📁 Caminho: dia-1/dia01_filtro_camera.py
# Desafio 30 dias com Python por Victor Beal
# ################################################


import cv2
import numpy as np

# Lista de filtros disponíveis
def apply_filter(frame, mode):
    if mode ==1: # Preto e Branco'
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    elif mode == 2: # Sepia
        sepia_filter = np.array([[0.272, 0.534, 0.131],
                                 [0.349, 0.686, 0.168],
                                 [0.393, 0.769, 0.189]])
        sepia = cv2.transform(frame, sepia_filter)
        return cv2.convertScaleAbs(sepia)
    elif mode == 3: # Negativo

        return cv2.bitwise_not(frame)
    
    elif mode == 4: # Azul neon

        return cv2.applyColorMap(frame, cv2.COLORMAP_OCEAN)
    else: # Sem filtro
        return frame

# INicializa a câmeta

print("🔍 Tentando abrir a câmera...")
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Erro: Não foi possível acessar a webcam. Verifique se ela está conectada e não está em uso por outro programa.")
    exit(1)
else:
    print("✅ Webcam aberta com sucesso!")
filter_mode = 0

print("Pressione 1-4 para mudar o filtro, 0 para sem filtro e 'q' para sair.")

while True:
    ret, frame = cap.read()
    print(f"Frame capturado: {ret}")
    if not ret:
        print("❌ Não foi possível capturar frame da webcam.")
        break

    # Aplicar o filtro selecionado
    filtered = apply_filter(frame, filter_mode)

    # Se for preto e branco, converte para 3 canais para exibir corretamente
    if filter_mode == 1:
        filtered = cv2.cvtColor(filtered, cv2.COLOR_GRAY2BGR)

    cv2.imshow('Filtro de Câmera - Dia 1', filtered)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key in [ord('1'), ord('2'), ord('3'), ord('4')]:
        filter_mode = int(chr(key))

cap.release()
cv2.destroyAllWindows()
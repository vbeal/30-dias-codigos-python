# ###################################################################
#           🎯 Projeto: Gráfico de Cotação de Moeda - Matplotlib    #
# ###################################################################
# 📁 Caminho: dia-9/dia09_grafico_moeda.py
# Desafio 30 dias com Python por Victor Beal
# ###################################################################
# 📚 Bibliotecas: matplotlib (gráficos), requests (API), 
# datetime (datas), pillow (salvar JPG)
# 🛠️  API: AwesomeAPI (gratuita, sem chave)
# 📊 Cotação: Consulta histórica de moeda em dias
# 🔗 API usada: https://economia.awesomeapi.com.br/json/daily/{MOEDA}-BRL/{DIAS}
#####################################################################

import requests
import matplotlib.pyplot as plt
from datetime import datetime

MOEDAS = ['USD', 'EUR', 'GBP', 'JPY', 'CAD']

def obter_cotacoes(moeda, dias):
    url = f'https://economia.awesomeapi.com.br/json/daily/{moeda}-BRL/{dias}'
    response = requests.get(url)
    response.raise_for_status()
    dados = response.json()
    datas = [datetime.fromtimestamp(int(item['timestamp'])).strftime('%d/%m/%y') for item in dados[::-1]]
    valores = [float(item['bid']) for item in dados[::-1]]
    return datas, valores

def main():
    print('💹 Gráfico de Cotação de Moeda')
    print('Moedas disponíveis:')
    for idx, m in enumerate(MOEDAS, 1):
        print(f'  {idx}. {m}')
    escolha = input('Escolha a moeda (1-5): ').strip()
    if escolha not in [str(i) for i in range(1, 6)]:
        print('❌ Opção inválida.')
        return
    moeda = MOEDAS[int(escolha)-1]
    dias = input('Quantos dias de histórico? (ex: 7, 15, 30): ').strip()
    if not dias.isdigit() or int(dias) < 1:
        print('❌ Número de dias inválido.')
        return
    dias = int(dias)
    try:
        datas, valores = obter_cotacoes(moeda, dias)
        fig, ax = plt.subplots(figsize=(10,5))
        fig.canvas.manager.set_window_title('Gráfico de Cotação de Moeda')
        pontos, = ax.plot(datas, valores, marker='o', color='blue', linestyle='-')
        plt.title(f'Cotação {moeda}-BRL últimos {dias} dias')
        plt.xlabel('Data')
        plt.ylabel(f'Valor {moeda} em BRL')
        plt.grid(True)
        plt.xticks(fontsize=8)  # Diminui o tamanho da fonte das datas
        plt.tight_layout()

        # Adiciona anotação dinâmica
        annot = ax.annotate("", xy=(0,0), xytext=(15,15), textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w"), arrowprops=dict(arrowstyle="->"))
        annot.set_visible(False)

        def update_annot(ind):
            x, y = pontos.get_xdata()[ind[0]], pontos.get_ydata()[ind[0]]
            annot.xy = (x, y)
            text = f"{x}: R$ {y:.2f}"
            annot.set_text(text)
            annot.get_bbox_patch().set_facecolor('yellow')
            annot.get_bbox_patch().set_alpha(0.8)

            # Centraliza a anotação se estiver nos extremos
            if ind[0] == 0:
                annot.set_ha('left')
                annot.set_va('center')
                annot.xytext = (15, 15)
            elif ind[0] == len(datas)-1:
                annot.set_ha('right')
                annot.set_va('center')
                annot.xytext = (-15, 15)
            else:
                annot.set_ha('center')
                annot.set_va('bottom')
                annot.xytext = (0, 20)

        def hover(event):
            vis = annot.get_visible()
            if event.inaxes == ax:
                for i, (x, y) in enumerate(zip(datas, valores)):
                    if abs(event.xdata - i) < 0.4 and abs(event.ydata - y) < 0.4:
                        update_annot([i])
                        annot.set_visible(True)
                        fig.canvas.draw_idle()
                        return
            if vis:
                annot.set_visible(False)
                fig.canvas.draw_idle()

        fig.canvas.mpl_connect("motion_notify_event", hover)
        # Para salvar em JPG, Pillow precisa estar instalado:
        # pip install pillow
        nome_arquivo = f"grafico_{moeda}_{datetime.now().strftime('%d%m%y_%H%M%S')}.jpg"
        plt.savefig(nome_arquivo, format='jpg')
        plt.show()
    except Exception as e:
        print(f'❌ Erro ao gerar gráfico: {e}')

if __name__ == '__main__':
    main()

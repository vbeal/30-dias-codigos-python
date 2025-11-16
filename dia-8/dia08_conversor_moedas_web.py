# ###################################################################
#           🎯 Projeto: Conversor de Moedas Web - Flask     #
# ###################################################################
# 📁 Caminho: dia-8/dia08_conversor_moedas_web.py
# Desafio 30 dias com Python por Victor Beal
# ###################################################################
# 📚 Bibliotecas: flask (web framework), requests (API), datetime (datas)
# 🛠️  API: AwesomeAPI (gratuita, sem chave)
# 📊 Conversão: De BRL para USD, EUR, GBP, JPY, CAD
# 🔗 API usada: https://economia.awesomeapi.com.br/last/{moeda}-BRL
# 🌐 Web: Aplicação Flask com formulário HTML
#####################################################################

from flask import Flask, render_template, request
import requests
from datetime import datetime

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    resultado = None
    if request.method == 'POST':
        try:
            # Pegar dados do formulário
            valor_brl = float(request.form['valor'].replace(',', '.'))
            moeda_destino = request.form['moeda']
            
            # Requisição para a API
            url = f'https://economia.awesomeapi.com.br/last/{moeda_destino}-BRL'
            response = requests.get(url)
            response.raise_for_status()
            
            # Extrair dados
            dados = response.json()
            chave = f'{moeda_destino}BRL'
            taxa = float(dados[chave]['bid'])
            
            # Cálculo da conversão
            valor_convertido = valor_brl / taxa
            
            # Converter data para formato brasileiro
            data_original = dados[chave]["create_date"]
            data_obj = datetime.strptime(data_original, "%Y-%m-%d %H:%M:%S")
            data_brasil = data_obj.strftime("%d/%m/%Y %H:%M:%S")
            
            resultado = {
                'valor_brl': f"{valor_brl:.2f}",
                'valor_convertido': f"{valor_convertido:.2f}",
                'moeda': moeda_destino,
                'taxa': f"{taxa:.4f}",
                'data': data_brasil
            }
            
        except ValueError:
            resultado = {'erro': 'Digite um valor numérico válido.'}
        except requests.exceptions.RequestException:
            resultado = {'erro': 'Erro na conexão com a API.'}
        except Exception as e:
            resultado = {'erro': f'Erro inesperado: {str(e)}'}
    
    return render_template('index.html', resultado=resultado)

if __name__ == '__main__':
    app.run(debug=True)
###################################################
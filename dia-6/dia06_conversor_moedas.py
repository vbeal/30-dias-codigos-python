# ###################################################################
#           🎯 Projeto: Conversor de Moedas Simples                 #
# ###################################################################
# 📁 Caminho: dia-6/dia06_conversor_moedas.py
# Desafio 30 dias com Python por Victor Beal
# ###################################################################
# 📚 Bibliotecas: requests (para requisições HTTP)
# 🛠️  API: AwesomeAPI (gratuita, sem chave)
# 📊 Conversão: De BRL para USD, EUR, GBP, JPY, CAD
# 🔗 API usada: https://economia.awesomeapi.com.br/last/{moeda}-BRL
#####################################################################

import requests
from datetime import datetime

def converter_moeda():
    # Lista de moedas disponíveis (código e nome)
    moedas_codigos = {
        '1': 'USD',
        '2': 'EUR',
        '3': 'GBP',
        '4': 'JPY',
        '5': 'CAD'
    }
    
    moedas_nomes = {
        'USD': 'USD (Dólar Americano)',
        'EUR': 'EUR (Euro)',
        'GBP': 'GBP (Libra Esterlina)',
        'JPY': 'JPY (Iene Japonês)',
        'CAD': 'CAD (Dólar Canadense)'
    }
    
    print('💰 Conversor de Moedas - De BRL para outras moedas')
    print('📋 Moedas disponíveis:')
    for key, codigo in moedas_codigos.items():
        print(f'   {key}. {moedas_nomes[codigo]}')
    
    # Entrada do usuário
    valor_brl = float(input('\n💵 Digite o valor em BRL (ex: 100): '))
    escolha = input('🔄 Escolha a moeda de destino (1-5): ').strip()
    
    if escolha not in moedas_codigos:
        print('❌ Opção inválida.')
        return
    
    moeda_destino = moedas_codigos[escolha]
    
    try:
        # Requisição para a API
        url = f'https://economia.awesomeapi.com.br/last/{moeda_destino}-BRL'
        response = requests.get(url)
        response.raise_for_status()
        
        # Extrair dados
        dados = response.json()
        chave = f'{moeda_destino}BRL'
        taxa = float(dados[chave]['bid'])
        nome_moeda = dados[chave]['name']
        
        # Cálculo da conversão
        valor_convertido = valor_brl / taxa
        
        # Converter data para formato brasileiro
        data_original = dados[chave]["create_date"]
        data_obj = datetime.strptime(data_original, "%Y-%m-%d %H:%M:%S")
        data_brasil = data_obj.strftime("%d/%m/%Y %H:%M:%S")
        
        print(f'\n✅ Conversão:')
        print(f'   {valor_brl:.2f} BRL = {valor_convertido:.2f} {moeda_destino}')
        print(f'   Taxa atual: 1 {moeda_destino} = {taxa:.4f} BRL')
        print(f'   Última atualização: {data_brasil}')
        
    except requests.exceptions.RequestException as e:
        print(f'❌ Erro na conexão com a API: {e}')
    except KeyError as e:
        print(f'❌ Erro nos dados da API: {e}')
    except Exception as e:
        print(f'❌ Erro inesperado: {e}')

if __name__ == '__main__':
    converter_moeda()
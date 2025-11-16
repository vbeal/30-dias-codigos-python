# ###################################################################
#           🎯 Projeto: Conversor de Moedas - Interface Gráfica     #
# ###################################################################
# 📁 Caminho: dia-7/dia07_conversor_moedas_gui.py
# Desafio 30 dias com Python por Victor Beal
# ###################################################################
# 📚 Bibliotecas: tkinter (interface gráfica), requests (API), datetime (datas)
# 🛠️  API: AwesomeAPI (gratuita, sem chave)
# 📊 Conversão: De BRL para USD, EUR, GBP, JPY, CAD
# 🔗 API usada: https://economia.awesomeapi.com.br/last/{moeda}-BRL
# 🎨 Interface: Tkinter com entrada formatada para centavos
#####################################################################

import tkinter as tk
from tkinter import messagebox
import requests
from datetime import datetime

def converter_moeda():
    try:
        # Aceitar entrada com vírgula (formato brasileiro) e converter para float
        valor_str = entry_valor.get().strip()
        if not valor_str or valor_str == '0,00':
            messagebox.showerror("Erro", "Digite um valor válido.")
            return
        valor_str = valor_str.replace('.', '').replace(',', '.')  # Remover pontos de milhar e trocar vírgula por ponto
        valor_brl = float(valor_str)
        moeda_destino = var_moeda.get()
        
        if not moeda_destino:
            messagebox.showerror("Erro", "Selecione uma moeda de destino.")
            return
        
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
        
        # Exibir resultado
        resultado = f"{valor_brl:.2f} BRL = {valor_convertido:.2f} {moeda_destino}\nTaxa: 1 {moeda_destino} = {taxa:.4f} BRL\nAtualizado: {data_brasil}"
        label_resultado.config(text=resultado)
        
    except ValueError:
        messagebox.showerror("Erro", "Digite um valor numérico válido.")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Erro", f"Erro na API: {e}")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro inesperado: {e}")

# Criar janela principal
root = tk.Tk()
root.title("💰 Conversor de Moedas - Interface Gráfica")
root.geometry("450x350")

# Lista de moedas
moedas = ['USD', 'EUR', 'GBP', 'JPY', 'CAD']

# Widgets
tk.Label(root, text="💵 Valor em BRL (digite com vírgula, ex: 100,50):").pack(pady=5)
entry_valor = tk.Entry(root)
entry_valor.pack(pady=5)
entry_valor.insert(0, "")  # Campo vazio para digitação livre

tk.Label(root, text="🔄 Moeda de destino:").pack(pady=5)
var_moeda = tk.StringVar()
option_menu = tk.OptionMenu(root, var_moeda, *moedas)
option_menu.pack(pady=5)

tk.Button(root, text="✅ Converter", command=converter_moeda).pack(pady=10)

label_resultado = tk.Label(root, text="", justify=tk.LEFT)
label_resultado.pack(pady=10)

# Iniciar loop da interface
root.mainloop()
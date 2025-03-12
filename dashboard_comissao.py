import streamlit as st
import pandas as pd

def format_currency(value):
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def calcular_comissao(faturamento, margem_operacional):
    comissao_bruta = faturamento * 0.30
    
    # Determinar o multiplicador baseado na margem operacional
    if margem_operacional > 50:
        multiplicador = 1.2
        regra = "MO > 50% (120%)"
    elif 46 <= margem_operacional <= 50:
        multiplicador = 1.0
        regra = "MO entre 46% e 50% (100%)"
    elif 41 <= margem_operacional <= 45:
        multiplicador = 0.75
        regra = "MO entre 41% e 45% (75%)"
    else:
        multiplicador = 0.50
        regra = "MO <= 40% (50%)"
    
    comissao_final = comissao_bruta * multiplicador
    return comissao_final, regra

# Criando o dashboard
st.title("Calculadora de Comissão")
st.markdown("Insira os valores abaixo ou faça o upload de um Excel para calcular sua comissão.")

# Inputs do usuário
faturamento = st.number_input("Faturamento (R$)", min_value=0.0, format="%.2f")
custo = st.empty()
margem = st.empty()

input_custo = custo.number_input("Custo (R$) (Deixe vazio se for informar a margem)", min_value=0.0, format="%.2f", value=0.0)
input_margem = margem.number_input("Margem Operacional (%) (Deixe vazio se for informar o custo)", min_value=0.0, max_value=100.0, format="%.2f", value=0.0)

# Calcular automaticamente o custo ou a margem operacional
if faturamento > 0:
    if input_custo > 0:
        margem_operacional = ((faturamento - input_custo) / faturamento) * 100
        input_margem = margem.number_input("Margem Operacional (%) (Deixe vazio se for informar o custo)", value=margem_operacional, min_value=0.0, max_value=100.0, format="%.2f")
    elif input_margem > 0:
        input_custo = faturamento * (1 - (input_margem / 100))
        input_custo = custo.number_input("Custo (R$) (Deixe vazio se for informar a margem)", value=input_custo, min_value=0.0, format="%.2f")
    
    comissao_final, regra = calcular_comissao(faturamento, input_margem)
    
    # Exibir os resultados
    st.subheader("Resultados")
    st.write(f"**Custo Calculado:** {format_currency(input_custo)}")
    st.write(f"**Margem Operacional:** {input_margem:.2f}%")
    st.write(f"**Comissão Final:** {format_currency(comissao_final)}")
    st.write(f"**Regra Aplicada:** {regra}")

# Upload de arquivo Excel
st.subheader("Upload de Excel para Cálculo em Massa")
st.markdown("**O arquivo Excel deve conter as seguintes colunas:**")
st.markdown("- `Valor mês` → Representa o faturamento da venda.")
st.markdown("- `Margem Vendida %` → Representa a margem operacional da venda.")
file = st.file_uploader("Envie um arquivo Excel", type=["xlsx"])

if file:
    df = pd.read_excel(file)
    df.columns = df.columns.str.strip()  # Remover espaços extras nos nomes das colunas
    
    if "Valor mês" in df.columns and "Margem Vendida %" in df.columns:
        df["Comissão Final"], df["Regra Aplicada"] = zip(*df.apply(lambda row: calcular_comissao(row["Valor mês"], row["Margem Vendida %"] * 100), axis=1))
        total_comissao = df["Comissão Final"].sum()
        
        # Exibir apenas o valor final de cada comissão
        st.subheader("Comissões Calculadas")
        for index, row in df.iterrows():
            st.write(f"Venda {index + 1}: {format_currency(row['Comissão Final'])}")
        
        # Exibir o total
        st.subheader("Total de Comissões")
        st.write(f"**{format_currency(total_comissao)}**")
    else:
        st.error("O arquivo deve conter as colunas 'Valor mês' e 'Margem Vendida %'.")

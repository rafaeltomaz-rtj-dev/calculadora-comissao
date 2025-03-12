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
st.markdown("- `Pagamento` → Status da comissão ('Pago', 'Pago Parcialmente', 'Não Pago').")
st.markdown("- `Valor Pago` → Se 'Pago Parcialmente', informar o valor já pago.")
file = st.file_uploader("Envie um arquivo Excel", type=["xlsx"])

if file:
    df = pd.read_excel(file)
    df.columns = df.columns.str.strip()
    
    if "Valor mês" in df.columns and "Margem Vendida %" in df.columns and "Pagamento" in df.columns and "Valor Pago" in df.columns:
        df_filtrado = df[df["Pagamento"] != "Pago"].copy()  # Ignorar pagamentos já quitados
        
        df_filtrado["Comissão Final"], df_filtrado["Regra Aplicada"] = zip(*df_filtrado.apply(lambda row: calcular_comissao(row["Valor mês"], row["Margem Vendida %"] * 100), axis=1))
        df_filtrado["Valor Pago"] = pd.to_numeric(df_filtrado["Valor Pago"], errors='coerce').fillna(0)
        df_filtrado["Comissão a Receber"] = df_filtrado["Comissão Final"] - df_filtrado["Valor Pago"]
        total_comissao = df_filtrado["Comissão a Receber"].sum()
        
        # Exibir apenas os valores finais e um resumo
        st.subheader("Comissões Calculadas")
        for index, row in df_filtrado.iterrows():
            status = f"(Restante: {format_currency(row['Comissão a Receber'])})" if row["Pagamento"] == "Pago Parcialmente" else ""
            st.write(f"Venda {index + 1}: {format_currency(row['Comissão Final'])} {status}")
        
        st.subheader("Resumo")
        st.write(f"**Comissões Ignoradas (Pagos):** {len(df) - len(df_filtrado)}")
        st.write(f"**Comissões Processadas:** {len(df_filtrado)}")
        st.write(f"**Total de Comissões a Receber:** {format_currency(total_comissao)}")
    else:
        st.error("O arquivo deve conter as colunas 'Valor mês', 'Margem Vendida %', 'Pagamento' e 'Valor Pago'.")

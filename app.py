import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Aplicação Modbus",
    page_icon="🔌",
    layout="centered"
)

# Título da aplicação
st.title("Aplicação Modbus")

# Campo de entrada para o código
codigo = st.text_input("Código")

# Exibir o código inserido (opcional - apenas para demonstração)
if codigo:
    st.write(f"Código inserido: {codigo}")

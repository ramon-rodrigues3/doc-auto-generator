import streamlit as st
from generator import arquivo_gerado

def main():
    st.header("Baixar arquivo")
    nome_arquivo = st.session_state.get("nome_arquivo", 'arquivo')
    nome_input = st.text_input('Nome do arquivo', value=nome_arquivo)

    if nome_input:
        nome_arquivo = nome_input
        st.session_state['nome_arquivo'] = nome_arquivo
    download_buttom = st.download_button('Baixar arquivo', arquivo_gerado(), file_name=f'{nome_arquivo}.txt')

if __name__ == "__main__":
    main()
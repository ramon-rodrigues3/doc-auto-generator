import streamlit as st
from document import get_document

def main():
    st.header("Baixar arquivo")

    extensao = st.selectbox('Extensao', ['txt', 'pdf'])

    nome_arquivo = st.session_state.get("nome_arquivo", 'arquivo')
    nome_input = st.text_input('Nome do arquivo', value=nome_arquivo)

    if nome_input:
        nome_arquivo = nome_input
        st.session_state['nome_arquivo'] = nome_arquivo

    download_buttom = st.download_button('Baixar arquivo', get_document(extensao), file_name=f'{nome_arquivo}.{extensao}')

if __name__ == "__main__":
    main()
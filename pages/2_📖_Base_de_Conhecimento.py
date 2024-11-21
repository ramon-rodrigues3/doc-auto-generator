import streamlit as st
from assistant import Assistant
from time import sleep
assistant = Assistant("asst_WolVDtnyp76KF2BPpz8TFqnP")

def gui_upload():
    st.subheader('Upload de arquivos')
    st.markdown('Faça upload dos seus arquivos para o conhecimento da IA')

    arquivos = st.file_uploader(
        'Arquivos para upload', type=['txt', 'docx', 'pdf'], 
        accept_multiple_files=True, key='uploader'
    )
    confirmar_button = st.button('Enviar arquivos')

    if confirmar_button:
        for arquivo in arquivos:
            arquivo.mode = 'rb'
        update = assistant.update_vector(arquivos, 'vs_oa9rE8zahOHVMVp2kukHRhRK')

        if update:
            st.write("Upload feito com sucesso!")
        else:
            st.write("Houve algum erro ao enviar os arquivos")

def gui_delete():
    st.subheader('Exclusão de arquivos')
    st.markdown('Remova arquivos do conhecimento da IA')
    files = assistant.list_files('vs_oa9rE8zahOHVMVp2kukHRhRK')
    arquivo = st.selectbox('Arquivo a ser removido',
        [file.id for file in files]
    )

    deletar_btn = st.button("Remover")

    if deletar_btn and arquivo:
        sucesso = assistant.remove_file(arquivo)

        if sucesso:
            st.write("Exclusão realizada com sucesso")
            sleep(2)
            st.rerun()
        else:
            st.write("Problema na exclusão")


def main():
    st.header("Base de Conhecimento",divider='gray')
    colunas = st.columns(2, gap='large')

    with colunas[0]:
        gui_upload()

    with colunas[1]:
        gui_delete()

if __name__ == "__main__":
    main()
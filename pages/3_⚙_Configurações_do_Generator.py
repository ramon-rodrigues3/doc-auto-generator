import streamlit as st
from assistant import Assistant
def main():
    st.header("Configurações do Generator")
    assistant = Assistant("asst_WolVDtnyp76KF2BPpz8TFqnP")
    valores_salvos = assistant.get()
    print(valores_salvos)

    nova_descricao = st.text_area('Descrição do Assistant', value= valores_salvos.description, key='description')
    nova_instrucao = st.text_area('Descrição do Assistant', value= valores_salvos.instructions, key='instructions')
    nova_temperatura = st.number_input('Temperatura do Assistant', min_value=0.0, max_value=2.0, value=valores_salvos.temperature)
    
    salvar = st.button('Salvar Mudanças')

    if salvar:
        response = assistant.update(
            description=nova_descricao,
            instructions=nova_instrucao,
            temperature=nova_temperatura
        )

        if response:
            st.write("Atualizado com sucesso!")
        else:
            st.write("Erro ao atualizar")

if __name__ == "__main__":
    main()
import streamlit as st
import generator, auto
from openai import OpenAI
from assistant import Topico

def gui_auto():
    client = OpenAI()
    tools = generator.tools
    chat_container = st.container()

    mensagens = st.session_state.get('mensagens',[
        {"role": "system", "content": "Use as calls functions para atender aos pedidos dos usuários. Primeiro pense em uma sequência de ações de call functions que resolve a demanda do usuário e em seguida chame-as functions passo a passo."}
    ])

    for mensagem in mensagens:
        if mensagem['content'] == None:
            continue

        if 'user' != mensagem['role'] != 'assistant':
            continue

        with chat_container.chat_message(mensagem['role']):
            st.markdown(mensagem['content'])
    
    pergunta = st.chat_input('Sua mensagem')
 
    if pergunta:
        chat = chat_container.chat_message('user')
        chat.markdown(pergunta)
        
        mensagens.append({
            "role": "user",
            "content": pergunta
        })
        
        while True:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=mensagens,
                tools=tools,
                tool_choice="auto"
            ).choices[0].message

            if response.content:
                chat = chat_container.chat_message('assistant')
                chat.markdown(response.content)
    
            mensagens.append(response.to_dict())
                
            if response.tool_calls:
                tools_p = response.tool_calls

                for tool in tools_p:
                    chat = chat_container.chat_message('Tool', avatar='🛠')
                    chat.write(f"Rodando {tool.function.name}")
                    mensagens.append(auto.rodar_tool_call(tool))
            else: break
        st.session_state['mensagens'] = mensagens

        #st.rerun()

def gui_generator():
    arquivo = st.session_state.get('arquivo', generator.texto_gerado)
    st.session_state['arquivo'] = arquivo
    generator.set_arquivo(arquivo)

    for i, topico in enumerate(arquivo):
        st.markdown(f'# Topico {i}')
        for i, sub in enumerate(topico):
            st.markdown(f'## Sub-Tópico {i}')
            for i, par in enumerate(sub):
                st.markdown(f'{i}. {par}')

def main():
    st.header("Document Auto-Generator")

    tabs = st.tabs(["AUTO", "GENERATOR"])

    with tabs[0]:
        gui_auto()

    with tabs[1]:
        gui_generator()

if __name__ == "__main__":
    main()
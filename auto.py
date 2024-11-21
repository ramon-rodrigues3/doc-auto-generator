from openai import OpenAI
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.utils.function_calling import convert_to_openai_function
from typing import Optional
from enum import Enum
from json import loads
from dotenv import load_dotenv, find_dotenv
import generator

load_dotenv(find_dotenv())

# ENUMS
class unidadeEnum(str, Enum):
    palavras = "palavras"
    paragrafos = "paragrafos"
    caracteres = "caracteres"

# TOLL CALLS
class buscar_informacao(BaseModel):
    """Retorna uma informação de uma base de dados"""
    info: str = Field(description="A informação que você está buscando", examples = ["Produtos", "Lista de defeitos"])
    fonte: Optional[str] = Field(description="Nome do arquivo que possui essa informação", examples = ["produtos.pdf"])

class gerar_pdf(BaseModel):
    """Use isso quando alguém pedir para você gerar um pdf. Retorna true ou false se o pdf foi gerado ou não"""
    tamanho: int = Field(description="Tamanho do pdf a ser gerado")
    unidade: unidadeEnum = Field(description="Unidade a que tamanho se refere")
    instrucao: str = Field(description="Que pdf deve ser criado")

class buscar_teperatura(BaseModel):
    """Retorna a temperatura em graus celcius"""
    local: str = Field(description="Nome da cidade que você quer saber a temperatura. Ex: São Paulo, Rio de Janeiro, Nova York")

def fn_buscar_informacao(info, fonte = "") -> str:
    return """
    * Salários baixos,
    * Vendas estagnadas
    * Infraestrutura precária
    * Escassez de estoque
    """

def fn_gerar_texto(tamanho, unidade, instrucao) -> str:
    return '{"result": true}'

def fn_buscar_temperatura(local):
    return len(local) * 3

funcs = {"buscar_informacao": fn_buscar_informacao, "gerar_pdf": fn_gerar_texto, "buscar_temperatura": fn_buscar_temperatura}
funcs = generator.funcoes

# RODAR TOOL CALL
def rodar_tool_call(tool):
    argumentos = loads(tool.function.arguments)
    print(f"\nRodando {tool.function.name}({argumentos})...")
    try:
        resultado = funcs[tool.function.name](**argumentos)
    except Exception as e:
        resultado = f"Error: {e}"
    print(f'resultado encontrado: {resultado}')
    

    return {
    'tool_call_id': tool.id,
    'role': 'tool',
    'name': tool.function.name,
    'content': str(resultado)
    }
    

# RESPOSTA TEXTUAL
def exibir_resposta(resposta):
    #resposta = response.choices[0].message.content
    print(f"IA: {resposta}")

def main():
    client = OpenAI()
    tools = [
        {
            "type": "function", 
            "function": convert_to_openai_function(gerar_pdf)
        },
        {
            "type": "function", 
            "function": convert_to_openai_function(buscar_informacao)
        },
        {
            "type": "function", 
            "function": convert_to_openai_function(buscar_teperatura)
        }
    ]
    tools = generator.tools

    mensagens = [
        {"role": "system", "content": "Use as calls functions para atender aos pedidos dos usuários. Primeiro pense em uma sequência de ações de call functions que resolve a demanda do usuário e em seguida chame-as functions passo a passo."}
    ]

    while True:
        pergunta = input("user: ")

        if pergunta == "q": break

        mensagens.append({
            "role": "user",
            "content": pergunta
        })

        while True:
            response = client.chat.completions.create(
                            model="gpt-4o",
                            messages=mensagens,
                            tools=tools,
                            tool_choice="auto",
                            stream=True
                        )#.choices[0].message
            for token in response:
                print(token)
                print()

            return
            mensagens.append(response)
            #print(response.to_dict())

            if response.content:
                exibir_resposta(response.content)
                
            if response.tool_calls:
                tools_p = response.tool_calls
                for tool in tools_p:
                    mensagens.append(rodar_tool_call(tool))
            else: break

if __name__ == "__main__":
    main()
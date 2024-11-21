from langchain.pydantic_v1 import BaseModel, Field
from typing import Optional, List
from enum import Enum
from assistant import Assistant
from langchain_core.utils.function_calling import convert_to_openai_function
from io import BytesIO

chat = Assistant("asst_WolVDtnyp76KF2BPpz8TFqnP") # passar o id do assistant
texto_gerado = []

# ENUMS
class unidadeEnum(str, Enum):
    pagina = "pagina"
    paragrafo = "paragrafo"
    palavra = "palavra"

class parteEnum(str, Enum):
    capitulo = "capitulo"
    pagina = "pagina"
    paragrafo = "paragrafo"

# TOOLS
class buscar_informacao(BaseModel):
    """Retorna uma informação de uma base de dados"""
    info: str = Field(description="A informação que você está buscando", examples = ["Produtos", "Lista de defeitos"])
    fontes: Optional[list[str]] = Field(description="Lista de arquivos que possuem essa informação", examples = ["produtos.pdf"])

class gerar_topico(BaseModel):
    """Gera um novo tópico para o usuário em segundo plano. Retorna apenas true ou false se o pedido foi recebido ou não."""
    instrucoes: str = Field(description="Instruções sobre como deve ser feita a geração do texto. Dê preferência a intruções detalhadas e precisas. Pode falar sobre estilo, forma, conteudo etc.")
    tema: str = Field(description="Tema do tópico a ser gerado")
    sub_topicos: List[str] = Field(description="Lista de sub-tópicos a serem criados dentro do tópico")

class gerar_texto_curto(BaseModel):
   """Gera um novo texto curto e adiciona ao arquivo. Retorna True ou False, se o texto foi gerado.""" 
   instrucao: str = Field(description="prompt que será usado para gerar o texto")

class alterar_texto(BaseModel):
    """Altera uma parte específica do texto. Retorna true ou false se o pedido foi recebido ou não."""
    instrucao: str = Field(description="Instrução e detalhes sobre a alteração.", examples = ["detalhe mais", "mude o tom"])
    topico: int = Field(description="indice do tópico a ser alterado")
    sub_topico: Optional[int] = Field(description="indice do sub-tópico a ser alterado")
    paragrafo: Optional[int] = Field(description="indice do parágrafo a ser alterado")

class substituir_texto(BaseModel):
    """Refaz uma parte específica do texto totalmente do zero. Retorna true ou false se o pedido foi recebido ou não."""
    instrucao: str = Field(description="Instrução e detalhes sobre o novo texto.", examples = ["gere um texto sobre a vida de Platão", "Fale sobre os problemas da empresa neste parágrafo"])
    topico: int = Field(description="indice do tópico a ser substituido")
    sub_topico: Optional[int] = Field(description="indice do sub-tópico a ser substituido")
    paragrafo: Optional[int] = Field(description="indice do parágrafo a ser substituido")

class remover_texto(BaseModel):
    """Remove uma parte específica do texto. Retorna true ou false se o pedido foi recebido ou não."""
    topico: int = Field(description="indice do tópico a ser removido")
    sub_topico: Optional[int] = Field(description="indice do sub-tópico a ser removido")
    paragrafo: Optional[int] = Field(description="indice do parágrafo a ser removido")

class arquivo_size(BaseModel):
    """Retorna um texto com o tamanho do arquivo gerado contendo número de tópicos, sub-tópicos e parágrafos"""

class arquivo_busca(BaseModel):
    """Retorna uma parte específica do texto."""
    topico: int = Field(description="indice do tópico a ser retornado")
    sub_topico: Optional[int] = Field(description="indice do sub-tópico a ser retornado")
    paragrafo: Optional[int] = Field(description="indice do parágrafo a ser retornado")

class gerar_arquivo(BaseModel):
    """Transforma o texto em um arquivo txt. Returna True ou False se teve exito"""
    nome: str = Field(description="Nome que será dado ao arquivo, dê preferência a nomes significativos escritos kebab-case")

# FUNCTIONS
def fn_buscar_informacao(info, fontes="") -> str:
    prompt = f"""
    Busque essa informação na sua base de conhecimento:
    {info}
    """
    if fontes:
        prompt += f"""Mais especificamente nos arquivos: 
        {fontes}"""

    # Apenas durante o teste

    prompt += "Invente informações se necessário"

    return chat.ask(prompt)

def fn_gerar_topico(instrucoes: str, tema: str, sub_topicos: list) -> bool:
    ultimo_paragrafo = ''

    if len(sub_topicos) == 0:
        prompt = f"faça um texto sobre o tópico {tema} seguindo as instrucoes: {instrucoes}\nTexto:"
        resposta = chat.ask(prompt)
        paragrafos = resposta.split("\n")
        paragrafos = [p for p in paragrafos if p not in ['', '\n']]         
        ultimo_paragrafo = paragrafos[-1]
        paragrafos.append("\n****\n")
        texto_gerado.append([paragrafos])
        
    for i, sub in enumerate(sub_topicos):
        if i == 0:
            prompt = f"Para o tópico {tema}, faça um sub-tópico sobre{sub}, seguindo as instruções: \n{instrucoes}\nTexto:"
            resposta = chat.ask(prompt)
            paragrafos = resposta.split("\n")
            paragrafos = [p for p in paragrafos if p not in ['', '\n']]         
            ultimo_paragrafo = paragrafos[-1]
            paragrafos.append("\n****\n")
            texto_gerado.append([paragrafos])
            continue
        
        prompt = f"Para o tópico {tema}, faça um sub-tópico sobre {sub}, seguindo as instruções: \n\"{instrucoes}\" \nContinuando o texto que terminou assim: {ultimo_paragrafo}  \nTexto:"
        resposta = chat.ask(prompt)
        paragrafos = resposta.split("\n")
        paragrafos.append("\n****\n")
        texto_gerado[-1].append(paragrafos)
        ultimo_paragrafo = paragrafos[-1]

    return True

def fn_gerar_texto_curto(instrucao: str) -> bool:
    resposta = chat.ask(instrucao)
    paragrafos = resposta.split("\n")
    paragrafos = [p for p in paragrafos if p not in ['', '\n']]         

    texto_gerado.append([paragrafos])
    return True

def fn_alterar_texto(instrucao: str, topico: int, sub_topico: int = None, paragrafo: int = None) -> bool:
    texto_alvo = ''
    print(paragrafo)
    if paragrafo != None:
        print("Alterando paragrafo")
        texto_alvo = texto_gerado[topico][sub_topico][paragrafo]
        print(texto_alvo)
    elif sub_topico != None:
        print("Alterando sub_topico")
        texto_alvo = "\n".join(texto_gerado[topico][sub_topico])
    else:
        print("Alterando topico")
        novo_topico = []
        ultimo_paragrafo = ''
        for i, sub in enumerate(texto_gerado[topico]):
            texto_alvo = "\n".join(sub)
            prompt = (f"Texto original: {texto_alvo} \n instrução: {instrucao} \nNovo texto:" if i == 0 
                      else f"Texto original: {texto_alvo} \n Paragrafo anterior: {ultimo_paragrafo}\n instrução: {instrucao} \nNovo texto:")
            resposta = chat.ask(prompt).split('\n')
            novo_topico.append(resposta)
            ultimo_paragrafo = resposta[-1]
        inserir_texto(novo_topico, topico)
        return True

    prompt = f'texto original: {texto_alvo} \n instrução: {instrucao} \nNovo texto:'
    resposta = chat.ask(prompt)
    inserir_texto(resposta, topico, sub_topico, paragrafo)

    return True

def fn_substituir_texto(instrucao, topico, sub_topico, paragrafo = None) -> bool:
    prompt = f'instrução: {instrucao} \nTexto:'
    resposta = chat.ask(prompt)
    inserir_texto(resposta, topico, sub_topico, paragrafo)

    return True

def fn_remover_texto(topico, sub_topico = None, paragrafo = None) -> bool:
    global texto_gerado
    if paragrafo != None:
        texto_gerado[topico][sub_topico] = [par for i, par in enumerate(texto_gerado[topico][sub_topico]) if i != paragrafo]
    elif sub_topico != None:
        texto_gerado[topico] = [sub for i, sub in enumerate(texto_gerado[topico]) if i != sub_topico]
    else:
        texto_gerado = [top for i, top in enumerate(texto_gerado) if i != topico]
    return True

def fn_arquivo_size() -> str:
    texto = f"arquivo: {len(texto_gerado)} topicos \n" + "-" * 20
    for i, topico in enumerate(texto_gerado):
        texto += f"topico {i}: {len(topico)} sub-topicos \n" 
        for i, sub in enumerate(topico):
            texto += f"sub-topico {i}: {len(sub)} paragrafos \n"
        texto += "\n\n"

    return texto

def fn_arquivo_busca(topico, sub_topico = None, paragrafo = None) -> str:
    if paragrafo != None:
        return texto_gerado[topico][sub_topico][paragrafo]
    elif sub_topico != None:
        return "\n".join(texto_gerado[topico][sub_topico])
    else:
        return "\n".join(["\n".join(sub) for sub in texto_gerado[topico]])

def fn_gerar_arquivo(nome: str) -> bool:
    caminho = f'docs/{nome}.txt'
    open(caminho, 'w', encoding='utf-8').write("\n".join([paragrafo for topico in texto_gerado for sub in topico for paragrafo in sub]))
    return True

def inserir_texto(texto, topico, sub_topico = None, paragrafo = None):
    print(texto_gerado)
    if paragrafo != None:
        texto_gerado[topico][sub_topico][paragrafo] = texto
    elif sub_topico != None:
        texto_gerado[topico][sub_topico] = texto.split("\n")
    else:
        print()
        texto_gerado[topico] = texto          

def set_arquivo(arquivo):
    global texto_gerado
    texto_gerado = arquivo

def arquivo_gerado():
    texto = "\n".join([paragrafo for topico in texto_gerado for sub in topico for paragrafo in sub])
    arquivo = BytesIO(bytes(texto, 'utf-8'))
    arquivo.name = 'arquivo'
    return arquivo
# Tolls 
tools = [
    {
        "type": "function", 
        "function": convert_to_openai_function(buscar_informacao)
    },
    {
        "type": "function", 
        "function": convert_to_openai_function(gerar_topico)
    },
    {
        "type": "function", 
        "function": convert_to_openai_function(gerar_texto_curto)
    },
    {
        "type": "function", 
        "function": convert_to_openai_function(alterar_texto)
    },
    {
        "type": "function", 
        "function": convert_to_openai_function(substituir_texto)
    },
    {
        "type": "function", 
        "function": convert_to_openai_function(remover_texto)
    },
    {
        "type": "function", 
        "function": convert_to_openai_function(arquivo_size)
    },    
    {
        "type": "function", 
        "function": convert_to_openai_function(arquivo_busca)
    },
    {
        "type": "function", 
        "function": convert_to_openai_function(gerar_arquivo)
    }

]

funcoes = {
    "buscar_informacao": fn_buscar_informacao,
    "gerar_topico": fn_gerar_topico,
    "gerar_texto_curto": fn_gerar_texto_curto,
    "alterar_texto": fn_alterar_texto,
    "substituir_texto": fn_substituir_texto,
    "remover_texto": fn_remover_texto,
    "arquivo_size": fn_arquivo_size,
    "arquivo_busca": fn_arquivo_busca,
    "gerar_arquivo": fn_gerar_arquivo
}

# MAIN
def main():
    fn_gerar_topico(tema='Mensagem de oi',
        sub_topicos=['Uma mensagem que diz "Oi"']
    )

    #fn_alterar_texto("Mude o tom para algo formal e seja muito prolixo", 0)
    #fn_substituir_texto('Diga para ele pagar o que deve de forma ameaçadora', 0, 1, 0)
    #fn_remover_texto(0,0)
    #fn_gerar_arquivo('teste')
    print(texto_gerado[0][0][-1])
if __name__ == "__main__": 
    main()
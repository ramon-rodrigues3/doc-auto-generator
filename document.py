from fpdf import FPDF
from io import BytesIO
import generator

def get_document(extensao: str) -> BytesIO:
    match extensao:
        case 'txt':
            return _gerar_txt()
        case 'pdf':
            return _gerar_pdf()

def _gerar_pdf() -> BytesIO:
    conteudo = generator.get_arquivo_str()

    pdf = FPDF()
    pdf.set_font('Helvetica', size=12)
    pdf.add_page()
    pdf.multi_cell(
        w=0,
        align='J',
        text=conteudo,
        markdown=True,
        wrapmode="WORD",
        padding=20.4
    )

    return BytesIO(pdf.output())

def _gerar_txt() -> BytesIO:
    conteudo = generator.get_arquivo_str()
    return BytesIO(bytes(conteudo, 'utf-8'))
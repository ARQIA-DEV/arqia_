import os
import logging
import pdfplumber
import pandas as pd
from docx import Document
import unicodedata
import ezdxf
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
import io
import base64

from pdf2image import convert_from_path

try:
    import ifcopenshell
except ImportError:
    ifcopenshell = None

load_dotenv()
logger = logging.getLogger(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def normalizar_texto(texto: str) -> str:
    texto = texto.lower()
    return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')

def analisar_com_gpt(texto: str, prompt: str = "") -> str:
    try:
        resposta = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": prompt or "Você é um especialista em análise de projetos."},
                {"role": "user", "content": texto}
            ],
            max_tokens=1000,
            temperature=0.3
        )
        return resposta.choices[0].message.content.strip()
    except Exception as e:
        logger.exception("Erro ao consultar o modelo GPT")
        raise RuntimeError("Erro ao processar com OpenAI") from e

def analisar_documento_por_imagem(file_path: str, prompt: str) -> str:
    try:
        imagens = convert_from_path(file_path)
        respostas = []

        for i, imagem in enumerate(imagens):
            img_byte_arr = io.BytesIO()
            imagem.save(img_byte_arr, format='PNG')
            img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")

            resposta = client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}},
                            {"type": "text", "text": f"Esta é a página {i+1} do projeto. Analise os principais elementos técnicos e estruturais."}
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.3
            )
            respostas.append(resposta.choices[0].message.content.strip())

        return "\n\n".join(respostas)
    except Exception as e:
        logger.exception("Erro ao analisar imagem com GPT-5")
        return f"Erro ao processar imagem: {e}"
    
def analisar_dwg(file_path: str) -> str:
    try:
        doc = ezdxf.readfile(file_path)
        tipos = {ent.dxftype() for ent in doc.modelspace()}
        return f"Entidades detectadas no DWG: {', '.join(tipos)}"
    except Exception as e:
        logger.exception("Erro ao analisar DWG")
        return f"Erro ao analisar DWG: {e}"

def analisar_bim(file_path: str) -> str:
    if not ifcopenshell:
        return "Biblioteca ifcopenshell não instalada."
    try:
        model = ifcopenshell.open(file_path)
        tipos = ["IfcWall", "IfcDoor", "IfcWindow", "IfcSpace"]
        resumo = {t: len(model.by_type(t)) for t in tipos}
        return "Elementos BIM: " + ", ".join(f"{k}: {v}" for k, v in resumo.items())
    except Exception as e:
        logger.exception("Erro ao analisar BIM")
        return f"Erro ao analisar BIM: {e}"

def analisar_documento_por_tipo(file_path: str, file_type: str, prompt: str = "") -> str:
    try:
        file_type = file_type.lower()
        if file_type == 'pdf':
            return analisar_documento_por_imagem(file_path, prompt)
        elif file_type == 'docx':
            doc = Document(file_path)
            texto = "\n".join(p.text for p in doc.paragraphs)
            return analisar_com_gpt(texto, prompt)
        elif file_type == 'xlsx':
            df = pd.read_excel(file_path)
            return df.to_string(index=False)
        elif file_type == 'dwg':
            return analisar_dwg(file_path)
        elif file_type in ['bim', 'ifc']:
            return analisar_bim(file_path)
        return "Tipo de arquivo não suportado."
    except Exception as e:
        logger.exception("Erro ao processar documento")
        return f"Erro ao processar o documento: {e}"

import os
import logging
import pandas as pd
from docx import Document
import unicodedata
import ezdxf
from dotenv import load_dotenv
import openai as openai_sdk
from openai import OpenAI
import base64

try:
    import ifcopenshell
except ImportError:
    ifcopenshell = None

load_dotenv()
logger = logging.getLogger(__name__)
OPENAI_SDK_VERSION = getattr(openai_sdk, "__version__", "desconhecida")


def get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY não configurada.")
    return OpenAI(api_key=api_key)


def _assert_responses_api_available(client: OpenAI) -> None:
    if not hasattr(client, "responses"):
        raise RuntimeError(
            "SDK openai sem suporte a client.responses "
            f"(versao instalada: {OPENAI_SDK_VERSION}). "
            "Atualize para openai>=1.40.0 e faça redeploy do web e worker."
        )

def normalizar_texto(texto: str) -> str:
    texto = texto.lower()
    return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')

def analisar_com_gpt(texto: str, prompt: str = "") -> str:
    try:
        client = get_openai_client()
        resposta = client.chat.completions.create(
            model="gpt-5-mini",
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

def analisar_pdf_com_gpt5mini_base64(pdf_base64: str, filename: str, prompt: str) -> str:
    try:
        client = get_openai_client()
        _assert_responses_api_available(client)

        file_data = f"data:application/pdf;base64,{pdf_base64}"
        resposta = client.responses.create(
            model="gpt-5-mini",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": prompt or "Você é um especialista em análise de projetos.",
                        },
                        {
                            "type": "input_file",
                            "filename": filename,
                            "file_data": file_data,
                        },
                    ],
                }
            ],
            store=False,
            reasoning={"effort": "minimal"},
        )
        return (resposta.output_text or "").strip()
    except Exception as e:
        logger.exception("Erro ao analisar PDF com GPT-5-mini")
        if "OPENAI_API_KEY não configurada." in str(e):
            raise RuntimeError("OPENAI_API_KEY não configurada.") from e
        raise RuntimeError("Erro ao processar PDF com OpenAI") from e


def analisar_pdf_com_gpt5mini(pdf_base64: str, filename: str, prompt: str) -> str:
    return analisar_pdf_com_gpt5mini_base64(
        pdf_base64=pdf_base64,
        filename=filename,
        prompt=prompt,
    )

def analisar_pdf_por_input_file(file_path: str, prompt: str = "") -> str:
    try:
        with open(file_path, "rb") as arquivo_pdf:
            arquivo_base64 = base64.b64encode(arquivo_pdf.read()).decode("utf-8")

        return analisar_pdf_com_gpt5mini_base64(
            pdf_base64=arquivo_base64,
            filename=os.path.basename(file_path),
            prompt=prompt,
        )
    except Exception as e:
        logger.exception("Erro ao analisar PDF por arquivo")
        return f"Erro ao processar PDF: {e}"
    
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
            return analisar_pdf_por_input_file(file_path, prompt)
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

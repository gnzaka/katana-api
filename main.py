from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = FastAPI()

DOCUMENT_ID = '1pAoGDhoae6Ma-c-PP9LG_ijqu5IZBu3IgkZWMoZnnWs'
SERVICE_ACCOUNT_FILE = 'katana-assistan.json'
SCOPES = ['https://www.googleapis.com/auth/documents']

class TextoEntrada(BaseModel):
    texto: str

def autenticar():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('docs', 'v1', credentials=creds)
    return service

@app.get("/documento")
def ler_documento():
    try:
        service = autenticar()
        doc = service.documents().get(documentId=DOCUMENT_ID).execute()
        conteudo = doc.get('body').get('content')
        texto = ''
        for elem in conteudo:
            if 'paragraph' in elem:
                for p in elem['paragraph'].get('elements', []):
                    texto += p.get('textRun', {}).get('content', '')
        return {"conteudo": texto.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/documento")
def adicionar_texto(dados: TextoEntrada):
    try:
        service = autenticar()
        requests = [
            {
                'insertText': {
                    'location': {
                        'index': 1,
                    },
                    'text': dados.texto + '\n'
                }
            }
        ]
        service.documents().batchUpdate(
            documentId=DOCUMENT_ID, body={'requests': requests}).execute()
        return {"mensagem": "Texto adicionado com sucesso."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

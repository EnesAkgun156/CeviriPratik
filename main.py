import os
import json
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

app = FastAPI(title="Pratik Çeviri API", version="2.0.0")

# Gemini anahtarı ve izin verilen site adresi ortam değişkenlerinden okunur.
# ALLOWED_ORIGINS örn: https://kullaniciadi.github.io  (birden fazlaysa virgülle ayır)
API_KEY = os.environ.get("GEMINI_API_KEY", "")
ORIGINS = [o.strip() for o in os.environ.get("ALLOWED_ORIGINS", "*").split(",") if o.strip()]
MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")

client = genai.Client(api_key=API_KEY) if API_KEY else None

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


_think_ok = True


def run_model(prompt, **cfg):
    """Düşünme (thinking) süresini kapatarak hızlı cevap ister.
    Model bu ayarı desteklemiyorsa otomatik olarak ayarsız tekrar dener."""
    global _think_ok

    def call(think):
        c = dict(cfg)
        if think:
            c["thinking_config"] = types.ThinkingConfig(thinking_budget=0)
        return client.models.generate_content(
            model=MODEL, contents=prompt, config=types.GenerateContentConfig(**c)
        )

    if _think_ok:
        try:
            return call(True)
        except Exception as e:
            if "thinking" not in str(e).lower():
                raise
            _think_ok = False
    return call(False)


@app.get("/")
def health():
    return {"status": "ok"}


# --- Siteyi çalıştıran ana uç: değerlendirme, paragraf üretme ve çeviri ---
class AskBody(BaseModel):
    prompt: str = Field(min_length=1, max_length=20000)


@app.post("/ask")
def ask(body: AskBody):
    if client is None:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY ayarlanmamış.")
    try:
        r = run_model(body.prompt, temperature=0.2, response_mime_type="application/json")
        return {"text": r.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API hatası: {str(e)}")


# --- İsteğe bağlı: senin yazdığın paragraf üretme ucu (site kullanmıyor) ---
class ParagraphResponse(BaseModel):
    level: str
    topic: str
    sentence_count: int
    english_paragraph: str
    turkish_paragraph: str


@app.get("/generate-paragraph", response_model=ParagraphResponse)
def generate_paragraph(
    topic: str = Query(...),
    level: str = Query(...),
    sentences: int = Query(..., ge=1, le=30),
):
    if level.upper() not in ["A1", "A2", "B1", "B2", "C1", "C2"]:
        raise HTTPException(status_code=400, detail="Geçersiz seviye.")
    if client is None:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY ayarlanmamış.")
    try:
        response = run_model(
            f"Write a paragraph about '{topic}', CEFR level {level.upper()}, exactly {sentences} short sentences.",
            system_instruction="Return the English paragraph and its exact Turkish translation with the same number of sentences.",
            response_mime_type="application/json",
            response_schema=ParagraphResponse,
            temperature=0.6,
        )
        return json.loads(response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API hatası: {str(e)}")

import json
import os
import re

CATEGORIES = [
    ("Museo", ["arte", "historia", "exhibición", "cultura", "educación"], ["museo", "arte", "exhibición", "galería"]),
    ("Parque", ["naturaleza", "aire libre", "familia", "jardín", "recreación"], ["parque", "jardín", "verde", "naturaleza"]),
    ("Restaurante", ["comida", "gastronomía", "servicio", "cocina", "chef"], ["restaurante", "comida", "gastronomía", "cocina"]),
    ("Monumento", ["histórico", "arquitectura", "cultural", "patrimonio"], ["monumento", "histórico", "patrimonio", "escultura"]),
    ("Teatro", ["espectáculo", "cultura", "entretenimiento", "danza", "ópera"], ["teatro", "espectáculo", "danza", "ópera"]),
    ("Iglesia", ["religión", "historia", "arquitectura", "fe"], ["iglesia", "templo", "catedral", "basílica"]),
    ("Mercado", ["comercio", "tradición", "local", "artesanía"], ["mercado", "plaza", "artesanía", "comercio"]),
    ("Lugar Cultural", ["cultura", "evento", "comunidad", "arte"], ["cultural", "evento", "comunidad", "arte"]),
]


def _rule_based_enrich(name: str, description: str):
    text = f"{name} {description}".lower()
    best = None
    max_hits = 0

    for cat, tags, keywords in CATEGORIES:
        hits = sum(1 for kw in keywords if kw in text)
        if hits > max_hits:
            best = (cat, tags, hits)
            max_hits = hits

    if not best:
        best = ("Lugar Cultural", ["cultura", "evento", "comunidad", "arte"], 0)

    category, tags, hits = best
    confidence = round(min(0.6 + min(hits, 3) * 0.13, 1.0), 2)
    return category, tags, confidence


def enrich_logic(name: str, description: str):
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=groq_key, base_url="https://api.groq.com/openai/v1")
            model = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
            response = client.chat.completions.create(
                model=model,
                messages=[{
                    "role": "user",
                    "content": (
                        f"Clasifica este sitio cultural en Colombia: '{name}'. Descripcion: {description}. "
                        'Responde solo JSON valido: {"category":"...","tags":["tag1","tag2"],"confidence":0.85}'
                    ),
                }],
                temperature=0.2,
            )
            raw = response.choices[0].message.content or ""
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                data = json.loads(match.group())
                category = str(data.get("category") or "Lugar Cultural")
                tags = data.get("tags") or ["cultura"]
                if not isinstance(tags, list):
                    tags = [str(tags)]
                confidence = round(min(float(data.get("confidence", 0.85)), 1.0), 2)
                return category, tags, confidence
        except Exception:
            pass

    return _rule_based_enrich(name, description)

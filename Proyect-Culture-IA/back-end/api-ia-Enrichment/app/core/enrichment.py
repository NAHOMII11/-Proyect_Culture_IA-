import random

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


def enrich_logic(name: str, description: str):
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
    confidence = round(0.6 + min(hits, 3) * 0.13 + random.uniform(0, 0.14), 2)
    confidence = min(confidence, 1.0)

    return category, tags, confidence
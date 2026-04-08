import random

CATEGORIES = ['Museo', 'Parque', 'Restaurante', 'Monumento', 'Teatro']
TAGS_BY_CATEGORY = {
    'Museo': ['arte', 'historia', 'exhibición'],
    'Parque': ['naturaleza', 'aire libre', 'familia'],
    'Restaurante': ['comida', 'gastronomía', 'servicio'],
    'Monumento': ['histórico', 'arquitectura', 'cultural'],
    'Teatro': ['espectáculo', 'cultura', 'entretenimiento'],
}

def simulate_enrichment(place):
    category = random.choice(CATEGORIES)
    tags = TAGS_BY_CATEGORY[category]
    confidence = round(random.uniform(0.6, 1.0), 2)
    return {
        "place_id": place.get("place_id"),
        "name": place.get("name"),
        "description": place.get("description"),
        "category": category,
        "tags": tags,
        "confidence": confidence
    }

def calculate_place_score(variables: dict):
    # Definimos pesos (estos podrían venir de un config service luego)
    weights = {
        "data_quality": 0.3,
        "cultural_relevance": 0.4,
        "accessibility": 0.3
    }
    
    explanation = []
    total_score = 0.0
    
    for var, weight in weights.items():
        val = variables.get(var, 0)
        contribution = round(val * weight, 2)
        total_score += contribution
        explanation.append({
            "variable": var,
            "weight": weight,
            "value": val,
            "contribution": contribution
        })
    
    # Determinar nivel
    level = "baja"
    if total_score >= 0.8: level = "alta"
    elif total_score >= 0.5: level = "media"
    
    return round(total_score, 2), level, explanation
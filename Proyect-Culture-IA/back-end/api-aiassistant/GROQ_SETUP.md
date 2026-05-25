# Groq.com Setup Guide - AI Assistant

## ¿Qué es Groq?

Groq.com es una plataforma de inferencia de IA ultra rápida. A diferencia de OpenRouter, Groq se especializa en **velocidad extrema** con modelos de código abierto como Mixtral, Llama 2 y Gemma.

### Ventajas de Groq

| Ventaja | Descripción |
|---------|-----------|
| **Súper Rápido** | Inferencia de 200+ tokens/segundo |
| **Gratis** | 14,000 tokens/día sin pagar |
| **Open Source** | Modelos Mixtral, Llama, Gemma |
| **Simple** | API compatible con OpenAI |
| **Libre de Límites** | Sin restricciones de modelo |

---

## API Key

Obtén la clave en https://console.groq.com/keys y configúrala en tu `.env` local (copia desde `.env.example`):

```
GROQ_API_KEY=your_groq_api_key_here
```

---

## Modelos Disponibles en Groq

| Modelo | Velocidad | Uso |
|--------|-----------|-----|
| **llama-3.1-70b-versatile** | ⚡⚡ Muy Rápido | Recomendado - Alta Calidad |
| **llama-3.1-8b-instant** | ⚡⚡⚡ Extremo | Ligero |
| ~~mixtral-8x7b-32768~~ | ❌ | Descontinuado

### Cambiar de Modelo

Solo edita `.env`:
```bash
# Recomendado - Alta Calidad
GROQ_MODEL=llama-3.1-70b-versatile

# Ligero - Ultra Rápido
GROQ_MODEL=llama-3.1-8b-instant

# ❌ NO USAR - Descontinuado
GROQ_MODEL=mixtral-8x7b-32768
```

Luego reinicia:
```bash
docker-compose restart api-aiassistant
```

---

## Configuración Actual

```bash
# En: back-end/api-aiassistant/.env
DATABASE_URL=postgresql+psycopg2://...
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-70b-versatile  ← ACTUALIZADO (reemplaza mixtral descontinuado)
PYTHONPATH=/app
```

```python
# En: back-end/api-aiassistant/app/config.py
class Settings(BaseSettings):
    database_url: str
    groq_api_key: str
    groq_model: str = "llama-3.1-70b-versatile"  ← ACTUALIZADO
```

```python
# En: back-end/api-aiassistant/app/application/services.py
self.client = OpenAI(
    api_key=self.settings.groq_api_key,
    base_url="https://api.groq.com/openai/v1"  # ← Endpoint de Groq
)
```

---

## Paso 1: Reinicia el Servicio

```bash
docker-compose restart api-aiassistant

# Espera 10 segundos a que reinicie
```

---

## Paso 2: Prueba

### Test Directo (Puerto 8009)
```bash
curl -X POST http://localhost:8009/aiassistant/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "query_text": "¿Cuál es la capital de Colombia?"
  }'
```

### Test vía Gateway (Puerto 8000)
```bash
curl -X POST http://localhost:8000/api/v1_aiassistant/aiassistant/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "query_text": "¿Cuál es la capital de Colombia?"
  }'
```

✅ Deberías ver una respuesta rápida con la respuesta de Groq.

---

## Monitorear Uso de Groq

1. Ve a https://console.groq.com
2. Haz login
3. Mira el dashboard de uso
4. Puedes ver:
   - Tokens usados
   - Costo
   - Requests por segundo

---

## Límites Gratis de Groq

- ✅ 14,000 tokens/día GRATIS
- ✅ Ilimitado después (con cuota)
- ✅ Velocidad prioritaria

---

## Solución de Problemas

### Error: "401 Unauthorized"
```
❌ Problema: API key incorrecta
✅ Solución:
   1. Verifica que copiaste toda la key en .env
   2. Reinicia: docker-compose restart api-aiassistant
```

### Error: "Model not found"
```
❌ Problema: Modelo especificado no existe
✅ Solución:
   1. Usa: mixtral-8x7b-32768 (recomendado)
   2. O: llama2-70b-4096
   3. O: gemma-7b-it
```

### Error: "Rate limit exceeded"
```
❌ Problema: Excediste el límite diario (14k tokens)
✅ Solución:
   1. Espera a mañana
   2. O actualiza tu plan de pago
```

### Respuesta Lenta
```
❌ Problema: Nunca ocurre con Groq (¡es super rápido!)
✅ Pero si: comprueba conexión a internet
```

---

## Cambios Realizados

✅ `.env` - Variables locales (ver `.env.example`)
✅ `config.py` - Cambiado a variables de Groq
✅ `services.py` - Cliente OpenAI apuntando a Groq
✅ `main.py` - Mensajes de error actualizados para Groq
✅ `README.md` - Documentación actualizada
✅ `API_AIASSISTANT_GATEWAY.md` - Integración actualizada

---

## Próximos Pasos

1. ✅ Reinicia el servicio: `docker-compose restart api-aiassistant`
2. ✅ Espera 10 segundos
3. ✅ Prueba con el curl anterior
4. ✅ ¡Disfruta de la velocidad de Groq! ⚡

---

## Referencias

- https://console.groq.com - Dashboard
- https://console.groq.com/docs/models - Modelos disponibles
- https://console.groq.com/docs/api-overview - Documentación API
- https://console.groq.com/keys - Gestión de API keys

---

**¿Listo?** El servicio ahora usa Groq. Pruébalo y cuéntame si tienes problemas. 🚀

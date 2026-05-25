# OpenRouter.ai Setup Guide

## ¿Qué es OpenRouter.ai?

OpenRouter.ai es una plataforma que proporciona acceso unificado a múltiples modelos de IA a través de una API compatible con OpenAI. Esto te permite:

- ✅ Acceder a ChatGPT, Claude, Llama y otros modelos
- ✅ Cambiar modelos fácilmente sin cambiar código
- ✅ Comparar precios y rendimiento
- ✅ Usar una sola API key para múltiples proveedores

## Paso 1: Crear Cuenta en OpenRouter

1. Abre https://openrouter.io en tu navegador
2. Haz clic en "Sign Up" en la esquina superior derecha
3. Completa el formulario con:
   - Email
   - Contraseña
   - Nombre completo
4. Verifica tu email
5. Inicia sesión

## Paso 2: Obtener la API Key

1. Una vez dentro de tu cuenta, ve a **Keys** en el menú izquierdo
2. Haz clic en **"Create New Key"**
3. Dale un nombre descriptivo, ej: "Proyecto Culture IA"
4. Selecciona el scope (permisos) - "All" es suficiente
5. Copia la API key que se genera

## Paso 3: Configurar en tu Proyecto

### Opción A: Variable de Entorno Local
```bash
# En el archivo .env del servicio api-aiassistant/
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxx
OPENROUTER_MODEL=openai/gpt-3.5-turbo
```

### Opción B: Docker Compose
```yaml
# En docker-compose.yml
services:
  api-aiassistant:
    environment:
      OPENROUTER_API_KEY: sk-or-v1-xxxxxxxxxxxxxxxxxxxx
      OPENROUTER_MODEL: openai/gpt-3.5-turbo
```

## Modelos Disponibles en OpenRouter

### Modelos Recomendados

| Modelo | Velocidad | Costo | Caso de Uso |
|--------|-----------|-------|-----------|
| `openai/gpt-3.5-turbo` | ⚡⚡⚡ Muy Rápido | $ | Consultas generales, producción |
| `openai/gpt-4` | ⚡ Moderado | $$$ | Análisis complejo, calidad máxima |
| `anthropic/claude-3-opus` | ⚡ Moderado | $$ | Texto largo, análisis detallado |
| `anthropic/claude-3-sonnet` | ⚡⚡ Rápido | $ | Balance velocidad/calidad |
| `meta-llama/llama-2-70b` | ⚡⚡ Rápido | $ | Open source, sin limitaciones |

### Cómo Cambiar de Modelo

Solo actualiza la variable `OPENROUTER_MODEL` en el `.env`:

```bash
# Cambiar a Claude
OPENROUTER_MODEL=anthropic/claude-3-opus

# Cambiar a Llama
OPENROUTER_MODEL=meta-llama/llama-2-70b

# Volver a GPT-3.5
OPENROUTER_MODEL=openai/gpt-3.5-turbo
```

Luego reinicia el servicio:
```bash
docker-compose restart api-aiassistant
```

## Paso 4: Verificar Configuración

### 1. Ver Balance de tu Cuenta
```bash
curl https://openrouter.io/api/v1/auth/key/info \
  -H "Authorization: Bearer sk-or-v1-xxxxxxxxxxxxxxxxxxxx"
```

### 2. Probar el Endpoint del Servicio
```bash
curl -X POST http://localhost:8009/aiassistant/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "query_text": "Hola, ¿cómo estás?"
  }'
```

### 3. Via Gateway
```bash
curl -X POST http://localhost:8000/api/v1_aiassistant/aiassistant/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "query_text": "Hola, ¿cómo estás?"
  }'
```

## Precios en OpenRouter

OpenRouter es competitivo en precios. Ejemplos aproximados:

| Modelo | Precio Entrada | Precio Salida |
|--------|-----------------|--------------|
| GPT-3.5-turbo | $0.0005/1K | $0.0015/1K |
| GPT-4 | $0.003/1K | $0.006/1K |
| Claude 3 Opus | $0.015/1K | $0.075/1K |
| Llama 2 70B | $0.00070/1K | $0.00090/1K |

*Verificar precios actuales en https://openrouter.io/docs/models*

## Solución de Problemas

### Error: "Unauthorized" o "Invalid API Key"
- Verifica que copié la API key correctamente (sin espacios)
- Asegúrate de que no expiró el tiempo de la key
- Ve a OpenRouter y regenera una nueva key si es necesario

### Error: "Model not available"
- Verifica el nombre del modelo: https://openrouter.io/docs/models
- El formato correcto es `proveedor/nombre-modelo`, ej: `openai/gpt-4`

### Error: "Rate limit exceeded"
- Espera unos minutos antes de hacer más consultas
- Considera un plan de pago en OpenRouter para aumentar límites

### Error: "Insufficient credits"
- Agrega fondos a tu cuenta en OpenRouter.io
- Ve a **Billing** → **Add Credits**

## Seguridad

⚠️ **IMPORTANTE:**
- ❌ Nunca commits tu API key en el repositorio
- ✅ Usa variables de entorno (`.env` que está en `.gitignore`)
- ✅ En producción, almacena la key en secrets seguros (AWS Secrets Manager, Azure Key Vault, etc.)
- ✅ Rotacea las keys periódicamente
- ✅ Monitorea el uso de tu key en OpenRouter dashboard

## Referencias

- https://openrouter.io/docs/intro
- https://openrouter.io/docs/models
- https://openrouter.io/docs/api/chat-complete
- https://openrouter.io/keys

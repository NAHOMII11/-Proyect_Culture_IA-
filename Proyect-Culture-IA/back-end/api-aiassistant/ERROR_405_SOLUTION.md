# 🔧 Solución de Error 405 - OpenRouter.ai

## Problema

Recibiste error **405 (Method Not Allowed)** al intentar hacer POST a tu API.

## Causas Posibles

### 1️⃣ **API Key No Configurada (PRINCIPAL)**
Si ves este error, probablemente es porque estás usando el placeholder:
```bash
OPENROUTER_API_KEY=your-openrouter-api-key-here  ❌ INCORRECTO
```

OpenRouter rechaza requests sin API key válida con error 405.

### 2️⃣ **Headers Faltantes (SECUNDARIO)**
OpenRouter requiere headers específicos. Hemos actualizado el código para incluirlos.

---

## ✅ Solución - Paso a Paso

### Paso 1: Obtén tu API Key en OpenRouter

1. Ve a https://openrouter.io
2. Inicia sesión (o crea cuenta)
3. Haz clic en **Keys** (en el menú)
4. Haz clic en **"Create new key"**
5. Dale un nombre, ej: "Proyecto Cultural"
6. **Copia la key completa** (empieza con `sk-or-v1-`)

### Paso 2: Actualiza tu .env

Abre `back-end/api-aiassistant/.env` y reemplaza:

```bash
# ANTES
OPENROUTER_API_KEY=your-openrouter-api-key-here

# DESPUÉS (pega tu key real)
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

⚠️ **IMPORTANTE:**
- No incluyas comillas
- La key debe tener al menos 50+ caracteres
- Verifica que no haya espacios antes/después

### Paso 3: Reinicia el Servicio

```bash
# Detén los contenedores
docker-compose down

# Inicia de nuevo
docker-compose up api-aiassistant
```

O si está corriendo:
```bash
docker-compose restart api-aiassistant
```

### Paso 4: Prueba de Nuevo

```bash
curl -X POST http://localhost:8000/api/v1_aiassistant/aiassistant/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "query_text": "¿Qué es el patrimonio cultural?"
  }'
```

---

## 📊 Checklist de Validación

- [ ] Abrí https://openrouter.io y creé cuenta
- [ ] Generé una API key en "Keys"
- [ ] Copié la key completa (sk-or-v1-...)
- [ ] Edité `back-end/api-aiassistant/.env`
- [ ] Reemplacé `OPENROUTER_API_KEY` con la key real
- [ ] Reinicié el contenedor (`docker-compose restart api-aiassistant`)
- [ ] Espéré 5-10 segundos a que se reinicie
- [ ] Volví a hacer POST al endpoint

---

## 🧪 Cómo Verificar que Funciona

### Opción A: Test Directo (Puerto 8009)
```bash
curl -X POST http://localhost:8009/aiassistant/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test",
    "query_text": "Hola"
  }'
```

✅ Deberías ver respuesta JSON con la consulta guardada

### Opción B: Test vía Gateway (Puerto 8000)
```bash
curl -X POST http://localhost:8000/api/v1_aiassistant/aiassistant/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test",
    "query_text": "Hola"
  }'
```

✅ Deberías ver la misma respuesta

### Opción C: Health Check
```bash
curl http://localhost:8000/api/v1_aiassistant/aiassistant/health
```

✅ Deberías ver: `{"status":"healthy","database":"connected"}`

---

## 🐛 Errores Comunes y Soluciones

### Error: "OpenAI error: 401 Unauthorized"
```
❌ Problema: API key incorrecta o expirada
✅ Solución: 
   1. Verifica que copiaste toda la key
   2. Regenera una nueva key en OpenRouter.io
   3. Reinicia el contenedor
```

### Error: "Connection refused"
```
❌ Problema: El contenedor no está corriendo
✅ Solución:
   1. docker-compose up api-aiassistant
   2. Espera 10 segundos
   3. Vuelve a intentar
```

### Error: "Model not found" 
```
❌ Problema: El modelo especificado no existe
✅ Solución:
   1. Verifica en https://openrouter.io/docs/models
   2. Usa un modelo válido: openai/gpt-3.5-turbo, etc.
   3. Actualiza OPENROUTER_MODEL en .env
   4. Reinicia
```

### Error: "No credits available"
```
❌ Problema: Tu cuenta no tiene fondos
✅ Solución:
   1. Ve a https://openrouter.io/account/billing
   2. Haz clic en "Add Credits"
   3. Completa el pago
```

---

## 📝 Lo que Hicimos Hoy

✅ Agregamos `extra_headers` requeridos por OpenRouter
✅ Configuramos `HTTP-Referer` y `X-OpenRouter-Title`
✅ El código ahora es compatible 100% con OpenRouter

---

## 🔗 Referencias

- https://openrouter.io/docs/intro
- https://openrouter.io/docs/api/chat-complete
- https://openrouter.io/keys (para obtener API keys)
- https://openrouter.io/docs/models (lista de modelos disponibles)

---

**¿Seguimos sin error?** Avísame qué error específico ves y te ayudo a resolverlo. 🚀

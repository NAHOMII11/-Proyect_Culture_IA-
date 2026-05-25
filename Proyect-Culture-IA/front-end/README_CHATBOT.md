# AI ChatBot Widget - Documentación

## 📌 Overview

Se ha creado un **widget de chatbot flotante** en el frontend que permite a los usuarios interactuar con la API de AI Assistant de Groq de manera intuitiva.

### Características

✅ **Círculo flotante** en la esquina inferior izquierda  
✅ **Chat interactivo** con el asistente de IA  
✅ **Respuestas en tiempo real** desde Groq  
✅ **Historial de mensajes** en la sesión  
✅ **Diseño responsive** para móviles  
✅ **Animaciones suaves** y profesionales  
✅ **Manejo de errores** elegante  

---

## 🎨 Componentes Creados

### 1. **AIChatBot.jsx** (`src/components/AIChatBot.jsx`)

Componente principal que gestiona:
- Estado del chat (abierto/cerrado)
- Mensajes de usuario y IA
- Envío de peticiones a la API
- Formateo de respuestas con markdown

**Props:** Ninguna (standalone)

**Estado:**
```javascript
- isOpen: bool         // ¿Está abierto el chat?
- messages: array      // Historial de mensajes
- inputValue: string   // Texto en el input
- isLoading: bool      // ¿Esperando respuesta?
```

### 2. **AIChatBot.css** (`src/styles/AIChatBot.css`)

Estilos del widget incluyendo:
- Botón flotante con gradiente
- Ventana de chat responsive
- Animaciones de entrada/salida
- Estilos de mensajes usuario/AI
- Indicador de escritura
- Compatibilidad móvil

---

## 🚀 Cómo Funciona

### Flujo de Mensajes

```
1. Usuario escribe un texto en el input
   ↓
2. Presiona el botón enviar (📤)
   ↓
3. El mensaje se muestra inmediatamente en el chat
   ↓
4. Se envía POST a:
   POST http://localhost:8000/api/v1_aiassistant/aiassistant/chat
   Body: {
     "user_id": "user-1",
     "query_text": "tu pregunta"
   }
   ↓
5. Se muestra indicador de carga (typing animation)
   ↓
6. Groq responde (típicamente en 1-3 segundos)
   ↓
7. La respuesta se formatea y muestra en el chat
   ↓
8. Usuario puede enviar más preguntas
```

### Formateo de Respuestas

La respuesta de Groq (markdown) se convierte a HTML:

```
**negrita** → <strong>negrita</strong>
*cursiva* → <em>cursiva</em>
\n → <br/>
* item → <li>item</li>
```

---

## 📱 Integración

El componente está integrado en `src/routes/AppRouter.jsx`:

```jsx
import AIChatBot from '../components/AIChatBot'

function AppRouter() {
  return (
    <>
      <Routes>
        {/* tus rutas */}
      </Routes>
      <AIChatBot />  ← ¡Disponible en todas las páginas!
    </>
  )
}
```

El chatbot ahora aparece en **todas las páginas** de tu aplicación.

---

## 🎯 Uso

### Para el Usuario (Frontend)

1. **Abrir chat**: Clickea el círculo morado en la esquina inferior izquierda
2. **Escribir pregunta**: "¿Qué es el patrimonio cultural?"
3. **Enviar**: Presiona enter o clickea el botón 📤
4. **Ver respuesta**: La IA responde en segundos
5. **Historial**: El chat guarda toda la conversación en la sesión
6. **Limpiar**: Clickea 🔄 en la esquina para borrar el historial

### Para el Desarrollador

Para obtener el user_id dinámico (desde contexto de autenticación):

```jsx
// En AIChatBot.jsx, importar contexto de auth:
import { useContext } from 'react'
import { AuthContext } from '../context/AuthContext'

// Usar el user_id del contexto:
const { user } = useContext(AuthContext)

// En la petición:
const response = await axios.post(
  'http://localhost:8000/api/v1_aiassistant/aiassistant/chat',
  {
    user_id: user?.id || 'user-1', // ← Dinámico
    query_text: inputValue,
  }
)
```

---

## 🎨 Personalización

### Cambiar posición del botón

En `AIChatBot.css`:
```css
.ai-chatbot-floating-btn {
  bottom: 20px;  /* ← Cambiar a 'top' para arriba */
  left: 20px;    /* ← Cambiar a 'right' para derecha */
}
```

### Cambiar colores

En `AIChatBot.css`:
```css
/* Cambiar el gradiente del botón */
.ai-chatbot-floating-btn {
  background: linear-gradient(135deg, #FF6B6B 0%, #FF4A6B 100%);
}

/* Cambiar color del mensaje del usuario */
.ai-chatbot-message.user .ai-chatbot-message-content {
  background: #FF6B6B;
}
```

### Cambiar dimensiones

En `AIChatBot.css`:
```css
.ai-chatbot-floating-btn {
  width: 70px;    /* Botón más grande */
  height: 70px;
}

.ai-chatbot-container {
  width: 420px;   /* Chat más ancho */
  height: 650px;  /* Chat más alto */
}
```

---

## 🔧 Variables de Entorno Necesarias

El chatbot necesita que la API de Groq esté corriendo:

```bash
# Backend debe estar en localhost:8000
# Y la API en puerto 8009
docker-compose up
```

---

## 📊 Estructura de Mensajes

**Mensaje de Usuario:**
```javascript
{
  id: 1234567890,
  text: "¿Qué es el patrimonio cultural?",
  sender: "user",
  timestamp: Date,
}
```

**Mensaje de IA:**
```javascript
{
  id: "uuid-de-groq",
  text: "**Introducción**\n\nEl patrimonio...",
  sender: "ai",
  timestamp: Date,
  metadata: {
    model: "llama-3.1-70b-versatile",
    tokens_total: 659,
    tokens_prompt: 44,
    tokens_completion: 615
  }
}
```

**Mensaje de Error:**
```javascript
{
  id: 1234567890,
  text: "Error al conectar con el asistente",
  sender: "ai",
  timestamp: Date,
  isError: true
}
```

---

## ⚠️ Manejo de Errores

El componente captura y muestra errores elegantemente:

```javascript
try {
  // Enviar petición
} catch (error) {
  // Muestra mensaje de error en el chat
  "Error al conectar con el asistente. Intenta de nuevo."
}
```

---

## 🎯 Próximas Mejoras Opcionales

- [ ] Guardar historial en localStorage
- [ ] Autenticación con user_id del contexto
- [ ] Typing indicators desde el servidor
- [ ] Soporte para imágenes en respuestas
- [ ] Modo oscuro/claro
- [ ] Compartir conversaciones
- [ ] Traducción de idiomas
- [ ] Analytics de preguntas

---

## 📦 Dependencias

- **React** (^19.2.4) - Ya instalado
- **axios** (^1.15.0) - Para peticiones HTTP (ya instalado)

No se agregaron dependencias nuevas.

---

## 🧪 Prueba Local

1. **Asegúrate que el backend está corriendo:**
   ```bash
   cd back-end
   docker-compose up
   ```

2. **Inicia el frontend:**
   ```bash
   cd front-end
   npm run dev
   ```

3. **Abre el navegador:**
   ```
   http://localhost:5173
   ```

4. **Haz click en el círculo morado** en la esquina inferior izquierda

5. **Escribe una pregunta** y presiona enviar

✅ Deberías ver la respuesta de Groq en el chat.

---

## 📝 Resumen de Archivos

| Archivo | Descripción |
|---------|-----------|
| `src/components/AIChatBot.jsx` | Componente principal del chatbot |
| `src/styles/AIChatBot.css` | Estilos del widget |
| `src/routes/AppRouter.jsx` | Integración en el router |

---

**¡El chatbot está listo para usar!** 🎉

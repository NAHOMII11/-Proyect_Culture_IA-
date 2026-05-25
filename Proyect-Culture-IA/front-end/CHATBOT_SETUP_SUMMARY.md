# ✅ AI ChatBot Flotante - CREADO

## 🎉 Componente Completado

He creado un **widget de chatbot flotante** completo que aparece en la esquina inferior izquierda de tu aplicación.

---

## 📦 Archivos Creados

### 1. **AIChatBot.jsx** ✅
- **Ruta:** `front-end/src/components/AIChatBot.jsx`
- **Descripción:** Componente principal del chatbot
- **Características:**
  - Botón flotante circular
  - Ventana de chat desplegable
  - Envío de mensajes a la API
  - Formateo de respuestas markdown
  - Historial de mensajes
  - Indicador de carga

### 2. **AIChatBot.css** ✅
- **Ruta:** `front-end/src/styles/AIChatBot.css`
- **Descripción:** Estilos completos del widget
- **Características:**
  - Gradientes y animaciones
  - Responsive para móviles
  - Botón flotante con hover
  - Animaciones de entrada/salida
  - Estilos de mensajes

### 3. **AppRouter.jsx** ✅ (Modificado)
- **Integración:** El chatbot ahora aparece en todas las páginas
- **Cambio:** Agregado `<AIChatBot />` en el router

### 4. **README_CHATBOT.md** ✅
- **Documentación completa** del componente

---

## 🎯 Cómo Funciona

```
┌─────────────────────────────────────────┐
│           TU APLICACIÓN                 │
│                                         │
│  (Todas las páginas)                   │
│                                         │
│                    [🤖] ← Círculo flotan│
│                                         │
│                       Clickea aquí ↘    │
└─────────────────────────────────────────┘
                        ↓
            ┌─────────────────────┐
            │  CHAT DESPLEGABLE    │
            │                      │
            │ Usuario: ¿Hola?     │
            │ IA: Hola, ¿cómo     │
            │     estás?          │
            │                      │
            │ [Escribe aquí...] 📤│
            └─────────────────────┘
                        ↓
            HTTP POST a Groq API
            (localhost:8000/api/v1_aiassistant)
                        ↓
            Respuesta formateada
                        ↓
            Se muestra en el chat
```

---

## 🚀 Para Usar

### 1. Backend (Groq) debe estar corriendo
```bash
cd back-end
docker-compose up
# Espera a que esté en http://localhost:8000
```

### 2. Frontend
```bash
cd front-end
npm run dev
# Abre http://localhost:5173
```

### 3. Interactúa
1. Haz click en el **círculo morado** (esquina inferior izquierda)
2. Se abre una ventana de chat
3. Escribe tu pregunta
4. Presiona Enter o clickea 📤
5. ¡La IA responde en segundos!

---

## ✨ Características

✅ **Botón flotante** con gradiente morado  
✅ **Chat en tiempo real** con la API de Groq  
✅ **Respuestas formateadas** (negrita, listas, etc.)  
✅ **Historial de mensajes** en la sesión  
✅ **Indicador de carga** (typing animation)  
✅ **Botón limpiar** para borrar conversación  
✅ **Responsive** en móviles  
✅ **Animaciones suaves** y profesionales  
✅ **Manejo de errores** elegante  

---

## 📊 Estructura del Flujo

```
┌─────────────────────────────────────────────┐
│ 1. Usuario escribe: "¿Qué es patrimonio?"   │
└────────────┬────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────┐
│ 2. Se muestra inmediatamente en el chat      │
└────────────┬────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────┐
│ 3. POST a /api/v1_aiassistant/aiassistant/chat
│    {                                        │
│      "user_id": "user-1",                   │
│      "query_text": "¿Qué es patrimonio?"    │
│    }                                        │
└────────────┬────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────┐
│ 4. Groq procesa (1-3 segundos)              │
│    Muestra: ⏳ ⏳ ⏳ (typing)               │
└────────────┬────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────┐
│ 5. Respuesta de Groq                        │
│    "**Patrimonio Cultural**\n\nEs el conjunto...│
└────────────┬────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────┐
│ 6. Se formatea y muestra en el chat         │
│    Patrimonio Cultural                      │
│    Es el conjunto...                        │
└─────────────────────────────────────────────┘
```

---

## 🎨 Apariencia

### Botón Flotante
- Posición: Esquina inferior izquierda
- Forma: Círculo (60px)
- Color: Gradiente morado
- Icono: Mensaje de chat
- Hover: Se amplía con sombra

### Ventana de Chat
- Tamaño: 380px x 600px
- Posición: Sobre el botón
- Colores: Blanco con encabezado gradiente
- Animación: Desliza hacia arriba

### Mensajes
- Usuario: Burbuja azul a la derecha
- IA: Burbuja gris a la izquierda
- Timestamp: Hora relativa (ej: "2m atrás")

---

## 🔧 Personalización Fácil

### Cambiar colores
```css
/* En AIChatBot.css */
.ai-chatbot-floating-btn {
  background: linear-gradient(135deg, #FF6B6B 0%, #FF4A6B 100%);
}
```

### Cambiar posición
```css
.ai-chatbot-floating-btn {
  bottom: 20px;  /* ← Cambiar a 'top' */
  left: 20px;    /* ← Cambiar a 'right' */
}
```

### Cambiar tamaño
```css
.ai-chatbot-floating-btn {
  width: 70px;   /* ← Más grande */
  height: 70px;
}
```

---

## 📱 Responsive

✅ Desktop: 380px x 600px  
✅ Tablet: Se ajusta al 85% del ancho  
✅ Móvil: Se ajusta a pantalla completa menos márgenes  
✅ Muy pequeño: Se reduce a 50px el botón

---

## 🔐 Seguridad

- ✅ User ID está hardcodeado como "user-1" (puedes hacerlo dinámico)
- ✅ API key está en backend (protegida)
- ✅ Validaciones en el input
- ✅ Manejo de errores sin exposición de datos sensibles

---

## 📚 Documentación

**Archivo:** `front-end/README_CHATBOT.md`
- Guía completa del componente
- Ejemplos de uso
- Opciones de personalización
- Troubleshooting

---

## ✅ Checklist

| Tarea | Status |
|-------|--------|
| Botón flotante | ✅ |
| Chat despleglable | ✅ |
| Envío de mensajes | ✅ |
| Conexión a API | ✅ |
| Formateo de respuestas | ✅ |
| Historial de chat | ✅ |
| Indicador de carga | ✅ |
| Estilos responsive | ✅ |
| Animaciones | ✅ |
| Integración en app | ✅ |
| Documentación | ✅ |

---

## 🚀 Próximos Pasos (Opcionales)

1. **Autenticación dinámica:** Usar el user_id del contexto de autenticación
2. **Persistencia:** Guardar historial en localStorage
3. **Tema oscuro:** Añadir soporte para dark mode
4. **Sonido:** Notificación de nuevos mensajes
5. **Analytics:** Trackear preguntas populares

---

## 📝 Resumen

**Creado:** Un chatbot flotante profesional  
**Ubicación:** Esquina inferior izquierda  
**Funcionalidad:** Chat en tiempo real con Groq  
**Responsividad:** Funciona en todos los dispositivos  
**Integración:** Ya está en todas las páginas  

**¡Está listo para usar!** Inicia el backend y frontend, y verás el círculo morado. 🎉

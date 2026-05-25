import { useState, useRef, useEffect } from 'react';
import { API } from '../config/api';
import { httpClient } from '../utils/httpClient';
import { useNavigate, useLocation } from 'react-router-dom';
import { useMapPlaces } from '../context/MapPlacesContext';
import { filterPlacesInColombia } from '../utils/colombia';
import '../styles/AIChatBot.css';

export default function AIChatBot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const { showPlacesOnMap } = useMapPlaces();
  const navigate = useNavigate();
  const location = useLocation();

  const scrollToMap = () => {
    setTimeout(() => {
      document.getElementById('map-section')?.scrollIntoView({ behavior: 'smooth' });
    }, 350);
  };

  const pushPlacesToMap = (rawPlaces = []) => {
    const normalized = filterPlacesInColombia(
      rawPlaces.map((place) => ({
        id: place.place_id || place.id,
        place_id: place.place_id || place.id,
        name: place.name,
        category: place.category,
        latitude: place.latitude ?? place.lat,
        longitude: place.longitude ?? place.lng,
      }))
    );

    if (normalized.length === 0) return 0;

    showPlacesOnMap(normalized);

    if (location.pathname !== '/') {
      navigate('/');
    }

    scrollToMap();
    return normalized.length;
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    const queryText = inputValue.trim();
    if (!queryText) return;

    // Add user message to chat
    const userMessage = {
      id: Date.now(),
      text: queryText,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await httpClient.post(API.bff.assistantQuery, {
        question: queryText,
        user_context: { user_id: 'user-1' },
      });

      const mapCount = pushPlacesToMap(response.data.metadata?.places || []);

      // Add AI response to chat
      const aiMessage = {
        id: response.data.query_id,
        text: response.data.response_text,
        sender: 'ai',
        timestamp: new Date(response.data.created_at),
        metadata: response.data.metadata,
        mapCount,
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now(),
        text: error.response?.data?.detail || 'Error al conectar con el asistente. Intenta de nuevo.',
        sender: 'ai',
        timestamp: new Date(),
        isError: true,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([]);
  };

  return (
    <>
      {/* Floating Button */}
      <button
        className="ai-chatbot-floating-btn"
        onClick={() => setIsOpen(!isOpen)}
        title="Asistente de IA"
      >
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
        >
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        </svg>
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="ai-chatbot-container">
          <div className="ai-chatbot-header">
            <h3>Asistente de IA</h3>
            <div className="ai-chatbot-header-actions">
              <button
                className="ai-chatbot-clear-btn"
                onClick={handleClearChat}
                title="Limpiar chat"
              >
                🔄
              </button>
              <button
                className="ai-chatbot-close-btn"
                onClick={() => setIsOpen(false)}
                title="Cerrar"
              >
                ✕
              </button>
            </div>
          </div>

          <div className="ai-chatbot-messages">
            {messages.length === 0 ? (
              <div className="ai-chatbot-welcome">
                <p>👋 ¡Hola! Soy tu asistente de IA.</p>
                <p>¿Qué deseas saber sobre sitios culturales en Colombia?</p>
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={`ai-chatbot-message ${message.sender} ${
                    message.isError ? 'error' : ''
                  }`}
                >
                  <div className="ai-chatbot-message-content">
                    {message.sender === 'ai' ? (
                      <>
                        <div
                          className="ai-chatbot-ai-text"
                          dangerouslySetInnerHTML={{
                            __html: formatResponseText(message.text),
                          }}
                        />
                        {message.mapCount > 0 && (
                          <p className="ai-chatbot-map-hint">
                            📍 {message.mapCount} lugar(es) marcado(s) en el mapa
                          </p>
                        )}
                      </>
                    ) : (
                      <p>{message.text}</p>
                    )}
                  </div>
                  <span className="ai-chatbot-timestamp">
                    {formatTime(message.timestamp)}
                  </span>
                </div>
              ))
            )}
            {isLoading && (
              <div className="ai-chatbot-message ai loading">
                <div className="ai-chatbot-message-content">
                  <div className="ai-chatbot-typing">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form className="ai-chatbot-input-form" onSubmit={handleSendMessage}>
            <input
              type="text"
              className="ai-chatbot-input"
              placeholder="Escribe tu pregunta..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              disabled={isLoading}
            />
            <button
              type="submit"
              className="ai-chatbot-send-btn"
              disabled={isLoading || !inputValue.trim()}
            >
              📤
            </button>
          </form>
        </div>
      )}
    </>
  );
}

// Helper function to format markdown-like text
function formatResponseText(text) {
  if (!text) return '';

  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Bold
    .replace(/\*(.*?)\*/g, '<em>$1</em>') // Italic
    .replace(/\n/g, '<br/>') // Line breaks
    .replace(/^(\d+\.|[\*\-])\s/gm, '<li>') // List items
    .replace(/(<li>.*?<br\/>)/gs, '<ul>$1</ul>'); // Wrap in ul
}

// Helper function to format time
function formatTime(date) {
  const now = new Date();
  const diffMs = now - new Date(date);
  const diffMins = Math.floor(diffMs / 60000);

  if (diffMins === 0) return 'Ahora';
  if (diffMins < 60) return `${diffMins}m atrás`;
  
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h atrás`;

  return date.toLocaleTimeString('es-CO', {
    hour: '2-digit',
    minute: '2-digit',
  });
}

from openai import OpenAI, OpenAIError
import httpx
from app.config import get_settings
from app.core.audit_client import send_audit_event
from app.infrastructure.repository import ChatQueryRepository
from app.domain.models import ChatQuery
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, Dict, Any


class AIAssistantService:
    PLACES_API_URL = "http://api_place_container:8003/places/"
    COLOMBIA_LAT_MIN = -4.3
    COLOMBIA_LAT_MAX = 13.5
    COLOMBIA_LNG_MIN = -81.8
    COLOMBIA_LNG_MAX = -66.8

    def __init__(self, db: Session):
        self.db = db
        self.repository = ChatQueryRepository(db)
        self.settings = get_settings()
        # Groq uses OpenAI-compatible API
        self.client = OpenAI(
            api_key=self.settings.groq_api_key,
            base_url="https://api.groq.com/openai/v1"
        )

    def _serialize(self, db_query: ChatQuery) -> Dict[str, Any]:
        return {
            "query_id": db_query.id,
            "user_id": db_query.user_id,
            "query_text": db_query.query_text,
            "response_text": db_query.response_text,
            "ai_provider": db_query.ai_provider,
            "status": db_query.status,
            "metadata": db_query.metadata_json,
            "created_at": db_query.created_at,
            "updated_at": db_query.updated_at,
        }

    def _in_colombia(self, lat: float, lng: float) -> bool:
        return (
            self.COLOMBIA_LAT_MIN <= lat <= self.COLOMBIA_LAT_MAX
            and self.COLOMBIA_LNG_MIN <= lng <= self.COLOMBIA_LNG_MAX
        )

    def _fetch_colombia_places(self) -> list[dict[str, Any]]:
        try:
            response = httpx.get(f"{self.PLACES_API_URL}?limit=100", timeout=10.0)
            response.raise_for_status()
            places = response.json()
        except Exception:
            return []

        colombia_places = []
        for place in places:
            lat = place.get("latitude")
            lng = place.get("longitude")
            if lat is None or lng is None:
                continue
            try:
                lat_f = float(lat)
                lng_f = float(lng)
            except (TypeError, ValueError):
                continue
            if not self._in_colombia(lat_f, lng_f):
                continue
            colombia_places.append(
                {
                    "place_id": str(place.get("id")),
                    "name": place.get("name"),
                    "category": place.get("category"),
                    "latitude": lat_f,
                    "longitude": lng_f,
                    "importance_score": place.get("importance_score", 0),
                }
            )

        colombia_places.sort(
            key=lambda item: float(item.get("importance_score") or 0),
            reverse=True,
        )
        return colombia_places

    def _match_places_for_map(
        self, response_text: str, places: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        if not places:
            return []

        lower_response = (response_text or "").lower()
        matched = [
            place
            for place in places
            if place.get("name") and place["name"].lower() in lower_response
        ]
        return matched[:8] if matched else places[:5]

    def process_query(self, user_id: str, query_text: str) -> Dict[str, Any]:
        db_query = self.repository.create(
            user_id=user_id,
            query_text=query_text,
            status="pending",
        )

        colombia_places = self._fetch_colombia_places()
        places_context = "\n".join(
            [
                f"- {place['name']} | {place.get('category', 'Sin categoría')} | relevancia: {place.get('importance_score', 0)}"
                for place in colombia_places[:12]
            ]
        ) or "No hay lugares geolocalizados en Colombia."

        system_prompt = (
            "Eres un asistente de patrimonio cultural en Colombia. "
            "Responde en español usando UNICAMENTE los lugares de la lista proporcionada. "
            "Nunca menciones ciudades, monumentos o destinos fuera de Colombia. "
            "Si preguntan por los mas visitados o relevantes, usa el campo relevancia de la lista."
        )
        user_prompt = (
            f"Catalogo verificado en Colombia (ordenado por relevancia):\n{places_context}\n\n"
            f"Pregunta del usuario: {query_text}"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.settings.groq_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=2000,
            )
        except OpenAIError as exc:
            self.repository.update(
                query_id=db_query.id,
                status="error",
                metadata={"error": str(exc)},
            )
            raise

        response_text = response.choices[0].message.content or ""
        map_places = self._match_places_for_map(response_text, colombia_places)
        if not colombia_places:
            response_text = (
                "No encuentro sitios culturales georreferenciados en Colombia en el catalogo. "
                "Importa o geolocaliza lugares para poder recomendarlos."
            )
            map_places = []
        metadata: Dict[str, Any] = {
            "model": response.model,
            "places": map_places,
            "country_scope": "Colombia",
        }
        if response.usage:
            metadata.update(
                {
                    "tokens_prompt": response.usage.prompt_tokens,
                    "tokens_completion": response.usage.completion_tokens,
                    "tokens_total": response.usage.total_tokens,
                }
            )

        updated_query = self.repository.update(
            query_id=db_query.id,
            response_text=response_text,
            status="success",
            metadata=metadata,
        )

        send_audit_event(
            event_type="consulta_asistente",
            source_service="aiassistant-service",
            reference_id=str(updated_query.id),
            payload_summary={
                "user_id": user_id,
                "query_text": query_text[:200],
                "status": "success",
            },
        )

        return self._serialize(updated_query)

    def get_query(self, query_id: UUID) -> Optional[Dict[str, Any]]:
        db_query = self.repository.get_by_id(query_id)
        if not db_query:
            return None
        return self._serialize(db_query)

    def list_queries(self, user_id: Optional[str] = None, skip: int = 0, limit: int = 10) -> Dict[str, Any]:
        if user_id:
            total, items = self.repository.get_by_user_id(user_id, skip, limit)
        else:
            total, items = self.repository.list_all(skip, limit)

        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": [self._serialize(item) for item in items],
        }
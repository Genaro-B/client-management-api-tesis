"""Router del asistente administrativo (admin bot).

Expone POST /consult: recibe texto libre en español, detecta la intención
con el matcher determinístico (misma filosofía que el Bot Router de la
tesis) y responde con datos reales de la base de datos.

Cada consulta se registra como una interacción con source="admin-bot",
alimentando las métricas de intenciones del dashboard.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.services.admin_bot.admin_intent_router import AdminIntentRouter
from src.services.admin_bot.admin_bot_service import AdminBotService
from src.services.interaction_service import InteractionService

router = APIRouter()


class ConsultRequest(BaseModel):
    """Cuerpo de la consulta al asistente administrativo."""
    mensaje: str = Field(..., min_length=1, description="Texto libre en español")


@router.post("/consult")
def consult(payload: ConsultRequest, db: Session = Depends(get_db)):
    """Procesa una consulta en lenguaje natural y responde con datos reales.

    - Detecta la intención con AdminIntentRouter (pattern matching determinístico).
    - Compone la respuesta con AdminBotService (datos reales de repositories).
    - Registra la consulta como interacción con source="admin-bot" e intent.
    Devuelve {"intent": ..., "respuesta": ...} con status 200.
    """
    mensaje = payload.mensaje.strip()
    if not mensaje:
        raise HTTPException(status_code=422, detail="El mensaje no puede estar vacío")

    router = AdminIntentRouter()
    intent = router.match(mensaje)

    service = AdminBotService(db)
    respuesta = service.respond(intent)

    # Registrar la consulta como interacción (source admin-bot, intent detectado).
    # result se trunca a 200 chars: el campo es String(255) en el modelo.
    InteractionService(db).create(
        source="admin-bot",
        payload=mensaje,
        intent=intent,
        result=respuesta[:200],
    )

    return {"intent": intent, "respuesta": respuesta}
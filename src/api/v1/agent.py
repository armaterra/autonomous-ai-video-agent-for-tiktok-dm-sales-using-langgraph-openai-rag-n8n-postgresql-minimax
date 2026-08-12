from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from loguru import logger

from src.services.langgraph_agent import SalesAgent

router = APIRouter()
sales_agent = SalesAgent()

class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    user_id: str
    response: str
    payment_link: str | None = None

@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """Interactúa con el agente de ventas."""
    try:
        result = await sales_agent.invoke(
            user_id=request.user_id,
            message=request.message,
        )

        return ChatResponse(
            user_id=request.user_id,
            response=result.get("response", ""),
            payment_link=result.get("payment_link"),
        )

    except Exception as e:
        logger.error(f"Error en agente: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trace/{user_id}")
async def get_trace(user_id: str):
    """Obtiene la traza de Langfuse para un usuario."""
    # Integración con Langfuse para consultar trazas
    return {
        "user_id": user_id,
        "message": "Consulta la traza en Langfuse en http://localhost:3000",
    }

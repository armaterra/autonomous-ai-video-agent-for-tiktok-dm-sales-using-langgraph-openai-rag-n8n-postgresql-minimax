from fastapi import APIRouter, Request, HTTPException
from loguru import logger

router = APIRouter()

@router.post("/tiktok")
async def tiktok_webhook(request: Request):
    """Webhook para recibir eventos de TikTok (comentarios, DMs)."""
    try:
        payload = await request.json()
        logger.info(f"Webhook TikTok recibido: {payload}")

        # Procesar payload y enviar a LangGraph
        # ...

        return {"status": "ok", "message": "Webhook procesado"}
    except Exception as e:
        logger.error(f"Error en webhook TikTok: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/payment")
async def payment_webhook(request: Request):
    """Webhook para confirmación de pago desde Link Bi / Mall Bi."""
    try:
        payload = await request.json()
        logger.info(f"Webhook de pago recibido: {payload}")

        # Confirmar pago y actualizar estado del lead
        # ...

        return {"status": "ok", "message": "Pago confirmado"}
    except Exception as e:
        logger.error(f"Error en webhook de pago: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

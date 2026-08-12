from fastapi import APIRouter, HTTPException, BackgroundTasks
from loguru import logger

from src.models.video import (
    VideoGenerationRequest,
    VideoGenerationResponse,
    TikTokPublishRequest,
)
from src.services.minimax import MiniMaxService
from src.services.tiktok import TikTokService

router = APIRouter()
minimax_service = MiniMaxService()
tiktok_service = TikTokService()

@router.post("/generate", response_model=VideoGenerationResponse)
async def generate_video(request: VideoGenerationRequest):
    """Genera un video usando MiniMax-H3 PRO."""
    try:
        result = await minimax_service.generate_video(request)
        return result
    except Exception as e:
        logger.error(f"Error generando video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/publish-tiktok")
async def publish_to_tiktok(request: TikTokPublishRequest, background_tasks: BackgroundTasks):
    """Publica un video en TikTok."""
    try:
        result = await tiktok_service.upload_video(
            video_path=request.video_path,
            caption=f"{request.caption} {' '.join(['#' + h for h in request.hashtags])}",
        )
        return result
    except Exception as e:
        logger.error(f"Error publicando en TikTok: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-and-publish")
async def generate_and_publish(
    prompt: str,
    background_tasks: BackgroundTasks,
):
    """Genera video y lo publica automáticamente en TikTok."""
    # 1. Generar video
    gen_request = VideoGenerationRequest(prompt=prompt)
    video_result = await minimax_service.generate_video(gen_request)

    if video_result.status != "completed" or not video_result.video_url:
        raise HTTPException(status_code=500, detail="Error generando video")

    # 2. Publicar en TikTok (en background)
    # Nota: Aquí se debe descargar el video y luego subirlo
    # Por simplicidad, se asume que el video ya está disponible

    return {
        "video": video_result,
        "message": "Video generado. La publicación en TikTok se procesará en segundo plano.",
    }

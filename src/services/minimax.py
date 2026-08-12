import httpx
import asyncio
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger

from src.config import settings
from src.models.video import VideoGenerationRequest, VideoGenerationResponse, VideoStatus

class MiniMaxService:
    def __init__(self):
        self.api_key = settings.minimax_api_key
        self.base_url = settings.minimax_api_url
        self.client = httpx.AsyncClient(timeout=120.0)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate_video(self, request: VideoGenerationRequest) -> VideoGenerationResponse:
        """Genera un video usando MiniMax-H3 API."""
        payload = {
            "model": "MiniMax-Hailuo-03",
            "prompt": request.prompt,
            "resolution": request.resolution.value,
            "duration": request.duration,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            # 1. Crear tarea de generación
            create_response = await self.client.post(
                f"{self.base_url}/v2/video_generation",
                json=payload,
                headers=headers
            )
            create_response.raise_for_status()
            task_data = create_response.json()
            task_id = task_data.get("task_id")

            logger.info(f"MiniMax task created: {task_id}")

            # 2. Polling hasta que el video esté listo
            return await self._poll_task(task_id)

        except httpx.HTTPStatusError as e:
            logger.error(f"MiniMax API error: {e.response.text}")
            return VideoGenerationResponse(
                task_id="",
                status=VideoStatus.FAILED,
                error=f"API error: {e.response.status_code}"
            )
        except Exception as e:
            logger.error(f"MiniMax error: {str(e)}")
            return VideoGenerationResponse(
                task_id="",
                status=VideoStatus.FAILED,
                error=str(e)
            )

    async def _poll_task(self, task_id: str, max_attempts: int = 60) -> VideoGenerationResponse:
        """Polling del estado de la tarea de MiniMax."""
        headers = {"Authorization": f"Bearer {self.api_key}"}

        for attempt in range(max_attempts):
            try:
                response = await self.client.get(
                    f"{self.base_url}/v2/query/video_generation/{task_id}",
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()

                status = data.get("status")

                if status == "succeeded":
                    video_url = data.get("video_url") or data.get("content", {}).get("url")
                    return VideoGenerationResponse(
                        task_id=task_id,
                        status=VideoStatus.COMPLETED,
                        video_url=video_url
                    )

                elif status == "failed":
                    return VideoGenerationResponse(
                        task_id=task_id,
                        status=VideoStatus.FAILED,
                        error=data.get("error", "Unknown error")
                    )

                logger.info(f"MiniMax task {task_id} status: {status}, attempt {attempt+1}/{max_attempts}")
                await asyncio.sleep(5)

            except Exception as e:
                logger.error(f"Polling error: {str(e)}")
                await asyncio.sleep(5)

        return VideoGenerationResponse(
            task_id=task_id,
            status=VideoStatus.FAILED,
            error="Timeout waiting for video generation"
        )

    async def close(self):
        await self.client.aclose()

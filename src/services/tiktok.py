import httpx
import base64
import hashlib
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger

from src.config import settings

class TikTokService:
    def __init__(self):
        self.client_key = settings.tiktok_client_key
        self.client_secret = settings.tiktok_client_secret
        self.access_token = settings.tiktok_access_token
        self.base_url = "https://open.tiktokapis.com/v2"
        self.client = httpx.AsyncClient(timeout=180.0)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def upload_video(self, video_path: str, caption: str) -> dict:
        """
        Sube un video a TikTok usando Content Posting API.
        Flujo: init → upload → poll → publish
        """
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json; charset=UTF-8",
        }

        # 1. Inicializar la publicación
        init_payload = {
            "video_info": {
                "title": caption[:2200],
                "privacy_level": "PUBLIC",
                "disable_duet": False,
                "disable_comment": False,
                "disable_stitch": False,
            },
            "source": "PULL_FROM_HTTP",
        }

        logger.info(f"Iniciando upload TikTok para: {video_path}")

        init_response = await self.client.post(
            f"{self.base_url}/post/publish/video/init/",
            json=init_payload,
            headers=headers
        )
        init_response.raise_for_status()
        init_data = init_response.json()

        upload_url = init_data.get("data", {}).get("upload_url")
        publish_id = init_data.get("data", {}).get("publish_id")

        if not upload_url or not publish_id:
            raise ValueError(f"TikTok init failed: {init_data}")

        # 2. Subir el archivo a la URL de upload
        with open(video_path, "rb") as f:
            video_bytes = f.read()

        upload_headers = {
            "Content-Type": "video/mp4",
            "Content-Length": str(len(video_bytes)),
        }

        upload_response = await self.client.put(
            upload_url,
            content=video_bytes,
            headers=upload_headers
        )
        upload_response.raise_for_status()

        logger.info(f"Video subido a TikTok, publish_id: {publish_id}")

        # 3. Confirmar la publicación
        confirm_payload = {"publish_id": publish_id}

        confirm_response = await self.client.post(
            f"{self.base_url}/post/publish/video/confirm/",
            json=confirm_payload,
            headers=headers
        )
        confirm_response.raise_for_status()
        confirm_data = confirm_response.json()

        logger.info(f"Video publicado exitosamente en TikTok: {confirm_data}")

        return {
            "publish_id": publish_id,
            "status": confirm_data.get("data", {}).get("status", "PUBLISHED"),
            "share_url": confirm_data.get("data", {}).get("share_url"),
        }

    async def close(self):
        await self.client.aclose()

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class VideoResolution(str, Enum):
    HD = "768P"
    FULL_HD = "2K"

class VideoStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class VideoGenerationRequest(BaseModel):
    prompt: str = Field(..., min_length=10, max_length=500)
    resolution: VideoResolution = VideoResolution.FULL_HD
    duration: int = Field(10, ge=4, le=15)

class VideoGenerationResponse(BaseModel):
    task_id: str
    status: VideoStatus
    video_url: Optional[str] = None
    error: Optional[str] = None

class TikTokPublishRequest(BaseModel):
    video_path: str
    caption: str = Field(..., max_length=2200)
    hashtags: List[str] = Field(default_factory=list)
    privacy_level: str = "PUBLIC"

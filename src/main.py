from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.api.v1 import video, agent, webhooks
from src.config import settings
from src.core.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Eventos de ciclo de vida de la aplicación."""
    logger.info("🚀 Iniciando ARMATERRA API...")

    # Inicializar base de datos
    await init_db()

    logger.info("✅ ARMATERRA API iniciada correctamente")
    yield

    logger.info("👋 Cerrando ARMATERRA API...")

# Crear aplicación FastAPI
app = FastAPI(
    title="ARMATERRA API",
    description="API para automatización de videos, agente de ventas y publicación en TikTok",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(video.router, prefix="/api/v1/video", tags=["Video"])
app.include_router(agent.router, prefix="/api/v1/agent", tags=["Agent"])
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["Webhooks"])

@app.get("/")
async def root():
    return {
        "service": "ARMATERRA API",
        "version": "1.0.0",
        "status": "operational",
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

import os
import json
from typing import List, Dict, Any
from pgvector.sqlalchemy import Vector
from sqlalchemy import create_engine, Column, String, Text, JSON, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from openai import OpenAI
from loguru import logger

from src.config import settings

Base = declarative_base()
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536))
    metadata = Column(JSON, nullable=False)

class RAGService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.session = SessionLocal()

    def embed(self, text: str) -> List[float]:
        """Genera embedding para un texto."""
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )
        return response.data[0].embedding

    def query(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Consulta el RAG y retorna documentos relevantes."""
        query_embedding = self.embed(query)

        # Búsqueda por similitud
        stmt = select(Document).order_by(
            Document.embedding.cosine_distance(query_embedding)
        ).limit(top_k)

        results = self.session.execute(stmt).scalars().all()

        return [
            {
                "content": doc.content,
                "metadata": doc.metadata,
                "score": 1.0,  # simplificado
            }
            for doc in results
        ]

    def format_context(self, results: List[Dict[str, Any]]) -> str:
        """Formatea los resultados del RAG como contexto para el LLM."""
        if not results:
            return "No hay información disponible sobre este tema."

        context_parts = []
        for i, doc in enumerate(results):
            context_parts.append(f"[Documento {i+1}]\n{doc['content']}")

        return "\n\n---\n\n".join(context_parts)

# Instancia global
rag_service = RAGService()

def query_rag(query: str) -> str:
    """Función de acceso rápido al RAG."""
    results = rag_service.query(query)
    return rag_service.format_context(results)

# ARMATERRA API

**Sistema Autónomo de Generación de Video + Agente de Ventas para Bootcamp de Ciberseguridad**

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.11-009688.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.5.0-3b82f6.svg)](https://langchain-ai.github.io/langgraph/)
[![Docker](https://img.shields.io/badge/docker-✓-2496ED.svg)](https://www.docker.com/)

---

## 📋 Tabla de Contenidos

- [Visión General](#visión-general)
- [Arquitectura Técnica](#arquitectura-técnica)
- [Requisitos Previos](#requisitos-previos)
- [Instalación y Configuración](#instalación-y-configuración)
- [Variables de Entorno](#variables-de-entorno)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Uso de la API](#uso-de-la-api)
- [Flujo Completo del Sistema](#flujo-completo-del-sistema)
- [Observabilidad con Langfuse](#observabilidad-con-langfuse)
- [Comandos Útiles](#comandos-útiles)
- [Resolución de Problemas](#resolución-de-problemas)

---

## 🎯 Visión General

ARMATERRA es una plataforma de automatización de marketing y ventas diseñada específicamente para promocionar y vender un **bootcamp de ciberseguridad de 40 módulos**, impartido por un Doctor en Ingeniería de Software.

El sistema está compuesto por dos grandes máquinas independientes que operan en sinergia:

| Máquina | Función | Tecnologías |
|---------|---------|-------------|
| **Atractor de Leads** | Genera videos automáticos con MiniMax-H3 y los publica en TikTok | n8n, MiniMax-H3 API, TikTok API |
| **Vendedor Autónomo** | Responde DMs/comentarios, califica leads, cierra ventas con Link Bi | LangGraph, OpenAI, RAG, PostgreSQL |

**Principio rector:** El agente de ventas NO ejecuta herramientas ofensivas (Kali Linux). Eso se enseña **dentro del bootcamp**. La preventa es 100% comercial y educativa.

---

## 🏗️ Arquitectura Técnica

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           GOOGLE CLOUD INSTANCE                                 │
│                    (Docker Compose - Todos los servicios)                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────┐          ┌─────────────────────────┐               │
│  │     minimax-api         │          │     langgraph-api       │               │
│  │     (PORT 8001)         │◄────────►│     (PORT 8002)         │               │
│  └────────────┬────────────┘          └────────────┬────────────┘               │
│               │                                    │                             │
│               └──────────────┬─────────────────────┘                             │
│                              │                                                   │
│                              ▼                                                   │
│               ┌─────────────────────────────────────┐                           │
│               │         RAG COMPARTIDO              │                           │
│               │    PostgreSQL + pgvector            │                           │
│               │  (Temario, precios, FAQs, casos)    │                           │
│               └─────────────────────────────────────┘                           │
│                              │                                                   │
│                              ▼                                                   │
│               ┌─────────────────────────────────────┐                           │
│               │         Langfuse v4                 │                           │
│               │  (Observabilidad de ambos agentes)  │                           │
│               └─────────────────────────────────────┘                           │
│                              │                                                   │
│                              ▼                                                   │
│               ┌─────────────────────────────────────┐                           │
│               │         n8n (Orquestador)           │                           │
│               │  (Cron, Webhooks, Workflows)        │                           │
│               └─────────────────────────────────────┘                           │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

**Tecnologías validadas:**

| Componente | Versión | Fuente |
|------------|---------|--------|
| FastAPI | 0.115.11 | PyPI |
| LangGraph | 0.5.0 | PyPI |
| LangChain-OpenAI | 0.3.6 | PyPI |
| Langfuse | 3.4.0 | PyPI |
| pgvector | 0.3.6 | PyPI |
| MiniMax-H3 | API v2 | minimax.chat |
| TikTok API | v2 | developers.tiktok.com |
| Link Bi | v1 | Banco Industrial |

---

## 📦 Requisitos Previos

| Herramienta | Versión Mínima | Nota |
|-------------|----------------|------|
| **Python** | 3.12 | Recomendado 3.12+ |
| **Docker** | 24.0.0 | Para contenerización |
| **Docker Compose** | 2.20.0 | Para orquestación |
| **Git** | 2.40.0 | Control de versiones |
| **Google Cloud SDK** | 470.0.0 | Solo para despliegue |

**Cuentas externas requeridas:**
- ✅ TikTok for Developers (App ID: 7673159040817580049)
- ✅ MiniMax API Key
- ✅ OpenAI API Key
- ✅ Afiliación a Link Bi (Banco Industrial)
- ✅ Langfuse (self-hosted o cloud)

---

## 🔧 Instalación y Configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/armaterra-api.git
cd armaterra-api
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
nano .env  # Editar con tus credenciales
```

**Credenciales TikTok (ya tienes):**
```
TIKTOK_CLIENT_KEY=aw24bsc16xki0sk5
TIKTOK_CLIENT_SECRET=TU_SECRETO
TIKTOK_ACCESS_TOKEN=TU_TOKEN
TIKTOK_APP_ID=7673159040817580049
```

**Credenciales MiniMax:**
```
MINIMAX_API_KEY=TU_API_KEY
MINIMAX_API_URL=https://api.minimax.chat/v1
```

### 3. Levantar la infraestructura completa

```bash
# Construir y levantar todos los servicios
docker-compose up -d

# Verificar que todos los contenedores estén corriendo
docker-compose ps
```

**Servicios expuestos:**

| Servicio | Puerto | URL |
|----------|--------|-----|
| API REST | 8000 | http://localhost:8000 |
| Langfuse UI | 3000 | http://localhost:3000 |
| n8n UI | 5678 | http://localhost:5678 |
| PostgreSQL | 5432 | localhost:5432 |
| Redis | 6379 | localhost:6379 |

### 4. Inicializar la base de datos y cargar el RAG

```bash
# Crear tablas y cargar documentos del bootcamp
python scripts/init_db.py
python scripts/seed_rag.py
```

---

## 🌱 Variables de Entorno

```env
# ============================
# TIKTOK API
# ============================
TIKTOK_CLIENT_KEY=aw24bsc16xki0sk5
TIKTOK_CLIENT_SECRET=tu_secreto
TIKTOK_ACCESS_TOKEN=tu_token
TIKTOK_APP_ID=7673159040817580049

# ============================
# MINIMAX (Generación de Video)
# ============================
MINIMAX_API_KEY=tu_api_key
MINIMAX_API_URL=https://api.minimax.chat/v1

# ============================
# OPENAI (Agente LangGraph)
# ============================
OPENAI_API_KEY=tu_openai_key

# ============================
# BASE DE DATOS
# ============================
DATABASE_URL=postgresql://postgres:postgres@db:5432/armaterra
REDIS_URL=redis://redis:6379

# ============================
# LANGFUSE (Observabilidad)
# ============================
LANGFUSE_PUBLIC_KEY=tu_public_key
LANGFUSE_SECRET_KEY=tu_secret_key
LANGFUSE_HOST=http://langfuse:3000

# ============================
# LINK BI / MALL BI
# ============================
LINK_BI_API_KEY=tu_link_bi_key
LINK_BI_API_URL=https://api.link.bi/v1

# ============================
# N8N WEBHOOK
# ============================
N8N_WEBHOOK_URL=http://n8n:5678/webhook
```

---

## 📁 Estructura del Proyecto

```
armaterra-api/
├── .env.example                 # Plantilla de variables de entorno
├── .dockerignore                # Archivos ignorados en Docker
├── .gitignore                   # Archivos ignorados en Git
├── docker-compose.yml           # Orquestación de contenedores
├── Dockerfile                   # Imagen de la API
├── requirements.txt             # Dependencias Python
├── Makefile                     # Comandos comunes
├── README.md                    # Este archivo
│
├── src/
│   ├── __init__.py
│   ├── main.py                  # Punto de entrada FastAPI
│   ├── config.py                # Configuración con Pydantic Settings
│   │
│   ├── models/                  # Schemas Pydantic
│   │   ├── video.py
│   │   └── payment.py
│   │
│   ├── services/                # Lógica de negocio
│   │   ├── minimax.py           # Generación de video
│   │   ├── tiktok.py            # Publicación en TikTok
│   │   └── langgraph_agent.py   # Agente de ventas
│   │
│   ├── api/                     # Endpoints REST
│   │   ├── deps.py
│   │   └── v1/
│   │       ├── video.py
│   │       ├── agent.py
│   │       └── webhooks.py
│   │
│   ├── core/                    # Núcleo del sistema
│   │   ├── database.py          # Conexión a PostgreSQL
│   │   ├── redis_client.py      # Conexión a Redis
│   │   └── rag.py               # RAG compartido (pgvector)
│   │
│   └── utils/                   # Utilidades
│       └── logger.py            # Configuración de logueo
│
├── tests/
│   ├── test_minimax.py
│   └── test_tiktok.py
│
└── scripts/
    ├── init_db.py               # Inicializa tablas
    └── seed_rag.py              # Carga el RAG con el dossier del bootcamp
```

---

## 📡 Uso de la API

### 1. Generar un video con MiniMax-H3

```http
POST /api/v1/video/generate
Content-Type: application/json
```

```json
{
  "prompt": "Agente de IA en ciberseguridad escaneando una red con Kali Linux, estilo TikTok viral, texto flotante en español",
  "resolution": "2K",
  "duration": 10
}
```

**Respuesta:**
```json
{
  "task_id": "task_abc123",
  "status": "completed",
  "video_url": "https://minimax.com/video/abc123.mp4"
}
```

### 2. Publicar video en TikTok

```http
POST /api/v1/video/publish-tiktok
Content-Type: application/json
```

```json
{
  "video_path": "/app/videos/abc123.mp4",
  "caption": "¿Sabías que un agente de IA puede auditar tu red en 5 minutos?",
  "hashtags": ["ciberseguridad", "IA", "KaliLinux"],
  "privacy_level": "PUBLIC"
}
```

### 3. Interactuar con el Agente de Ventas

```http
POST /api/v1/agent/chat
Content-Type: application/json
```

```json
{
  "user_id": "tiktok_user_123",
  "message": "Hola, ¿cuánto cuesta el bootcamp?"
}
```

**Respuesta:**
```json
{
  "user_id": "tiktok_user_123",
  "response": "El bootcamp tiene 40 módulos. El precio es de $15 por módulo para estudiantes o $35 para empresas. Puedes pagar en cuotas sin interés. ¿Te gustaría inscribirte en el Módulo 1?",
  "payment_link": "https://link.bi/armaterra/tiktok_user_123"
}
```

### 4. Webhook de TikTok (para recibir comentarios/DMs)

```http
POST /api/v1/webhooks/tiktok
Content-Type: application/json
```

```json
{
  "event": "comment",
  "user_id": "tiktok_user_123",
  "message": "¿Qué herramientas de Kali se enseñan?",
  "comment_id": "123456789"
}
```

### 5. Webhook de Confirmación de Pago (Link Bi)

```http
POST /api/v1/webhooks/payment
Content-Type: application/json
```

```json
{
  "transaction_id": "pay_123456",
  "user_id": "tiktok_user_123",
  "amount": "117.00",
  "status": "completed",
  "module": 1
}
```

---

## 🔄 Flujo Completo del Sistema

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                              FLUJO DE VENTAS                                    │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  [n8n Cron]                                                                      │
│       │                                                                          │
│       ▼                                                                          │
│  [MiniMax-H3 API]  →  Genera video (10-15s en 2K)                              │
│       │                                                                          │
│       ▼                                                                          │
│  [TikTok API]  →  Publica video en perfil de ARMATERRA                         │
│       │                                                                          │
│       ▼                                                                          │
│  [Usuario comenta o envía DM]                                                   │
│       │                                                                          │
│       ▼                                                                          │
│  [Webhook TikTok]  →  n8n recibe evento → encola en Redis                      │
│       │                                                                          │
│       ▼                                                                          │
│  [LangGraph Agent]                                                              │
│       │                                                                          │
│       ├──► [Nodo: Clasificar Intención]  (precio, temario, hardware, compra)   │
│       │                                                                          │
│       ├──► [Nodo: Recuperar Contexto]  →  RAG (PostgreSQL + pgvector)          │
│       │                                                                          │
│       ├──► [Nodo: Generar Respuesta]  →  OpenAI GPT-4o-mini                    │
│       │                                                                          │
│       └──► [Nodo: Cerrar Venta]  →  Link Bi API  →  Genera link de pago        │
│                                                                                  │
│       ▼                                                                          │
│  [Langfuse]  →  Registra toda la traza (decisiones, costos, latencia)          │
│       │                                                                          │
│       ▼                                                                          │
│  [TikTok DM]  →  Responde al lead con el link de pago                          │
│                                                                                  │
│       ▼                                                                          │
│  [Usuario paga]  →  Link Bi confirma vía webhook                               │
│       │                                                                          │
│       ▼                                                                          │
│  [LangGraph]  →  Actualiza estado del lead → Activa acceso al módulo           │
│                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔍 Observabilidad con Langfuse

Langfuse captura automáticamente **cada decisión** del agente de ventas y **cada evento** del sistema de video.

### Vista de Traza (Trace)

```json
{
  "id": "trace_abc123",
  "name": "generate_response",
  "user_id": "tiktok_user_123",
  "input": {
    "message": "¿Cuánto cuesta el bootcamp?",
    "intent": "pregunta_precio",
    "context": "El bootcamp cuesta $15 por módulo para estudiantes..."
  },
  "output": {
    "response": "El precio es de $15 por módulo...",
    "should_close": true
  },
  "metadata": {
    "cost": 0.0025,
    "latency": 1.23,
    "tokens": 452
  }
}
```

### Acceso a Langfuse UI

```bash
# Abrir en el navegador
http://localhost:3000
```

**Credenciales por defecto:**
- Email: admin@armaterra.com
- Password: admin123

---

## 🛠️ Comandos Útiles

### Iniciar todos los servicios

```bash
docker-compose up -d
```

### Ver logs de un servicio específico

```bash
docker-compose logs -f api
docker-compose logs -f langfuse
docker-compose logs -f n8n
```

### Detener servicios

```bash
docker-compose down
```

### Detener y eliminar volúmenes (reinicio completo)

```bash
docker-compose down -v
```

### Reconstruir la API después de cambios

```bash
docker-compose build api
docker-compose up -d api
```

### Ejecutar pruebas

```bash
pytest tests/
```

---

## 🧪 Resolución de Problemas

### Error: "TikTok API: invalid_client"

**Solución:** Verificar que `TIKTOK_CLIENT_SECRET` esté correcto. Asegurar que la app esté en modo **Production** (no Sandbox).

### Error: "MiniMax API: insufficient balance"

**Solución:** Verificar que tengas crédito en la cuenta de MiniMax. Cargar crédito en el dashboard de MiniMax.

### Error: "Langfuse: database connection failed"

**Solución:** Asegurar que PostgreSQL esté corriendo. Verificar `DATABASE_URL` en `.env`.

### Error: "RAG: no documents found"

**Solución:** Ejecutar `python scripts/seed_rag.py` para cargar el dossier del bootcamp en la base de datos vectorial.

### Error: "Port already in use"

**Solución:** Cambiar los puertos en `docker-compose.yml` o detener servicios que estén usando los puertos 8000, 3000, 5678, 5432, 6379.

---

## 📊 Estado de los Servicios

| Servicio | Estado Esperado | URL de Verificación |
|----------|----------------|---------------------|
| API REST | ✅ Running | http://localhost:8000/health |
| Langfuse | ✅ Running | http://localhost:3000 |
| n8n | ✅ Running | http://localhost:5678 |
| PostgreSQL | ✅ Running | `docker-compose ps db` |
| Redis | ✅ Running | `docker-compose ps redis` |

---

## 📚 Referencias Externas

| Documentación | URL |
|---------------|-----|
| TikTok for Developers | https://developers.tiktok.com |
| MiniMax API | https://www.minimax.chat |
| LangGraph Docs | https://langchain-ai.github.io/langgraph/ |
| Langfuse Docs | https://langfuse.com/docs |
| pgvector | https://github.com/pgvector/pgvector |
| FastAPI | https://fastapi.tiangolo.com |

---

## 📄 Licencia

Este proyecto es propiedad de **ARMATERRA** y está destinado exclusivamente para el uso interno del bootcamp de ciberseguridad. No se permite su redistribución ni uso comercial sin autorización expresa.

---

**Versión:** 1.0.0
**Última actualización:** 12 de agosto de 2026
**Mantenido por:** ARMATERRA Team
```

from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langfuse import Langfuse
from loguru import logger
import json

from src.config import settings
from src.core.database import get_db_connection
from src.core.rag import query_rag

# === Estado del agente ===
class AgentState(TypedDict):
    user_id: str
    message: str
    conversation_history: List[dict]
    intent: str
    retrieved_context: Optional[str]
    response: Optional[str]
    payment_link: Optional[str]
    should_close: bool

class SalesAgent:
    def __init__(self):
        # Inicializar LLM
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=settings.openai_api_key,
            temperature=0.3,
        )

        # Inicializar Langfuse
        self.langfuse = Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            host=settings.langfuse_host,
        )

        # Checkpointer con PostgreSQL
        self.conn = get_db_connection()
        self.checkpointer = PostgresSaver(self.conn)
        self.checkpointer.setup()

        # Construir el grafo
        self.graph = self._build_graph()
        self.app = self.graph.compile(checkpointer=self.checkpointer)

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(AgentState)

        # Nodos
        workflow.add_node("classify_intent", self._classify_intent)
        workflow.add_node("retrieve_knowledge", self._retrieve_knowledge)
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("close_sale", self._close_sale)

        # Flujo
        workflow.set_entry_point("classify_intent")
        workflow.add_edge("classify_intent", "retrieve_knowledge")
        workflow.add_edge("retrieve_knowledge", "generate_response")

        # Condicional: si debe cerrar venta
        workflow.add_conditional_edges(
            "generate_response",
            self._should_close_condition,
            {
                "close": "close_sale",
                "end": END,
            }
        )
        workflow.add_edge("close_sale", END)

        return workflow

    def _classify_intent(self, state: AgentState) -> dict:
        """Clasifica la intención del mensaje."""
        trace = self.langfuse.trace(
            name="classify_intent",
            user_id=state["user_id"],
            input=state["message"],
        )

        prompt = f"""
        Clasifica la intención del siguiente mensaje de un lead interesado en un bootcamp de ciberseguridad.

        Mensaje: "{state['message']}"

        Opciones:
        - pregunta_precio: pregunta por costos
        - pregunta_temario: pregunta por contenido del curso
        - pregunta_hardware: pregunta por requisitos técnicos
        - objeción: expresa duda o resistencia
        - intención_compra: muestra alta intención de comprar
        - otro: cualquier otra cosa

        Responde SOLO con la categoría.
        """

        response = self.llm.invoke(prompt)
        intent = response.content.strip().lower()

        trace.update(output={"intent": intent})
        trace.end()

        return {"intent": intent}

    def _retrieve_knowledge(self, state: AgentState) -> dict:
        """Recupera contexto del RAG compartido."""
        trace = self.langfuse.trace(
            name="retrieve_knowledge",
            user_id=state["user_id"],
            input=state["message"],
        )

        # Consultar RAG
        context = query_rag(state["message"])

        trace.update(output={"context_length": len(context)})
        trace.end()

        return {"retrieved_context": context}

    def _generate_response(self, state: AgentState) -> dict:
        """Genera respuesta usando el contexto recuperado."""
        trace = self.langfuse.trace(
            name="generate_response",
            user_id=state["user_id"],
            input={
                "message": state["message"],
                "intent": state["intent"],
                "context": state["retrieved_context"],
            },
        )

        # Prompt del sistema (vendedor determinista)
        system_prompt = """
        Eres el asistente de ventas del bootcamp ARMATERRA.
        Tu objetivo es vender el bootcamp de 40 módulos sobre Agentes de IA en Ciberseguridad.

        Reglas:
        1. Basa tus respuestas ÚNICAMENTE en el contexto proporcionado.
        2. Si el lead pregunta por precio, responde con los precios oficiales:
           - Estudiante: $15 USD por módulo (Q117)
           - Empresa: $35 USD por módulo (Q273)
        3. Menciona que se puede pagar en cuotas sin interés.
        4. Si el lead muestra intención de compra, indícale que le generarás un link de pago.
        5. Siempre ofrece valor: menciona un módulo específico relevante.

        Contexto:
        {context}

        Historial de conversación:
        {history}
        """

        prompt = system_prompt.format(
            context=state["retrieved_context"],
            history=json.dumps(state["conversation_history"][-5:]),
        )

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": state["message"]},
        ]

        response = self.llm.invoke(messages)
        response_text = response.content

        # Detectar si debe cerrar venta
        should_close = "intención_compra" in state["intent"] or "precio" in state["message"].lower()

        trace.update(output={
            "response": response_text,
            "should_close": should_close,
        })
        trace.end()

        return {
            "response": response_text,
            "should_close": should_close,
        }

    def _should_close_condition(self, state: AgentState) -> str:
        """Decide si ir a cierre o terminar."""
        return "close" if state.get("should_close", False) else "end"

    def _close_sale(self, state: AgentState) -> dict:
        """Genera link de pago y cierra la venta."""
        trace = self.langfuse.trace(
            name="close_sale",
            user_id=state["user_id"],
            input={"message": state["message"]},
        )

        # Aquí se integra Link Bi / Mall Bi
        # Por ahora simulamos la generación del link
        payment_link = f"https://link.bi/armaterra/{state['user_id']}"

        response_text = f"""
        ¡Excelente decisión, {state['user_id']}!

        Aquí está tu link de pago para el bootcamp:
        🔗 {payment_link}

        Detalles:
        - Módulo 1: $15 USD (Q117) para estudiantes
        - Pago en cuotas sin interés disponible
        - Factura electrónica automática

        Una vez confirmado el pago, recibirás acceso al aula virtual.
        """

        trace.update(output={"payment_link": payment_link})
        trace.end()

        return {
            "response": response_text,
            "payment_link": payment_link,
            "should_close": False,
        }

    async def invoke(self, user_id: str, message: str) -> dict:
        """Ejecuta el agente con un mensaje."""
        config = {"configurable": {"thread_id": user_id}}

        # Recuperar historial
        history = []
        try:
            state = self.app.get_state(config)
            if state and state.values:
                history = state.values.get("conversation_history", [])
        except:
            pass

        # Actualizar historial
        history.append({"role": "user", "content": message})

        initial_state = {
            "user_id": user_id,
            "message": message,
            "conversation_history": history,
            "intent": "",
            "retrieved_context": "",
            "response": "",
            "payment_link": "",
            "should_close": False,
        }

        result = await self.app.ainvoke(initial_state, config=config)

        # Guardar historial actualizado
        result["conversation_history"].append({"role": "assistant", "content": result.get("response", "")})

        return result

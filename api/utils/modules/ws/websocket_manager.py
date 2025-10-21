from fastapi import WebSocket
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Mapeia user_id para a sua conexão WebSocket ativa
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"WebSocket conectado para o usuário: {user_id}")

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info(f"WebSocket desconectado para o usuário: {user_id}")

    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            try:
                await websocket.send_json(message)
                logger.debug(f"Mensagem enviada para {user_id}: {message}")
            except Exception as e:
                logger.error(f"Erro ao enviar mensagem para {user_id}: {e}. Desconectando.")
                self.disconnect(user_id)

# Crie uma única instância para ser usada em toda a aplicação
manager = ConnectionManager()
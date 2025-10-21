from typing import List, Optional, Dict, Any, Literal
from uuid import UUID
from sqlalchemy.orm import Session
from api.v1._database.models import Usuario
from api.v1._shared.schemas import UsuarioCreate, UsuarioUpdate, UsuarioView 
from api.v1.usuario.service import UsuarioService 
from api.v1.usuario.mapper import map_to_usuario_view, map_list_to_usuario_view
from api.v1._shared.base_use_case import BaseUseCase

class UsuarioUseCase(BaseUseCase[Usuario, UsuarioCreate, UsuarioUpdate, UsuarioView]):
    """
    Use case for Usuario entity.

    This class handles the business logic for Usuario operations.
    It inherits from BaseUseCase which provides common CRUD operations.
    """

    def __init__(self):
        """Initialize the UsuarioUseCase with its service and mappers."""
        super().__init__(
            service=UsuarioService(),
            entity_name="Usuario",
            map_to_view=map_to_usuario_view,
            map_list_to_view=map_list_to_usuario_view
        )
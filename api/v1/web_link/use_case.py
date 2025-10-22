from typing import Dict, Any, Optional, List, Literal
from sqlalchemy.orm import Session
from uuid import UUID

from api.v1._database.models import WebLink
from api.v1._shared.base_use_case import BaseUseCase
from api.v1._shared.schemas import WebLinkCreate, WebLinkUpdate, WebLinkView
from api.v1.web_link.mapper import map_list_to_web_link_view, map_to_web_link_view
from api.v1.web_link.service import WebLinkService
from api.utils.permissions import has_permission

class WebLinkUseCase(BaseUseCase[WebLink, WebLinkCreate, WebLinkUpdate, WebLinkView]):
    """
    Use case for WebLink entity.

    This class handles the business logic for WebLink operations.
    It inherits from BaseUseCase which provides common CRUD operations.
    """

    def __init__(self):
        """Initialize the WebLinkUseCase with its service and mappers."""
        super().__init__(
            service=WebLinkService(),
            entity_name="WebLink",
            map_to_view=map_to_web_link_view,
            map_list_to_view=map_list_to_web_link_view
        )

    async def get_all(
        self,
        db: Session,
        skip: int,
        limit: int,
        include: Optional[List[str]],
        filter_params: Optional[Dict[str, Dict[str, Any]]],
        sort_by: Optional[str],
        sort_dir: Optional[Literal["asc", "desc"]],
        search: Optional[str] = None,
        select_fields: Optional[str] = None,
        user_info: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Get all WebLinks with access control.
        
        Business Rule:
        - Admin (ADMIN permission): Can see all links from all users
        - Normal user (LINK permission): Can only see their own links
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            include: Related entities to include
            filter_params: Filtering parameters
            sort_by: Field to sort by
            sort_dir: Sort direction (asc or desc)
            search: Search term
            select_fields: Fields to select
            user_info: Usuario object from authentication
            
        Returns:
            Dictionary with total count and list of view models
        """
        if filter_params is None:
            filter_params = {}
        
        # Aplicar regra de negócio de acesso aos links
        if user_info:
            # Verificar se o usuário é admin
            is_admin = has_permission(user_info, "ADMIN")
            
            if not is_admin:
                # Usuário normal: filtrar apenas seus próprios links
                user_id = user_info.id if hasattr(user_info, 'id') else user_info
                if not isinstance(user_id, UUID):
                    user_id = UUID(str(user_id))
                
                # Adicionar filtro de usuario_id
                filter_params['usuario_id'] = {'eq': user_id}
        
        # Chamar o método base com os filtros aplicados
        # Se o usuário é admin, não passar user_info para evitar filtro automático por user_id
        user_info_for_base = None if (user_info and has_permission(user_info, "ADMIN")) else user_info
        
        return await super().get_all(
            db=db,
            skip=skip,
            limit=limit,
            include=include,
            filter_params=filter_params,
            sort_by=sort_by,
            sort_dir=sort_dir,
            search=search,
            select_fields=select_fields,
            user_info=user_info_for_base
        )

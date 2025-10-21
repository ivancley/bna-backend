
from api.v1._database.models import WebLink
from api.v1._shared.base_use_case import BaseUseCase
from api.v1._shared.schemas import WebLinkCreate, WebLinkUpdate, WebLinkView
from api.v1.web_link.mapper import map_list_to_web_link_view, map_to_web_link_view
from api.v1.web_link.service import WebLinkService

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

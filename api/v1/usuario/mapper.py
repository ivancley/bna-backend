from typing import List, Optional, Dict, Any, Type
from uuid import UUID

from api.v1._database.models import Usuario
from api.v1._shared.schemas import UsuarioView
from api.v1._shared.base_mapper import BaseMapper

class UsuarioMapper(BaseMapper[Usuario, UsuarioView]):
    """
    Mapper for Usuario entity.

    This class handles mapping between Usuario ORM models and UsuarioView Pydantic models.
    It inherits from BaseMapper which provides common mapping operations with caching.
    """

    def __init__(self):
        """Initialize the UsuarioMapper with its model class, view class, and relationship map."""
        # Define relationship map with forward declarations to avoid circular imports
        relationship_map = {
            
            'livros': {
                'mapper': lambda model, include: self._get_livro_mapper().map_to_view(model, include),
                'is_list': True,
                'model_class': 'Livro'  # String to avoid circular imports
            },
            
            'etiquetas': {
                'mapper': lambda model, include: self._get_etiqueta_mapper().map_to_view(model, include),
                'is_list': True,
                'model_class': 'Etiqueta'  # String to avoid circular imports
            },
            
            'aulas': {
                'mapper': lambda model, include: self._get_aula_mapper().map_to_view(model, include),
                'is_list': True,
                'model_class': 'Aula'  # String to avoid circular imports
            },
            
            'apresentacoes': {
                'mapper': lambda model, include: self._get_apresentacao_mapper().map_to_view(model, include),
                'is_list': True,
                'model_class': 'Apresentacao'  # String to avoid circular imports
            },
            
            'slides': {
                'mapper': lambda model, include: self._get_slide_mapper().map_to_view(model, include),
                'is_list': True,
                'model_class': 'Slide'  # String to avoid circular imports
            },
            
            'questoes': {
                'mapper': lambda model, include: self._get_questoes_mapper().map_to_view(model, include),
                'is_list': True,
                'model_class': 'Questoes'  # String to avoid circular imports
            },
            
            'layouts': {
                'mapper': lambda model, include: self._get_layout_mapper().map_to_view(model, include),
                'is_list': True,
                'model_class': 'Layout'  # String to avoid circular imports
            },
            
            'aulas_livro': {
                'mapper': lambda model, include: self._get_aula_livro_mapper().map_to_view(model, include),
                'is_list': True,
                'model_class': 'AulaLivro'  # String to avoid circular imports
            },
            
            'atividade_livro': {
                'mapper': lambda model, include: self._get_atividade_livro_mapper().map_to_view(model, include),
                'is_list': True,
                'model_class': 'AtividadeLivro'  # String to avoid circular imports
            },
            
            'apresentacao_livro': {
                'mapper': lambda model, include: self._get_apresentacao_livro_mapper().map_to_view(model, include),
                'is_list': True,
                'model_class': 'ApresentacaoLivro'  # String to avoid circular imports
            },
            
            'atividades': {
                'mapper': lambda model, include: self._get_atividade_mapper().map_to_view(model, include),
                'is_list': True,
                'model_class': 'Atividade'  # String to avoid circular imports
            }
            
        }

        super().__init__(
            model_class=Usuario,
            view_class=UsuarioView,
            entity_name="Usuario",
            relationship_map=relationship_map,
            sensitive_fields=['senha']
        )
    
    def _get_livro_mapper(self):
        """Get the LivroMapper instance (lazy loading to avoid circular imports)."""
        from api.v1.livro.mapper import livro_mapper
        return livro_mapper
    
    def _get_etiqueta_mapper(self):
        """Get the EtiquetaMapper instance (lazy loading to avoid circular imports)."""
        from api.v1.etiqueta.mapper import etiqueta_mapper
        return etiqueta_mapper
    
    def _get_aula_mapper(self):
        """Get the AulaMapper instance (lazy loading to avoid circular imports)."""
        from api.v1.aula.mapper import aula_mapper
        return aula_mapper
    
    def _get_apresentacao_mapper(self):
        """Get the ApresentacaoMapper instance (lazy loading to avoid circular imports)."""
        from api.v1.apresentacao.mapper import apresentacao_mapper
        return apresentacao_mapper
    
    def _get_slide_mapper(self):
        """Get the SlideMapper instance (lazy loading to avoid circular imports)."""
        from api.v1.slide.mapper import slide_mapper
        return slide_mapper
    
    def _get_questoes_mapper(self):
        """Get the QuestoesMapper instance (lazy loading to avoid circular imports)."""
        from api.v1.questoes.mapper import questoes_mapper
        return questoes_mapper
    
    def _get_layout_mapper(self):
        """Get the LayoutMapper instance (lazy loading to avoid circular imports)."""
        from api.v1.layout.mapper import layout_mapper
        return layout_mapper
    
    def _get_aula_livro_mapper(self):
        """Get the AulaLivroMapper instance (lazy loading to avoid circular imports)."""
        from api.v1.aula_livro.mapper import aula_livro_mapper
        return aula_livro_mapper
    
    def _get_atividade_livro_mapper(self):
        """Get the AtividadeLivroMapper instance (lazy loading to avoid circular imports)."""
        from api.v1.atividade_livro.mapper import atividade_livro_mapper
        return atividade_livro_mapper
    
    def _get_apresentacao_livro_mapper(self):
        """Get the ApresentacaoLivroMapper instance (lazy loading to avoid circular imports)."""
        from api.v1.apresentacao_livro.mapper import apresentacao_livro_mapper
        return apresentacao_livro_mapper
    
    def _get_atividade_mapper(self):
        """Get the AtividadeMapper instance (lazy loading to avoid circular imports)."""
        from api.v1.atividade.mapper import atividade_mapper
        return atividade_mapper
    

# Create a singleton instance
usuario_mapper = UsuarioMapper()

# Export the mapper functions to maintain backward compatibility
def map_to_usuario_view(
    model: Usuario,
    include: Optional[List[str]] = None,
    select_fields: Optional[str] = None,
) -> Optional[UsuarioView]:
    """Map a Usuario model to a UsuarioView."""
    return usuario_mapper.map_to_view(model, include, select_fields)

def map_list_to_usuario_view(
    models: List[Usuario],
    include: Optional[List[str]] = None,
    select_fields: Optional[str] = None,
) -> List[UsuarioView]:
    """Map a list of Usuario models to a list of UsuarioViews."""
    return usuario_mapper.map_list_to_view(models, include, select_fields)
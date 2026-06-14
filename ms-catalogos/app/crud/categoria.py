from app.crud.base import CRUDBase
from app.models.categoria import Categoria
from app.schemas.categoria import CategoriaCreate, CategoriaUpdate

crud_categoria = CRUDBase[Categoria, CategoriaCreate, CategoriaUpdate](Categoria)

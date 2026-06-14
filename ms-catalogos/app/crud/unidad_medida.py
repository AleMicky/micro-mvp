from app.crud.base import CRUDBase
from app.models.unidad_medida import UnidadMedida
from app.schemas.unidad_medida import UnidadMedidaCreate, UnidadMedidaUpdate

crud_unidad_medida = CRUDBase[UnidadMedida, UnidadMedidaCreate, UnidadMedidaUpdate](
    UnidadMedida
)

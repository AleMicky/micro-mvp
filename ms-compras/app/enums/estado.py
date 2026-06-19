from enum import StrEnum


class EstadoOrdenCompra(StrEnum):
    BORRADOR = "BORRADOR"
    APROBADA = "APROBADA"
    CANCELADA = "CANCELADA"


class EstadoRecepcionCompra(StrEnum):
    BORRADOR = "BORRADOR"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"

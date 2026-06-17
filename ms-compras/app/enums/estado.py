from enum import Enum


class EstadoDocumento(str, Enum):
    BORRADOR = "BORRADOR"
    PENDIENTE = "PENDIENTE"
    APROBADA = "APROBADA"
    RECHAZADA = "RECHAZADA"
    RECIBIDA = "RECIBIDA"
    CANCELADA = "CANCELADA"

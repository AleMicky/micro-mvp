-- DDL: ms-notificaciones
CREATE TABLE notificaciones (
    id              SERIAL          PRIMARY KEY,
    cliente_id      INTEGER,
    tipo            VARCHAR(100)    NOT NULL,
    contenido       TEXT            NOT NULL,
    evento_origen   VARCHAR(100)    NOT NULL,
    creado_en       TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_notificaciones_cliente ON notificaciones (cliente_id);
CREATE INDEX idx_notificaciones_evento ON notificaciones (evento_origen);

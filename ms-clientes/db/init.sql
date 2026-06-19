-- DDL: ms-clientes
CREATE OR REPLACE FUNCTION actualizar_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.actualizado_en = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TABLE clientes (
    id              SERIAL          PRIMARY KEY,
    codigo          VARCHAR(50)     NOT NULL,
    nombre          VARCHAR(200)    NOT NULL,
    email           VARCHAR(150),
    telefono        VARCHAR(50),
    documento       VARCHAR(50),
    direccion       TEXT,
    activo          BOOLEAN         NOT NULL DEFAULT TRUE,
    creado_en       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    actualizado_en  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_clientes_codigo UNIQUE (codigo)
);

CREATE TRIGGER trg_clientes_actualizado
    BEFORE UPDATE ON clientes
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

CREATE TABLE puntos_cliente (
    id              SERIAL          PRIMARY KEY,
    cliente_id      INTEGER         NOT NULL,
    puntos          INTEGER         NOT NULL DEFAULT 0,
    motivo          VARCHAR(200),
    referencia      VARCHAR(100),
    activo          BOOLEAN         NOT NULL DEFAULT TRUE,
    creado_en       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    actualizado_en  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_puntos_cliente FOREIGN KEY (cliente_id) REFERENCES clientes (id)
);

CREATE INDEX idx_puntos_cliente_id ON puntos_cliente (cliente_id);

CREATE TABLE historial_cliente (
    id              SERIAL          PRIMARY KEY,
    cliente_id      INTEGER         NOT NULL,
    tipo            VARCHAR(50)     NOT NULL,
    descripcion     TEXT,
    monto           NUMERIC(15, 2),
    referencia      VARCHAR(100),
    creado_en       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_historial_cliente FOREIGN KEY (cliente_id) REFERENCES clientes (id)
);

CREATE INDEX idx_historial_cliente_id ON historial_cliente (cliente_id);

CREATE TABLE descuentos_cliente (
    id              SERIAL          PRIMARY KEY,
    cliente_id      INTEGER         NOT NULL,
    porcentaje      NUMERIC(5, 2)   NOT NULL DEFAULT 0,
    descripcion     VARCHAR(200),
    vigente_desde   DATE,
    vigente_hasta   DATE,
    activo          BOOLEAN         NOT NULL DEFAULT TRUE,
    creado_en       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    actualizado_en  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_descuentos_cliente FOREIGN KEY (cliente_id) REFERENCES clientes (id)
);

CREATE INDEX idx_descuentos_cliente_id ON descuentos_cliente (cliente_id);

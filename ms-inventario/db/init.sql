-- ============================================================
-- DDL: ms-inventario
-- Base de datos exclusiva del microservicio de inventario
-- ============================================================

-- ── Función de auditoría ────────────────────────────────────
CREATE OR REPLACE FUNCTION actualizar_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.actualizado_en = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ── 1. almacenes ────────────────────────────────────────────
CREATE TABLE almacenes (
    id              SERIAL          PRIMARY KEY,
    codigo          VARCHAR(50)     NOT NULL,
    nombre          VARCHAR(150)    NOT NULL,
    direccion       TEXT,
    activo          BOOLEAN         NOT NULL DEFAULT TRUE,
    creado_en       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    actualizado_en  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_almacenes_codigo UNIQUE (codigo)
);

CREATE INDEX idx_almacenes_activo ON almacenes (activo);
CREATE INDEX idx_almacenes_nombre ON almacenes (nombre);

CREATE TRIGGER trg_almacenes_actualizado
    BEFORE UPDATE ON almacenes
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

-- ── 2. existencias ────────────────────────────────────────
CREATE TABLE existencias (
    id              SERIAL          PRIMARY KEY,
    producto_id     INTEGER         NOT NULL,
    almacen_id      INTEGER         NOT NULL,
    cantidad_actual NUMERIC(15, 4)  NOT NULL DEFAULT 0,
    stock_minimo    NUMERIC(15, 4)  NOT NULL DEFAULT 0,
    stock_maximo    NUMERIC(15, 4),
    activo          BOOLEAN         NOT NULL DEFAULT TRUE,
    creado_en       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    actualizado_en  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_existencias_almacen
        FOREIGN KEY (almacen_id) REFERENCES almacenes (id),
    CONSTRAINT uq_existencias_producto_almacen
        UNIQUE (producto_id, almacen_id),
    CONSTRAINT chk_existencias_cantidad_no_negativa
        CHECK (cantidad_actual >= 0)
);

CREATE INDEX idx_existencias_producto_id ON existencias (producto_id);
CREATE INDEX idx_existencias_almacen_id ON existencias (almacen_id);

CREATE TRIGGER trg_existencias_actualizado
    BEFORE UPDATE ON existencias
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

-- ── 3. transferencias_inventario ────────────────────────────
CREATE TABLE transferencias_inventario (
    id                  SERIAL          PRIMARY KEY,
    codigo              VARCHAR(50),
    almacen_origen_id   INTEGER         NOT NULL,
    almacen_destino_id  INTEGER         NOT NULL,
    estado              VARCHAR(30)     NOT NULL DEFAULT 'COMPLETADA',
    observaciones       TEXT,
    activo              BOOLEAN         NOT NULL DEFAULT TRUE,
    creado_en           TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    actualizado_en      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_transferencias_origen
        FOREIGN KEY (almacen_origen_id) REFERENCES almacenes (id),
    CONSTRAINT fk_transferencias_destino
        FOREIGN KEY (almacen_destino_id) REFERENCES almacenes (id),
    CONSTRAINT chk_transferencias_almacenes_distintos
        CHECK (almacen_origen_id <> almacen_destino_id)
);

CREATE INDEX idx_transferencias_origen ON transferencias_inventario (almacen_origen_id);
CREATE INDEX idx_transferencias_destino ON transferencias_inventario (almacen_destino_id);

CREATE TRIGGER trg_transferencias_actualizado
    BEFORE UPDATE ON transferencias_inventario
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

-- ── 4. ajustes_inventario ───────────────────────────────────
CREATE TABLE ajustes_inventario (
    id              SERIAL          PRIMARY KEY,
    codigo          VARCHAR(50),
    almacen_id      INTEGER         NOT NULL,
    motivo          TEXT,
    observaciones   TEXT,
    activo          BOOLEAN         NOT NULL DEFAULT TRUE,
    creado_en       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    actualizado_en  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_ajustes_almacen
        FOREIGN KEY (almacen_id) REFERENCES almacenes (id)
);

CREATE INDEX idx_ajustes_almacen_id ON ajustes_inventario (almacen_id);

CREATE TRIGGER trg_ajustes_actualizado
    BEFORE UPDATE ON ajustes_inventario
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

-- ── 5. movimientos_inventario ───────────────────────────────
CREATE TABLE movimientos_inventario (
    id                  SERIAL          PRIMARY KEY,
    tipo                VARCHAR(50)     NOT NULL,
    producto_id         INTEGER         NOT NULL,
    almacen_id          INTEGER         NOT NULL,
    cantidad            NUMERIC(15, 4)  NOT NULL,
    cantidad_anterior   NUMERIC(15, 4)  NOT NULL,
    cantidad_nueva      NUMERIC(15, 4)  NOT NULL,
    referencia_tipo     VARCHAR(50),
    referencia_id       INTEGER,
    observaciones       TEXT,
    creado_en           TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_movimientos_almacen
        FOREIGN KEY (almacen_id) REFERENCES almacenes (id),
    CONSTRAINT chk_movimientos_cantidad_positiva
        CHECK (cantidad > 0)
);

CREATE INDEX idx_movimientos_producto_id ON movimientos_inventario (producto_id);
CREATE INDEX idx_movimientos_almacen_id ON movimientos_inventario (almacen_id);
CREATE INDEX idx_movimientos_tipo ON movimientos_inventario (tipo);
CREATE INDEX idx_movimientos_creado_en ON movimientos_inventario (creado_en);
CREATE INDEX idx_movimientos_referencia ON movimientos_inventario (referencia_tipo, referencia_id);

-- ── 6. transferencia_detalles ───────────────────────────────
CREATE TABLE transferencia_detalles (
    id                  SERIAL          PRIMARY KEY,
    transferencia_id    INTEGER         NOT NULL,
    producto_id         INTEGER         NOT NULL,
    cantidad            NUMERIC(15, 4)  NOT NULL,
    creado_en           TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_transferencia_detalles_transferencia
        FOREIGN KEY (transferencia_id) REFERENCES transferencias_inventario (id)
            ON DELETE CASCADE,
    CONSTRAINT chk_transferencia_detalles_cantidad_positiva
        CHECK (cantidad > 0)
);

CREATE INDEX idx_transferencia_detalles_transferencia ON transferencia_detalles (transferencia_id);
CREATE INDEX idx_transferencia_detalles_producto ON transferencia_detalles (producto_id);

-- ── 7. ajuste_detalles ──────────────────────────────────────
CREATE TABLE ajuste_detalles (
    id                  SERIAL          PRIMARY KEY,
    ajuste_id           INTEGER         NOT NULL,
    producto_id         INTEGER         NOT NULL,
    cantidad_anterior   NUMERIC(15, 4)  NOT NULL,
    cantidad_nueva      NUMERIC(15, 4)  NOT NULL,
    diferencia          NUMERIC(15, 4)  NOT NULL,
    creado_en           TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_ajuste_detalles_ajuste
        FOREIGN KEY (ajuste_id) REFERENCES ajustes_inventario (id)
            ON DELETE CASCADE
);

CREATE INDEX idx_ajuste_detalles_ajuste ON ajuste_detalles (ajuste_id);
CREATE INDEX idx_ajuste_detalles_producto ON ajuste_detalles (producto_id);

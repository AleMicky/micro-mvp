-- ============================================================
-- DDL: ms-catalogos
-- Base de datos exclusiva del microservicio de catálogos
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── Función de auditoría ────────────────────────────────────
CREATE OR REPLACE FUNCTION actualizar_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.actualizado_en = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ── 1. categorias ───────────────────────────────────────────
CREATE TABLE categorias (
    id              SERIAL          PRIMARY KEY,
    codigo          VARCHAR(50)     NOT NULL,
    nombre          VARCHAR(150)    NOT NULL,
    descripcion     TEXT,
    activo          BOOLEAN         NOT NULL DEFAULT TRUE,
    creado_en       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    actualizado_en  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_categorias_codigo UNIQUE (codigo)
);

CREATE INDEX idx_categorias_activo ON categorias (activo);
CREATE INDEX idx_categorias_nombre ON categorias (nombre);

CREATE TRIGGER trg_categorias_actualizado
    BEFORE UPDATE ON categorias
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

-- ── 2. marcas ───────────────────────────────────────────────
CREATE TABLE marcas (
    id              SERIAL          PRIMARY KEY,
    codigo          VARCHAR(50)     NOT NULL,
    nombre          VARCHAR(150)    NOT NULL,
    descripcion     TEXT,
    activo          BOOLEAN         NOT NULL DEFAULT TRUE,
    creado_en       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    actualizado_en  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_marcas_codigo UNIQUE (codigo)
);

CREATE INDEX idx_marcas_activo ON marcas (activo);
CREATE INDEX idx_marcas_nombre ON marcas (nombre);

CREATE TRIGGER trg_marcas_actualizado
    BEFORE UPDATE ON marcas
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

-- ── 3. unidades_medida ──────────────────────────────────────
CREATE TABLE unidades_medida (
    id              SERIAL          PRIMARY KEY,
    codigo          VARCHAR(20)     NOT NULL,
    nombre          VARCHAR(100)    NOT NULL,
    abreviatura     VARCHAR(10)     NOT NULL,
    activo          BOOLEAN         NOT NULL DEFAULT TRUE,
    creado_en       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    actualizado_en  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_unidades_medida_codigo UNIQUE (codigo),
    CONSTRAINT uq_unidades_medida_abreviatura UNIQUE (abreviatura)
);

CREATE INDEX idx_unidades_medida_activo ON unidades_medida (activo);

CREATE TRIGGER trg_unidades_medida_actualizado
    BEFORE UPDATE ON unidades_medida
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

-- ── 4. productos ────────────────────────────────────────────
CREATE TABLE productos (
    id                  SERIAL          PRIMARY KEY,
    codigo              VARCHAR(50)     NOT NULL,
    codigo_barras       VARCHAR(50),
    nombre              VARCHAR(200)    NOT NULL,
    descripcion         TEXT,
    categoria_id        INTEGER         NOT NULL,
    marca_id            INTEGER,
    unidad_medida_id    INTEGER         NOT NULL,
    precio_base         NUMERIC(15, 2)  NOT NULL DEFAULT 0,
    estado              VARCHAR(30)     NOT NULL DEFAULT 'ACTIVO',
    activo              BOOLEAN         NOT NULL DEFAULT TRUE,
    creado_en           TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    actualizado_en      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_productos_codigo UNIQUE (codigo),
    CONSTRAINT fk_productos_categoria
        FOREIGN KEY (categoria_id) REFERENCES categorias (id),
    CONSTRAINT fk_productos_marca
        FOREIGN KEY (marca_id) REFERENCES marcas (id),
    CONSTRAINT fk_productos_unidad_medida
        FOREIGN KEY (unidad_medida_id) REFERENCES unidades_medida (id)
);

CREATE INDEX idx_productos_categoria_id ON productos (categoria_id);
CREATE INDEX idx_productos_marca_id ON productos (marca_id);
CREATE INDEX idx_productos_unidad_medida_id ON productos (unidad_medida_id);
CREATE INDEX idx_productos_activo ON productos (activo);
CREATE INDEX idx_productos_nombre ON productos (nombre);

CREATE TRIGGER trg_productos_actualizado
    BEFORE UPDATE ON productos
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

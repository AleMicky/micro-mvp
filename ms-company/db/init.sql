-- DDL: ms-company
CREATE OR REPLACE FUNCTION actualizar_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.actualizado_en = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TABLE ciudades (
    id              SERIAL          PRIMARY KEY,
    nombre          VARCHAR(150)    NOT NULL,
    departamento    VARCHAR(150),
    activo          BOOLEAN         NOT NULL DEFAULT TRUE,
    creado_en       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    actualizado_en  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_ciudades_nombre UNIQUE (nombre)
);

CREATE TRIGGER trg_ciudades_actualizado
    BEFORE UPDATE ON ciudades
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

CREATE TABLE companias (
    id              SERIAL          PRIMARY KEY,
    codigo          VARCHAR(50)     NOT NULL,
    nombre          VARCHAR(200)    NOT NULL,
    nit             VARCHAR(50),
    direccion       TEXT,
    telefono        VARCHAR(50),
    activo          BOOLEAN         NOT NULL DEFAULT TRUE,
    creado_en       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    actualizado_en  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_companias_codigo UNIQUE (codigo)
);

CREATE TRIGGER trg_companias_actualizado
    BEFORE UPDATE ON companias
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

CREATE TABLE sucursales (
    id              SERIAL          PRIMARY KEY,
    codigo          VARCHAR(50)     NOT NULL,
    nombre          VARCHAR(200)    NOT NULL,
    compania_id     INTEGER         NOT NULL,
    ciudad_id       INTEGER         NOT NULL,
    direccion       TEXT,
    activo          BOOLEAN         NOT NULL DEFAULT TRUE,
    creado_en       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    actualizado_en  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_sucursales_codigo UNIQUE (codigo),
    CONSTRAINT fk_sucursales_compania FOREIGN KEY (compania_id) REFERENCES companias (id),
    CONSTRAINT fk_sucursales_ciudad FOREIGN KEY (ciudad_id) REFERENCES ciudades (id)
);

CREATE INDEX idx_sucursales_compania ON sucursales (compania_id);
CREATE INDEX idx_sucursales_ciudad ON sucursales (ciudad_id);

CREATE TRIGGER trg_sucursales_actualizado
    BEFORE UPDATE ON sucursales
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

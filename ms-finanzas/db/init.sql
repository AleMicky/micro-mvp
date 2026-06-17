-- ms-finanzas schema
CREATE TABLE IF NOT EXISTS cuentas_por_cobrar (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    referencia_tipo VARCHAR(50),
    referencia_id INTEGER,
    tercero_id INTEGER,
    tercero_tipo VARCHAR(30),
    monto NUMERIC(14,2) NOT NULL,
    saldo NUMERIC(14,2) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    fecha_vencimiento VARCHAR(10),
    descripcion TEXT,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS cuentas_por_pagar (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    referencia_tipo VARCHAR(50),
    referencia_id INTEGER,
    tercero_id INTEGER,
    tercero_tipo VARCHAR(30),
    monto NUMERIC(14,2) NOT NULL,
    saldo NUMERIC(14,2) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    fecha_vencimiento VARCHAR(10),
    descripcion TEXT,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS cajas (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    saldo NUMERIC(14,2) NOT NULL DEFAULT 0,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS movimientos_caja (
    id SERIAL PRIMARY KEY,
    caja_id INTEGER NOT NULL REFERENCES cajas(id),
    tipo VARCHAR(20) NOT NULL,
    monto NUMERIC(14,2) NOT NULL,
    referencia VARCHAR(100),
    observaciones TEXT,
    creado_en VARCHAR(30)
);

CREATE TABLE IF NOT EXISTS bancos (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS cuentas_bancarias (
    id SERIAL PRIMARY KEY,
    banco_id INTEGER NOT NULL REFERENCES bancos(id),
    numero_cuenta VARCHAR(50) NOT NULL,
    saldo NUMERIC(14,2) NOT NULL DEFAULT 0,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS movimientos_bancarios (
    id SERIAL PRIMARY KEY,
    cuenta_bancaria_id INTEGER NOT NULL REFERENCES cuentas_bancarias(id),
    tipo VARCHAR(20) NOT NULL,
    monto NUMERIC(14,2) NOT NULL,
    referencia VARCHAR(100),
    observaciones TEXT,
    creado_en VARCHAR(30)
);

CREATE TABLE IF NOT EXISTS pagos (
    id SERIAL PRIMARY KEY,
    cuenta_pagar_id INTEGER NOT NULL REFERENCES cuentas_por_pagar(id),
    monto NUMERIC(14,2) NOT NULL,
    metodo VARCHAR(30) NOT NULL DEFAULT 'TRANSFERENCIA',
    referencia VARCHAR(100),
    fecha VARCHAR(10)
);

CREATE TABLE IF NOT EXISTS cobros (
    id SERIAL PRIMARY KEY,
    cuenta_cobrar_id INTEGER NOT NULL REFERENCES cuentas_por_cobrar(id),
    monto NUMERIC(14,2) NOT NULL,
    metodo VARCHAR(30) NOT NULL DEFAULT 'EFECTIVO',
    referencia VARCHAR(100),
    fecha VARCHAR(10)
);

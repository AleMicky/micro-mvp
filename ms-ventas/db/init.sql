-- ms-ventas schema
CREATE TABLE IF NOT EXISTS clientes (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    rfc VARCHAR(20),
    email VARCHAR(150),
    telefono VARCHAR(30),
    direccion TEXT,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS cotizaciones_venta (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    cliente_id INTEGER NOT NULL REFERENCES clientes(id),
    estado VARCHAR(20) NOT NULL DEFAULT 'BORRADOR',
    fecha VARCHAR(10),
    observaciones TEXT,
    total NUMERIC(14,2) NOT NULL DEFAULT 0,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS cotizacion_venta_detalles (
    id SERIAL PRIMARY KEY,
    cotizacion_id INTEGER NOT NULL REFERENCES cotizaciones_venta(id) ON DELETE CASCADE,
    producto_id INTEGER NOT NULL,
    cantidad NUMERIC(14,4) NOT NULL,
    precio_unitario NUMERIC(14,2) NOT NULL,
    subtotal NUMERIC(14,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS ventas (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    cliente_id INTEGER NOT NULL REFERENCES clientes(id),
    cotizacion_id INTEGER REFERENCES cotizaciones_venta(id),
    almacen_id INTEGER NOT NULL DEFAULT 1,
    estado VARCHAR(20) NOT NULL DEFAULT 'BORRADOR',
    fecha VARCHAR(10),
    observaciones TEXT,
    total NUMERIC(14,2) NOT NULL DEFAULT 0,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS venta_detalles (
    id SERIAL PRIMARY KEY,
    venta_id INTEGER NOT NULL REFERENCES ventas(id) ON DELETE CASCADE,
    producto_id INTEGER NOT NULL,
    cantidad NUMERIC(14,4) NOT NULL CHECK (cantidad = TRUNC(cantidad)),
    precio_unitario NUMERIC(14,2) NOT NULL,
    subtotal NUMERIC(14,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS facturas (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    venta_id INTEGER NOT NULL REFERENCES ventas(id),
    estado VARCHAR(20) NOT NULL DEFAULT 'FACTURADA',
    fecha VARCHAR(10),
    subtotal NUMERIC(14,2) NOT NULL DEFAULT 0,
    impuesto NUMERIC(14,2) NOT NULL DEFAULT 0,
    total NUMERIC(14,2) NOT NULL DEFAULT 0,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS factura_detalles (
    id SERIAL PRIMARY KEY,
    factura_id INTEGER NOT NULL REFERENCES facturas(id) ON DELETE CASCADE,
    producto_id INTEGER NOT NULL,
    cantidad NUMERIC(14,4) NOT NULL,
    precio_unitario NUMERIC(14,2) NOT NULL,
    subtotal NUMERIC(14,2) NOT NULL
);

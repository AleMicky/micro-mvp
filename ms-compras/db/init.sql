-- ms-compras schema
CREATE TABLE IF NOT EXISTS proveedores (
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

CREATE TABLE IF NOT EXISTS cotizaciones_compra (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    proveedor_id INTEGER NOT NULL REFERENCES proveedores(id),
    estado VARCHAR(20) NOT NULL DEFAULT 'BORRADOR',
    fecha VARCHAR(10),
    observaciones TEXT,
    total NUMERIC(14,2) NOT NULL DEFAULT 0,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS cotizacion_compra_detalles (
    id SERIAL PRIMARY KEY,
    cotizacion_id INTEGER NOT NULL REFERENCES cotizaciones_compra(id) ON DELETE CASCADE,
    producto_id INTEGER NOT NULL,
    cantidad NUMERIC(14,4) NOT NULL,
    precio_unitario NUMERIC(14,2) NOT NULL,
    subtotal NUMERIC(14,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS ordenes_compra (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    proveedor_id INTEGER NOT NULL REFERENCES proveedores(id),
    cotizacion_id INTEGER REFERENCES cotizaciones_compra(id),
    estado VARCHAR(20) NOT NULL DEFAULT 'BORRADOR',
    fecha VARCHAR(10),
    observaciones TEXT,
    total NUMERIC(14,2) NOT NULL DEFAULT 0,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS orden_compra_detalles (
    id SERIAL PRIMARY KEY,
    orden_id INTEGER NOT NULL REFERENCES ordenes_compra(id) ON DELETE CASCADE,
    producto_id INTEGER NOT NULL,
    cantidad NUMERIC(14,4) NOT NULL,
    precio_unitario NUMERIC(14,2) NOT NULL,
    subtotal NUMERIC(14,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS recepciones_compra (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    orden_id INTEGER NOT NULL REFERENCES ordenes_compra(id),
    almacen_id INTEGER NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'RECIBIDA',
    fecha VARCHAR(10),
    observaciones TEXT,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS recepcion_compra_detalles (
    id SERIAL PRIMARY KEY,
    recepcion_id INTEGER NOT NULL REFERENCES recepciones_compra(id) ON DELETE CASCADE,
    producto_id INTEGER NOT NULL,
    cantidad NUMERIC(14,4) NOT NULL
);

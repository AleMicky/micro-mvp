CREATE TABLE IF NOT EXISTS reportes_generados (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,
    parametros TEXT,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS exportaciones (
    id SERIAL PRIMARY KEY,
    tipo_reporte VARCHAR(50) NOT NULL,
    formato VARCHAR(10) NOT NULL,
    archivo VARCHAR(255),
    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

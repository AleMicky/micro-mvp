-- ============================================================
-- SEED: datos de prueba para ms-catalogos
-- Idempotente: se puede ejecutar varias veces sin duplicar
-- ============================================================

-- ── Categorías ──────────────────────────────────────────────
INSERT INTO categorias (codigo, nombre, descripcion) VALUES
    ('CAT-LACTEOS', 'Lácteos',   'Leche y derivados lácteos'),
    ('CAT-GRANOS',  'Granos',    'Arroz y cereales'),
    ('CAT-BEBIDAS', 'Bebidas',   'Gaseosas y bebidas')
ON CONFLICT (codigo) DO NOTHING;

-- ── Marcas ──────────────────────────────────────────────────
INSERT INTO marcas (codigo, nombre, descripcion) VALUES
    ('MAR-PIL',         'PIL',         'Lácteos PIL'),
    ('MAR-GRANO-ORO',   'Grano de Oro', 'Arroz y granos'),
    ('MAR-COCA-COLA',   'Coca-Cola',   'Bebidas Coca-Cola')
ON CONFLICT (codigo) DO NOTHING;

-- ── Unidades de medida ──────────────────────────────────────
INSERT INTO unidades_medida (codigo, nombre, abreviatura) VALUES
    ('UND', 'Unidad',    'UND'),
    ('BOL', 'Bolsa',     'BOL'),
    ('KG',  'Kilogramo', 'KG')
ON CONFLICT (codigo) DO NOTHING;

-- ── Productos ───────────────────────────────────────────────
INSERT INTO productos (codigo, codigo_barras, nombre, descripcion, categoria_id, marca_id, unidad_medida_id, precio_base) VALUES
    (
        'PROD-001',
        '777100100001',
        'Leche PIL 980cc',
        'Leche entera pasteurizada bolsa 980cc',
        (SELECT id FROM categorias WHERE codigo = 'CAT-LACTEOS'),
        (SELECT id FROM marcas WHERE codigo = 'MAR-PIL'),
        (SELECT id FROM unidades_medida WHERE codigo = 'BOL'),
        18.50
    ),
    (
        'PROD-002',
        '777100100002',
        'Arroz Grano de Oro 1kg',
        'Arroz blanco de grano largo bolsa 1kg',
        (SELECT id FROM categorias WHERE codigo = 'CAT-GRANOS'),
        (SELECT id FROM marcas WHERE codigo = 'MAR-GRANO-ORO'),
        (SELECT id FROM unidades_medida WHERE codigo = 'KG'),
        12.00
    ),
    (
        'PROD-003',
        '777100100003',
        'Coca-Cola 2L',
        'Bebida gaseosa sabor cola botella 2 litros',
        (SELECT id FROM categorias WHERE codigo = 'CAT-BEBIDAS'),
        (SELECT id FROM marcas WHERE codigo = 'MAR-COCA-COLA'),
        (SELECT id FROM unidades_medida WHERE codigo = 'UND'),
        12.50
    )
ON CONFLICT (codigo) DO NOTHING;

-- ── Precios de venta ────────────────────────────────────────
INSERT INTO precios_producto (producto_id, precio_venta, activo)
SELECT p.id, v.precio_venta, TRUE
FROM (VALUES
    ('PROD-001', 18.50),
    ('PROD-002', 12.00),
    ('PROD-003', 12.50)
) AS v(codigo, precio_venta)
JOIN productos p ON p.codigo = v.codigo
WHERE NOT EXISTS (
    SELECT 1 FROM precios_producto pp
    WHERE pp.producto_id = p.id AND pp.activo = TRUE
);

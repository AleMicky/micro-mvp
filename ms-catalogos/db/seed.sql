-- ============================================================
-- SEED: datos de prueba para ms-catalogos
-- Idempotente: se puede ejecutar varias veces sin duplicar
-- ============================================================

-- ── Categorías ──────────────────────────────────────────────
INSERT INTO categorias (codigo, nombre, descripcion) VALUES
    ('CAT-ELEC',  'Electrónica',    'Dispositivos y accesorios electrónicos'),
    ('CAT-ALIM',  'Alimentos',      'Productos comestibles y bebidas'),
    ('CAT-HOGAR', 'Hogar',          'Artículos para el hogar y limpieza'),
    ('CAT-ROPA',  'Ropa',           'Prendas de vestir y accesorios'),
    ('CAT-FERRE', 'Ferretería',     'Herramientas y materiales de construcción')
ON CONFLICT (codigo) DO NOTHING;

-- ── Marcas ──────────────────────────────────────────────────
INSERT INTO marcas (codigo, nombre, descripcion) VALUES
    ('MAR-SAMS',  'Samsung',        'Electrónica y electrodomésticos'),
    ('MAR-COCA',  'Coca-Cola',      'Bebidas gaseosas y refrescos'),
    ('MAR-NEST',  'Nestlé',         'Alimentos procesados y lácteos'),
    ('MAR-UNILE', 'Unilever',       'Productos de limpieza y cuidado personal'),
    ('MAR-NIKE',  'Nike',           'Calzado y ropa deportiva'),
    ('MAR-BOSCH', 'Bosch',          'Herramientas eléctricas y manuales')
ON CONFLICT (codigo) DO NOTHING;

-- ── Unidades de medida ──────────────────────────────────────
INSERT INTO unidades_medida (codigo, nombre, abreviatura) VALUES
    ('UND',  'Unidad',       'und'),
    ('KG',   'Kilogramo',    'kg'),
    ('LT',   'Litro',        'lt'),
    ('MT',   'Metro',        'm'),
    ('CAJ',  'Caja',         'caj'),
    ('PAR',  'Par',          'par')
ON CONFLICT (codigo) DO NOTHING;

-- ── Productos ───────────────────────────────────────────────
INSERT INTO productos (codigo, nombre, descripcion, categoria_id, marca_id, unidad_medida_id) VALUES
    (
        'PROD-001',
        'Smartphone Galaxy A54',
        'Teléfono inteligente 128GB, pantalla 6.4"',
        (SELECT id FROM categorias WHERE codigo = 'CAT-ELEC'),
        (SELECT id FROM marcas WHERE codigo = 'MAR-SAMS'),
        (SELECT id FROM unidades_medida WHERE codigo = 'UND')
    ),
    (
        'PROD-002',
        'Coca-Cola Original 2L',
        'Bebida gaseosa sabor cola, botella 2 litros',
        (SELECT id FROM categorias WHERE codigo = 'CAT-ALIM'),
        (SELECT id FROM marcas WHERE codigo = 'MAR-COCA'),
        (SELECT id FROM unidades_medida WHERE codigo = 'LT')
    ),
    (
        'PROD-003',
        'Leche Condensada La Lechera',
        'Leche condensada azucarada 390g',
        (SELECT id FROM categorias WHERE codigo = 'CAT-ALIM'),
        (SELECT id FROM marcas WHERE codigo = 'MAR-NEST'),
        (SELECT id FROM unidades_medida WHERE codigo = 'UND')
    ),
    (
        'PROD-004',
        'Detergente Líquido Omo',
        'Detergente para ropa, envase 3 litros',
        (SELECT id FROM categorias WHERE codigo = 'CAT-HOGAR'),
        (SELECT id FROM marcas WHERE codigo = 'MAR-UNILE'),
        (SELECT id FROM unidades_medida WHERE codigo = 'LT')
    ),
    (
        'PROD-005',
        'Zapatillas Air Max 90',
        'Calzado deportivo unisex, tallas 38-44',
        (SELECT id FROM categorias WHERE codigo = 'CAT-ROPA'),
        (SELECT id FROM marcas WHERE codigo = 'MAR-NIKE'),
        (SELECT id FROM unidades_medida WHERE codigo = 'PAR')
    ),
    (
        'PROD-006',
        'Taladro Percutor GSB 13 RE',
        'Taladro percutor 600W con maletín',
        (SELECT id FROM categorias WHERE codigo = 'CAT-FERRE'),
        (SELECT id FROM marcas WHERE codigo = 'MAR-BOSCH'),
        (SELECT id FROM unidades_medida WHERE codigo = 'UND')
    ),
    (
        'PROD-007',
        'Arroz Premium 1kg',
        'Arroz blanco de grano largo, bolsa 1kg',
        (SELECT id FROM categorias WHERE codigo = 'CAT-ALIM'),
        NULL,
        (SELECT id FROM unidades_medida WHERE codigo = 'KG')
    ),
    (
        'PROD-008',
        'Cable HDMI 2m',
        'Cable HDMI 2.0 de alta velocidad, 2 metros',
        (SELECT id FROM categorias WHERE codigo = 'CAT-ELEC'),
        NULL,
        (SELECT id FROM unidades_medida WHERE codigo = 'MT')
    )
ON CONFLICT (codigo) DO NOTHING;

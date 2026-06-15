-- ============================================================
-- SEED: datos iniciales para ms-auth
-- Idempotente: se puede ejecutar varias veces sin duplicar
-- Usuario admin: admin / Admin123456
-- ============================================================

-- ── Roles ───────────────────────────────────────────────────
INSERT INTO roles (codigo, nombre, descripcion) VALUES
    ('ADMIN',    'Administrador', 'Acceso total al sistema'),
    ('OPERADOR', 'Operador',      'Operaciones de catálogos e inventario'),
    ('CONSULTA', 'Consulta',      'Solo lectura')
ON CONFLICT (codigo) DO NOTHING;

-- ── Permisos ────────────────────────────────────────────────
INSERT INTO permisos (codigo, nombre, modulo) VALUES
    ('CATALOGOS_VER',          'Ver catálogos',              'CATALOGOS'),
    ('CATALOGOS_CREAR',        'Crear catálogos',            'CATALOGOS'),
    ('CATALOGOS_EDITAR',       'Editar catálogos',           'CATALOGOS'),
    ('CATALOGOS_ELIMINAR',     'Eliminar catálogos',         'CATALOGOS'),
    ('INVENTARIO_VER',         'Ver inventario',             'INVENTARIO'),
    ('INVENTARIO_CREAR',       'Crear inventario',           'INVENTARIO'),
    ('INVENTARIO_EDITAR',      'Editar inventario',          'INVENTARIO'),
    ('INVENTARIO_ELIMINAR',    'Eliminar inventario',        'INVENTARIO'),
    ('INVENTARIO_MOVIMIENTOS', 'Movimientos de inventario',  'INVENTARIO'),
    ('AUTH_USUARIOS_VER',      'Ver usuarios',               'AUTH'),
    ('AUTH_USUARIOS_CREAR',    'Gestionar usuarios',         'AUTH'),
    ('AUTH_ROLES_GESTIONAR',   'Gestionar roles y permisos', 'AUTH')
ON CONFLICT (codigo) DO NOTHING;

-- ── Permisos del rol ADMIN (todos) ──────────────────────────
INSERT INTO rol_permisos (rol_id, permiso_id)
SELECT r.id, p.id
FROM roles r
CROSS JOIN permisos p
WHERE r.codigo = 'ADMIN'
ON CONFLICT DO NOTHING;

-- ── Permisos del rol OPERADOR ───────────────────────────────
INSERT INTO rol_permisos (rol_id, permiso_id)
SELECT r.id, p.id
FROM roles r
JOIN permisos p ON p.codigo IN (
    'CATALOGOS_VER',
    'CATALOGOS_CREAR',
    'INVENTARIO_VER',
    'INVENTARIO_CREAR',
    'INVENTARIO_MOVIMIENTOS'
)
WHERE r.codigo = 'OPERADOR'
ON CONFLICT DO NOTHING;

-- ── Permisos del rol CONSULTA ───────────────────────────────
INSERT INTO rol_permisos (rol_id, permiso_id)
SELECT r.id, p.id
FROM roles r
JOIN permisos p ON p.codigo IN ('CATALOGOS_VER', 'INVENTARIO_VER')
WHERE r.codigo = 'CONSULTA'
ON CONFLICT DO NOTHING;

-- ── Usuario administrador ───────────────────────────────────
-- password: Admin123456
INSERT INTO usuarios (nombre_completo, nombre_usuario, correo, password_hash) VALUES
    (
        'Administrador del Sistema',
        'admin',
        'admin@test.com',
        '$2b$12$WCajcuRXqUv70J9ssL/.ROtA65Y/Z/rbm7SgccLOI8jlfvLwDidOi'
    )
ON CONFLICT (nombre_usuario) DO NOTHING;

-- ── Rol ADMIN al usuario admin ──────────────────────────────
INSERT INTO usuario_roles (usuario_id, rol_id)
SELECT u.id, r.id
FROM usuarios u
JOIN roles r ON r.codigo = 'ADMIN'
WHERE u.nombre_usuario = 'admin'
ON CONFLICT DO NOTHING;

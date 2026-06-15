-- ============================================================
-- DDL: ms-auth
-- Base de datos exclusiva del microservicio de autenticación
-- ============================================================

-- ── Función de auditoría ────────────────────────────────────
CREATE OR REPLACE FUNCTION actualizar_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.actualizado_en = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ── 1. usuarios ─────────────────────────────────────────────
CREATE TABLE usuarios (
    id                  SERIAL          PRIMARY KEY,
    nombre_completo     VARCHAR(200)    NOT NULL,
    nombre_usuario      VARCHAR(100)    NOT NULL,
    correo              VARCHAR(255)    NOT NULL,
    password_hash       VARCHAR(255)    NOT NULL,
    activo              BOOLEAN         NOT NULL DEFAULT TRUE,
    ultimo_login_en     TIMESTAMPTZ,
    creado_en           TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    actualizado_en      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_usuarios_nombre_usuario UNIQUE (nombre_usuario),
    CONSTRAINT uq_usuarios_correo UNIQUE (correo)
);

CREATE INDEX idx_usuarios_activo ON usuarios (activo);
CREATE INDEX idx_usuarios_nombre_usuario ON usuarios (nombre_usuario);
CREATE INDEX idx_usuarios_correo ON usuarios (correo);

CREATE TRIGGER trg_usuarios_actualizado
    BEFORE UPDATE ON usuarios
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

-- ── 2. roles ────────────────────────────────────────────────
CREATE TABLE roles (
    id              SERIAL          PRIMARY KEY,
    codigo          VARCHAR(50)     NOT NULL,
    nombre          VARCHAR(150)    NOT NULL,
    descripcion     TEXT,
    activo          BOOLEAN         NOT NULL DEFAULT TRUE,
    creado_en       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    actualizado_en  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_roles_codigo UNIQUE (codigo)
);

CREATE INDEX idx_roles_activo ON roles (activo);

CREATE TRIGGER trg_roles_actualizado
    BEFORE UPDATE ON roles
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

-- ── 3. permisos ─────────────────────────────────────────────
CREATE TABLE permisos (
    id              SERIAL          PRIMARY KEY,
    codigo          VARCHAR(80)     NOT NULL,
    nombre          VARCHAR(150)    NOT NULL,
    modulo          VARCHAR(50)     NOT NULL,
    descripcion     TEXT,
    activo          BOOLEAN         NOT NULL DEFAULT TRUE,
    creado_en       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    actualizado_en  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_permisos_codigo UNIQUE (codigo)
);

CREATE INDEX idx_permisos_activo ON permisos (activo);
CREATE INDEX idx_permisos_modulo ON permisos (modulo);

CREATE TRIGGER trg_permisos_actualizado
    BEFORE UPDATE ON permisos
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

-- ── 4. usuario_roles ────────────────────────────────────────
CREATE TABLE usuario_roles (
    usuario_id      INTEGER         NOT NULL,
    rol_id          INTEGER         NOT NULL,
    creado_en       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_usuario_roles PRIMARY KEY (usuario_id, rol_id),
    CONSTRAINT fk_usuario_roles_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE,
    CONSTRAINT fk_usuario_roles_rol
        FOREIGN KEY (rol_id) REFERENCES roles (id) ON DELETE CASCADE
);

CREATE INDEX idx_usuario_roles_rol_id ON usuario_roles (rol_id);

-- ── 5. rol_permisos ─────────────────────────────────────────
CREATE TABLE rol_permisos (
    rol_id          INTEGER         NOT NULL,
    permiso_id      INTEGER         NOT NULL,
    creado_en       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_rol_permisos PRIMARY KEY (rol_id, permiso_id),
    CONSTRAINT fk_rol_permisos_rol
        FOREIGN KEY (rol_id) REFERENCES roles (id) ON DELETE CASCADE,
    CONSTRAINT fk_rol_permisos_permiso
        FOREIGN KEY (permiso_id) REFERENCES permisos (id) ON DELETE CASCADE
);

CREATE INDEX idx_rol_permisos_permiso_id ON rol_permisos (permiso_id);

-- ── 6. refresh_tokens ───────────────────────────────────────
CREATE TABLE refresh_tokens (
    id              SERIAL          PRIMARY KEY,
    usuario_id      INTEGER         NOT NULL,
    token_hash      VARCHAR(255)    NOT NULL,
    expiracion_en   TIMESTAMPTZ     NOT NULL,
    revocado        BOOLEAN         NOT NULL DEFAULT FALSE,
    creado_en       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    revocado_en     TIMESTAMPTZ,

    CONSTRAINT fk_refresh_tokens_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
);

CREATE INDEX idx_refresh_tokens_usuario_id ON refresh_tokens (usuario_id);
CREATE INDEX idx_refresh_tokens_token_hash ON refresh_tokens (token_hash);
CREATE INDEX idx_refresh_tokens_revocado ON refresh_tokens (revocado);

-- ── 7. sesiones_login ───────────────────────────────────────
CREATE TABLE sesiones_login (
    id              SERIAL          PRIMARY KEY,
    usuario_id      INTEGER,
    ip_address      VARCHAR(45),
    user_agent      TEXT,
    exito           BOOLEAN         NOT NULL,
    mensaje         VARCHAR(255),
    creado_en       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_sesiones_login_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE SET NULL
);

CREATE INDEX idx_sesiones_login_usuario_id ON sesiones_login (usuario_id);
CREATE INDEX idx_sesiones_login_creado_en ON sesiones_login (creado_en);

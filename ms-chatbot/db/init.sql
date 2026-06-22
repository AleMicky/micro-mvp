-- DDL: ms-chatbot
CREATE OR REPLACE FUNCTION actualizar_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.actualizado_en = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TABLE chatbot_conversaciones (
    id              SERIAL          PRIMARY KEY,
    sesion_id       VARCHAR(100)    NOT NULL,
    canal           VARCHAR(20)     NOT NULL DEFAULT 'test',
    estado          VARCHAR(50)     NOT NULL DEFAULT 'menu',
    contexto        JSONB           NOT NULL DEFAULT '{}'::jsonb,
    cliente_id      INTEGER,
    creado_en       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    actualizado_en  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_chatbot_conversaciones_sesion UNIQUE (sesion_id)
);

CREATE INDEX idx_chatbot_conversaciones_sesion ON chatbot_conversaciones (sesion_id);
CREATE INDEX idx_chatbot_conversaciones_canal ON chatbot_conversaciones (canal);

CREATE TRIGGER trg_chatbot_conversaciones_actualizado
    BEFORE UPDATE ON chatbot_conversaciones
    FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

CREATE TABLE chatbot_mensajes (
    id                SERIAL          PRIMARY KEY,
    conversacion_id   INTEGER         NOT NULL REFERENCES chatbot_conversaciones(id) ON DELETE CASCADE,
    direccion         VARCHAR(10)     NOT NULL,
    origen            VARCHAR(10)     NOT NULL DEFAULT 'bot',
    texto             TEXT            NOT NULL,
    tipo_mensaje      VARCHAR(10)     NOT NULL DEFAULT 'texto',
    nombre_archivo    VARCHAR(255),
    wa_message_id     VARCHAR(100),
    creado_en         TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_chatbot_mensajes_wa_message_id UNIQUE (wa_message_id),
    CONSTRAINT ck_chatbot_mensajes_origen CHECK (origen IN ('cliente', 'bot', 'agente')),
    CONSTRAINT ck_chatbot_mensajes_tipo_mensaje CHECK (tipo_mensaje IN ('texto', 'imagen', 'documento'))
);

CREATE INDEX idx_chatbot_mensajes_conversacion ON chatbot_mensajes (conversacion_id);

CREATE TABLE chatbot_etiquetas (
    id              SERIAL          PRIMARY KEY,
    nombre          VARCHAR(50)     NOT NULL,
    color           VARCHAR(7)      NOT NULL DEFAULT '#64748b',
    creado_en       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_chatbot_etiquetas_nombre UNIQUE (nombre)
);

CREATE TABLE chatbot_conversacion_etiquetas (
    conversacion_id INTEGER NOT NULL REFERENCES chatbot_conversaciones(id) ON DELETE CASCADE,
    etiqueta_id      INTEGER NOT NULL REFERENCES chatbot_etiquetas(id) ON DELETE CASCADE,
    creado_en        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (conversacion_id, etiqueta_id)
);

CREATE INDEX idx_chatbot_conversacion_etiquetas_etiqueta ON chatbot_conversacion_etiquetas (etiqueta_id);

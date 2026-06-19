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
    texto             TEXT            NOT NULL,
    wa_message_id     VARCHAR(100),
    creado_en         TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_chatbot_mensajes_wa_message_id UNIQUE (wa_message_id)
);

CREATE INDEX idx_chatbot_mensajes_conversacion ON chatbot_mensajes (conversacion_id);

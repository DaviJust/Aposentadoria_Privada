CREATE TABLE IF NOT EXISTS perfil (
    id_usuario SERIAL PRIMARY KEY,
    renda_bruta_mensal NUMERIC(12, 2) NOT NULL CHECK (renda_bruta_mensal >= 0),
    gasto_mensal_aposentadoria NUMERIC(12, 2) NOT NULL CHECK (gasto_mensal_aposentadoria > 0),
    margem_gasto_percentual NUMERIC(5, 4) NOT NULL CHECK (margem_gasto_percentual >= 0),
    aporte_mensal NUMERIC(12, 2) NOT NULL CHECK (aporte_mensal >= 0),
    patrimonio_atual NUMERIC(14, 2) NOT NULL DEFAULT 0.00 CHECK (patrimonio_atual >= 0),
    meta_patrimonio NUMERIC(14, 2) NOT NULL CHECK (meta_patrimonio > 0),
    declara_ir_completo BOOLEAN NOT NULL DEFAULT FALSE,
    anos_ate_aposentadoria INT NOT NULL CHECK (anos_ate_aposentadoria > 0),
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS simulacoes_resultados (
    id_simulacao SERIAL PRIMARY KEY,
    id_usuario INT NOT NULL REFERENCES perfil(id_usuario) ON DELETE CASCADE,
    perfil_risco_calculado VARCHAR(20) NOT NULL,
    plano_recomendado VARCHAR(50) NOT NULL,
    probabilidade_sucesso NUMERIC(5, 2) NOT NULL,
    patrimonio_p10 NUMERIC(16, 2) NOT NULL,
    patrimonio_mediano_p50 NUMERIC(16, 2) NOT NULL,
    patrimonio_p90 NUMERIC(16, 2) NOT NULL,
    taxa_retirada_media NUMERIC(6, 2) NOT NULL,
    sustentavel BOOLEAN NOT NULL,
    executado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
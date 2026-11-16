export interface SimulacaoRequest {
    renda_bruta_mensal: number;
    gasto_mensal_aposentadoria: number;
    margem_gasto_percentual: number;
    aporte_mensal: number;
    patrimonio_atual: number;
    meta_patrimonio: number;
    declara_ir_completo: boolean;
    anos_ate_aposentadoria: number;
}

export interface ResultadoMonteCarlo {
    probabilidade_sucesso: number;
    patrimonio_p10: number;
    patrimonio_mediano_p50: number;
    patrimonio_p90: number;
    taxa_retirada_media_combinada: number;
    sustentavel: boolean;
}

export interface SimulacaoResponse {
    id_simulacao: number;
    renda_anual: number;
    perfil_calculado: string;
    plano_recomendado: string;
    tributacao_nota: string;
    simulacao: ResultadoMonteCarlo;
}

export interface HistoricoItem {
    id_simulacao: number;
    perfil_risco: string;
    plano_recomendado: string;
    probabilidade_sucesso: number;
    patrimonio_p10: number;
    patrimonio_mediano_p50: number;
    patrimonio_p90: number;
    taxa_retirada_media: number;
    sustentavel: boolean;
    executado_em: string;
}
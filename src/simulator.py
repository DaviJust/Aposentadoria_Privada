import numpy as np
from typing import Dict, Any, Tuple

from src.domain import (
    PARAMETROS_PERFIL,
    PerfilInvestidor,
)


def simular_cenarios_pca(
    perfil: PerfilInvestidor,
    retorno_base: float,
    volatilidade_base: float,
    n_simulacoes: int = 1000,
    seed: int = 42
) -> Dict[str, Any]:
    np.random.seed(seed)
    meses = perfil.anos_ate_aposentadoria * 12

    # 1. Simulação Monte Carlo no Espaço PCA (Acumulação de Capital)
    pca_x_profissional = np.random.normal(loc=0.0, scale=0.15, size=n_simulacoes)
    pca_y_mercado = np.random.normal(loc=0.0, scale=volatilidade_base, size=n_simulacoes)

    patrimonios_finais = []
    sucessos = 0

    for i in range(n_simulacoes):
        fator_aporte = max(0.5, 1.0 + pca_x_profissional[i])
        aporte_simulado = perfil.aporte_mensal * fator_aporte

        retorno_anual_simulado = max(0.01, retorno_base + pca_y_mercado[i])
        r_mensal = (1 + retorno_anual_simulado) ** (1 / 12) - 1

        fv_patrimonio = perfil.patrimonio_atual * ((1 + r_mensal) ** meses)
        fv_aportes = aporte_simulado * (((1 + r_mensal) ** meses - 1) / r_mensal)
        patrimonio_final = fv_patrimonio + fv_aportes

        patrimonios_finais.append(patrimonio_final)

        if patrimonio_final >= perfil.meta_patrimonio:
            sucessos += 1

    patrimonios_finais = np.array(patrimonios_finais)
    probabilidade_sucesso = (sucessos / n_simulacoes) * 100

    p10 = float(np.percentile(patrimonios_finais, 10))
    p50 = float(np.median(patrimonios_finais))
    p90 = float(np.percentile(patrimonios_finais, 90))

    # Classifica em qual percentil (P10, P50 ou P90) a meta é atingida
    if p10 >= perfil.meta_patrimonio:
        cenario_atingido = "P10"
    elif p50 >= perfil.meta_patrimonio:
        cenario_atingido = "P50"
    else:
        cenario_atingido = "P90"

    # 2. Análise Combinatória de Gastos (Margem Flexível)
    gasto_alvo_anual = perfil.gasto_mensal_aposentadoria * 12
    margem = perfil.margem_gasto_percentual

    # Criação da faixa de variação de gastos (Min, Alvo, Max)
    cenarios_gastos_anuais = np.linspace(
        gasto_alvo_anual * (1 - margem),
        gasto_alvo_anual * (1 + margem),
        num=5  # 5 combinações de custo de vida
    )

    # Matriz de combinações: Cruzamento de todos os patrimônios com todos os cenários de gasto
    todas_as_taxas = []
    for p in patrimonios_finais:
        if p > 0:
            taxas_p = (cenarios_gastos_anuais / p) * 100
            todas_as_taxas.extend(taxas_p)

    todas_as_taxas = np.array(todas_as_taxas)

    # Estatísticas Consolidadas da Combinatória
    taxa_retirada_media_combinada = np.mean(todas_as_taxas)
    desvio_padrao_taxa = np.std(todas_as_taxas)
    taxa_retirada_mediana = np.median(todas_as_taxas)

    return {
        "probabilidade_sucesso": round(float(probabilidade_sucesso), 2),
        "cenario_atingido": cenario_atingido,
        "patrimonio_p10": round(p10, 2),
        "patrimonio_mediano_p50": round(p50, 2),
        "patrimonio_p90": round(p90, 2),
        "margem_gasto_analisada": f"±{int(margem * 100)}%",
        "gasto_mensal_minimo": round(float((gasto_alvo_anual * (1 - margem)) / 12), 2),
        "gasto_mensal_maximo": round(float((gasto_alvo_anual * (1 + margem)) / 12), 2),
        "taxa_retirada_media_combinada": round(float(taxa_retirada_media_combinada), 2),
        "taxa_retirada_mediana": round(float(taxa_retirada_mediana), 2),
        "desvio_padrao_taxa": round(float(desvio_padrao_taxa), 2),
        "sustentavel": bool(taxa_retirada_media_combinada <= (retorno_base * 100))
    }


def _definir_estrategia_tributaria(perfil: PerfilInvestidor, renda_anual: float) -> Tuple[str, str]:
    """Define a modalidade (PGBL/VGBL), o regime (Regressiva/Progressiva) e a recomendação fiscal."""
    tabela_ir = "Regressiva" if perfil.anos_ate_aposentadoria >= 10 else "Progressiva"

    if perfil.renda_bruta_mensal < 6000.0 or not perfil.declara_ir_completo:
        plano = f"VGBL ({tabela_ir})"
        nota = (
            "Opte por VGBL: quando a renda mensal é menor que R$ 6.000,00 ou não há necessidade de "
            "declaração completa do IR, o VGBL é a melhor opção pois o imposto incide apenas sobre os rendimentos no resgate."
        )
    else:
        limite_pgbl_mensal = (renda_anual * 0.12) / 13
        plano = f"PGBL ({tabela_ir})"
        nota = (
            f"Como a renda mensal é igual ou superior a R$ 6.000,00 e há declaração completa do IR, "
            f"invista até R$ {limite_pgbl_mensal:.2f}/mês no PGBL para dedução de até 12% no IRPF."
        )

    return plano, nota


def recomendar_aposentadoria(perfil: PerfilInvestidor) -> Dict[str, Any]:
    renda_anual = perfil.renda_bruta_mensal * 13
    tolerancia = perfil.tolerancia_risco
    params = PARAMETROS_PERFIL[tolerancia]

    simulacao = simular_cenarios_pca(
        perfil=perfil,
        retorno_base=params['retorno'],
        volatilidade_base=params['volatilidade'],
        n_simulacoes=1000
    )

    plano_recomendado, tributacao_nota = _definir_estrategia_tributaria(perfil, renda_anual)

    return {
        "renda_anual": float(renda_anual),
        "perfil_calculado": tolerancia,
        "cenario_atingido": simulacao["cenario_atingido"],
        "plano_recomendado": plano_recomendado,
        "tributacao_nota": tributacao_nota,
        "simulacao": simulacao
    }
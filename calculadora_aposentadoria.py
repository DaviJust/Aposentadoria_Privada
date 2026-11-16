import numpy as np
from dataclasses import dataclass
from typing import Dict, Any, Tuple

# Constantes de configuração no escopo do módulo
PARAMETROS_PERFIL: Dict[str, Dict[str, float]] = {
    'conservador': {'retorno': 0.04, 'volatilidade': 0.03},
    'moderado':    {'retorno': 0.06, 'volatilidade': 0.06},
    'arrojado':    {'retorno': 0.08, 'volatilidade': 0.10}
}
TETO_ISENCAO_SIMPLIFICADA_ANUAL: float = 85000.0


@dataclass
class PerfilInvestidor:
    renda_bruta_mensal: float
    gasto_mensal_aposentadoria: float  # Gasto Alvo
    margem_gasto_percentual: float     # Ex: 0.15 (+/- 15% de margem de variação)
    aporte_mensal: float
    patrimonio_atual: float
    meta_patrimonio: float
    declara_ir_completo: bool
    anos_ate_aposentadoria: int

    @property
    def tolerancia_risco(self) -> str:
        """Classifica a tolerância ao risco com base na flexibilidade de gastos."""
        if self.margem_gasto_percentual <= 0.10:
            return 'conservador'
        elif self.margem_gasto_percentual <= 0.20:
            return 'moderado'
        else:
            return 'arrojado'


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
        "probabilidade_sucesso": round(probabilidade_sucesso, 2),
        "patrimonio_mediano_p50": round(np.median(patrimonios_finais), 2),
        "margem_gasto_analisada": f"±{int(margem * 100)}%",
        "gasto_mensal_minimo": round((gasto_alvo_anual * (1 - margem)) / 12, 2),
        "gasto_mensal_maximo": round((gasto_alvo_anual * (1 + margem)) / 12, 2),
        "taxa_retirada_media_combinada": round(taxa_retirada_media_combinada, 2),
        "taxa_retirada_mediana": round(taxa_retirada_mediana, 2),
        "desvio_padrao_taxa": round(desvio_padrao_taxa, 2),
        "sustentavel": taxa_retirada_media_combinada <= (retorno_base * 100)
    }


def _definir_estrategia_tributaria(perfil: PerfilInvestidor, renda_anual: float) -> Tuple[str, str]:
    """Define a modalidade (PGBL/VGBL), o regime (Regressiva/Progressiva) e a recomendação fiscal."""
    tabela_ir = "Regressiva" if perfil.anos_ate_aposentadoria >= 10 else "Progressiva"

    if perfil.declara_ir_completo and renda_anual > TETO_ISENCAO_SIMPLIFICADA_ANUAL:
        limite_pgbl_mensal = (renda_anual * 0.12) / 13
        plano = f"PGBL ({tabela_ir})"
        nota = (
            f"Como a renda anual supera a faixa de isenção/desconto simplificado e a declaração é completa, "
            f"invista até R$ {limite_pgbl_mensal:.2f}/mês no PGBL para dedução de até 12% no IRPF."
        )
    else:
        plano = f"VGBL ({tabela_ir})"
        nota = (
            "Opte por VGBL: para rendas menores, isentas ou declaração simplificada, o diferimento do PGBL "
            "não compensa e o VGBL garante imposto apenas sobre os rendimentos no resgate."
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
        "renda_anual": renda_anual,
        "perfil_calculado": tolerancia,
        "plano_recomendado": plano_recomendado,
        "tributacao_nota": tributacao_nota,
        "simulacao_pca": simulacao
    }


# Exemplo de Execução
if __name__ == "__main__":
    usuario = PerfilInvestidor(
        renda_bruta_mensal=3000.0,
        gasto_mensal_aposentadoria=1500.0,
        margem_gasto_percentual=0.15,      # Margem de ±15% -> classifica automaticamente como 'moderado'
        aporte_mensal=1400.0,
        patrimonio_atual=30000.0,
        meta_patrimonio=500000.0,
        declara_ir_completo=True,
        anos_ate_aposentadoria=20
    )

    resultado = recomendar_aposentadoria(usuario)
    sim = resultado['simulacao_pca']

    print("=== ANÁLISE COMBINATÓRIA COM MARGEM DE GASTOS ===")
    print(f"Perfil Calculado: {resultado['perfil_calculado'].capitalize()}")
    print(f"Plano Recomendado: {resultado['plano_recomendado']}")
    print(f"Nota Tributária: {resultado['tributacao_nota']}")
    print(f"Probabilidade de Atingir a Meta: {sim['probabilidade_sucesso']}%")
    print(f"Faixa de Gasto Mensal Analisada ({sim['margem_gasto_analisada']}): R$ {sim['gasto_mensal_minimo']} a R$ {sim['gasto_mensal_maximo']}")
    print(f"Taxa de Retirada Média Combinada: {sim['taxa_retirada_media_combinada']}% a.a.")
    print(f"Desvio Padrão da Taxa: ±{sim['desvio_padrao_taxa']}%")
    print(f"Plano Sustentável na Média das Combinações? {'SIM' if sim['sustentavel'] else 'NÃO'}")
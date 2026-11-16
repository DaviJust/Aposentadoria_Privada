from dataclasses import dataclass

PARAMETROS_PERFIL: Dict[str, Dict[str, float]] = {
    'conservador': {'retorno': 0.04, 'volatilidade': 0.03},
    'moderado':    {'retorno': 0.06, 'volatilidade': 0.06},
    'arrojado':    {'retorno': 0.08, 'volatilidade': 0.10}
}
TETO_ISENCAO_SIMPLIFICADA_ANUAL: float = 85000.0

@dataclass
class PerfilInvestidor:
    renda_bruta_mensal: float
    gasto_mensal_aposentadoria: float  
    margem_gasto_percentual: float     
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

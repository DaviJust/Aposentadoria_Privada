from src.domain import PerfilInvestidor
from src.simulator import recomendar_aposentadoria

if __name__ == "__main__":
    usuario = PerfilInvestidor(
        renda_bruta_mensal=3000.0,
        gasto_mensal_aposentadoria=1500.0,
        margem_gasto_percentual=0.15,
        aporte_mensal=1400.0,
        patrimonio_atual=30000.0,
        meta_patrimonio=500000.0,
        declara_ir_completo=True,
        anos_ate_aposentadoria=20,
    )

    resultado = recomendar_aposentadoria(usuario)
    sim = resultado["simulacao"]

    print("=== ANÁLISE COMBINATÓRIA COM MARGEM DE GASTOS ===")
    print(f"Perfil Calculado: {resultado['perfil_calculado'].capitalize()}")
    print(f"Plano Recomendado: {resultado['plano_recomendado']}")
    print(f"Probabilidade de Atingir a Meta: {sim['probabilidade_sucesso']}%")
    print(f"Patrimônio Mediano (P50): R$ {sim['patrimonio_mediano_p50']}")
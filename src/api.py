from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.database import SessionLocal, SimulacaoResultadoModel, init_db, salvar_simulacao
from src.domain import PerfilInvestidor
from src.simulator import recomendar_aposentadoria


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="API Simulador de Previdência Privada",
    description="Motor Monte Carlo para projeção patrimonial e estratégia tributária (PGBL/VGBL).",
    version="1.0.0",
    lifespan=lifespan,
)

# Libera requisições vindas do frontend React (Vite / localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SimulacaoRequest(BaseModel):
    renda_bruta_mensal: float = Field(..., ge=0, example=5000.0)
    gasto_mensal_aposentadoria: float = Field(..., gt=0, example=2500.0)
    margem_gasto_percentual: float = Field(..., ge=0, le=1.0, example=0.15)
    aporte_mensal: float = Field(..., ge=0, example=1500.0)
    patrimonio_atual: float = Field(0.0, ge=0, example=30000.0)
    meta_patrimonio: float = Field(..., gt=0, example=600000.0)
    declara_ir_completo: bool = Field(False, example=True)
    anos_ate_aposentadoria: int = Field(..., gt=0, example=20)


@app.post("/simular")
def executar_simulacao(dados: SimulacaoRequest):
    perfil = PerfilInvestidor(
        renda_bruta_mensal=dados.renda_bruta_mensal,
        gasto_mensal_aposentadoria=dados.gasto_mensal_aposentadoria,
        margem_gasto_percentual=dados.margem_gasto_percentual,
        aporte_mensal=dados.aporte_mensal,
        patrimonio_atual=dados.patrimonio_atual,
        meta_patrimonio=dados.meta_patrimonio,
        declara_ir_completo=dados.declara_ir_completo,
        anos_ate_aposentadoria=dados.anos_ate_aposentadoria,
    )

    resultado = recomendar_aposentadoria(perfil)
    id_simulacao = salvar_simulacao(perfil, resultado)

    return {
        "id_simulacao": id_simulacao,
        **resultado,
    }


@app.get("/historico")
def listar_historico(limite: int = 10):
    with SessionLocal() as db:
        registros = (
            db.query(SimulacaoResultadoModel)
            .order_by(SimulacaoResultadoModel.id_simulacao.desc())
            .limit(limite)
            .all()
        )
        return [
            {
                "id_simulacao": r.id_simulacao,
                "perfil_risco": r.perfil_risco_calculado,
                "plano_recomendado": r.plano_recomendado,
                "probabilidade_sucesso": float(r.probabilidade_sucesso),
                "patrimonio_p10": float(r.patrimonio_p10),
                "patrimonio_mediano_p50": float(r.patrimonio_mediano_p50),
                "patrimonio_p90": float(r.patrimonio_p90),
                "taxa_retirada_media": float(r.taxa_retirada_media),
                "sustentavel": r.sustentavel,
                "executado_em": r.executado_em,
            }
            for r in registros
        ]
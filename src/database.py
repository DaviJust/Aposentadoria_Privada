import os
from datetime import datetime, timezone
from typing import Any, Dict
from dotenv import load_dotenv
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from src.domain import PerfilInvestidor

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./aposentadoria.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class PerfilModel(Base):
    __tablename__ = "perfil"

    id_usuario = Column(Integer, primary_key=True, index=True, autoincrement=True)
    renda_bruta_mensal = Column(Numeric(12, 2), nullable=False)
    gasto_mensal_aposentadoria = Column(Numeric(12, 2), nullable=False)
    margem_gasto_percentual = Column(Numeric(5, 4), nullable=False)
    aporte_mensal = Column(Numeric(12, 2), nullable=False)
    patrimonio_atual = Column(Numeric(14, 2), nullable=False, default=0.00)
    meta_patrimonio = Column(Numeric(14, 2), nullable=False)
    declara_ir_completo = Column(Boolean, nullable=False, default=False)
    anos_ate_aposentadoria = Column(Integer, nullable=False)
    criado_em = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    simulacoes = relationship(
        "SimulacaoResultadoModel",
        back_populates="usuario",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint("renda_bruta_mensal >= 0", name="ck_renda_positiva"),
        CheckConstraint("gasto_mensal_aposentadoria > 0", name="ck_gasto_positivo"),
        CheckConstraint("margem_gasto_percentual >= 0", name="ck_margem_positiva"),
        CheckConstraint("aporte_mensal >= 0", name="ck_aporte_positivo"),
        CheckConstraint("patrimonio_atual >= 0", name="ck_patrimonio_positivo"),
        CheckConstraint("meta_patrimonio > 0", name="ck_meta_positiva"),
        CheckConstraint("anos_ate_aposentadoria > 0", name="ck_anos_positivo"),
    )


class SimulacaoResultadoModel(Base):
    __tablename__ = "simulacoes_resultados"
    

    id_simulacao = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_usuario = Column(
        Integer, ForeignKey("perfil.id_usuario", ondelete="CASCADE"), nullable=False
    )
    perfil_risco_calculado = Column(String(20), nullable=False)
    plano_recomendado = Column(String(50), nullable=False)
    probabilidade_sucesso = Column(Numeric(5, 2), nullable=False)
    patrimonio_p10 = Column(Numeric(16, 2), nullable=False)
    patrimonio_mediano_p50 = Column(Numeric(16, 2), nullable=False)
    patrimonio_p90 = Column(Numeric(16, 2), nullable=False)
    taxa_retirada_media = Column(Numeric(6, 2), nullable=False)
    sustentavel = Column(Boolean, nullable=False)
    executado_em = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    usuario = relationship("PerfilModel", back_populates="simulacoes")


def init_db() -> None:
    """Cria as tabelas no banco caso ainda não existam."""
    Base.metadata.create_all(bind=engine)


def salvar_simulacao(perfil: PerfilInvestidor, resultado: Dict[str, Any]) -> int:
    """Persiste o perfil e o resultado da simulação, retornando o id_simulacao."""
    sim = resultado["simulacao"]
    with SessionLocal() as db:
        novo_perfil = PerfilModel(
            renda_bruta_mensal=perfil.renda_bruta_mensal,
            gasto_mensal_aposentadoria=perfil.gasto_mensal_aposentadoria,
            margem_gasto_percentual=perfil.margem_gasto_percentual,
            aporte_mensal=perfil.aporte_mensal,
            patrimonio_atual=perfil.patrimonio_atual,
            meta_patrimonio=perfil.meta_patrimonio,
            declara_ir_completo=perfil.declara_ir_completo,
            anos_ate_aposentadoria=perfil.anos_ate_aposentadoria,
        )
        db.add(novo_perfil)
        db.flush()

        nova_simulacao = SimulacaoResultadoModel(
            id_usuario=novo_perfil.id_usuario,
            perfil_risco_calculado=resultado["perfil_calculado"],
            plano_recomendado=resultado["plano_recomendado"],
            probabilidade_sucesso=sim["probabilidade_sucesso"],
            patrimonio_p10=sim["patrimonio_p10"],
            patrimonio_mediano_p50=sim["patrimonio_mediano_p50"],
            patrimonio_p90=sim["patrimonio_p90"],
            taxa_retirada_media=sim["taxa_retirada_media_combinada"],
            sustentavel=sim["sustentavel"],
        )
        db.add(nova_simulacao)
        db.commit()
        db.refresh(nova_simulacao)
        return nova_simulacao.id_simulacao
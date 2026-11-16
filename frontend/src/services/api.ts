import type { HistoricoItem, SimulacaoRequest, SimulacaoResponse } from "../types/simulacao";

const API_URL = "http://localhost:8000";

export async function executarSimulacao(dados: SimulacaoRequest): Promise<SimulacaoResponse> {
    const response = await fetch(`${API_URL}/simular`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(dados),
    });

    if (!response.ok) {
        const erro = await response.json();
        throw new Error(erro.detail?.[0]?.msg || "Erro ao executar simulação.");
    }

    return response.json();
}

export async function buscarHistorico(limite = 10): Promise<HistoricoItem[]> {
    const response = await fetch(`${API_URL}/historico?limite=${limite}`);
    if (!response.ok) {
        throw new Error("Erro ao carregar histórico.");
    }
    return response.json();
}
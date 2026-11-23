import { useEffect, useState } from "react";
import { buscarHistorico, executarSimulacao } from "./services/api";
import type { HistoricoItem, SimulacaoRequest, SimulacaoResponse } from "./types/simulacao";

const formatarMoeda = (valor: number) =>
  valor.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

export function App() {
  const [rendaBrutaMensal, setRendaBrutaMensal] = useState<number>(5000);
  const [gastoMensalAtual, setGastoMensalAtual] = useState<number>(3000);
  const [gastoAposentadoria, setGastoAposentadoria] = useState<number>(2500);
  const [ganhoEsperado, setGanhoEsperado] = useState<number>(300);
  const [anosInvestimento, setAnosInvestimento] = useState<number>(20);
  const [aporteMensal, setAporteMensal] = useState<number>(1500);

  const [resultado, setResultado] = useState<SimulacaoResponse | null>(null);
  const [historico, setHistorico] = useState<HistoricoItem[]>([]);
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);

  // Calcula a porcentagem do ganho esperado em relação à renda bruta
  const porcentagemGanho = rendaBrutaMensal > 0 ? ganhoEsperado / rendaBrutaMensal : 0;

  // Calcula a variação percentual entre o gasto atual e o gasto na aposentadoria (limitada entre 0 e 1 para a API)
  const variacaoGasto =
    gastoMensalAtual > 0
      ? Math.abs(gastoMensalAtual - gastoAposentadoria) / gastoMensalAtual
      : porcentagemGanho;
  const margemPercentual = Math.min(1, Math.max(0, Number(variacaoGasto.toFixed(4))));

  const carregarHistorico = async () => {
    try {
      const lista = await buscarHistorico(10);
      setHistorico(lista);
    } catch {
      // Silencia caso a API ainda não tenha sido iniciada
    }
  };

  useEffect(() => {
    carregarHistorico();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setCarregando(true);
    setErro(null);

    // Meta patrimonial baseada no maior valor entre o gasto na aposentadoria e o ganho esperado (regra dos 4%)
    const rendaAlvoMensal = Math.max(gastoAposentadoria, ganhoEsperado);

    const payload: SimulacaoRequest = {
      renda_bruta_mensal: rendaBrutaMensal,
      gasto_mensal_aposentadoria: gastoAposentadoria,
      margem_gasto_percentual: margemPercentual,
      aporte_mensal: aporteMensal,
      patrimonio_atual: 0,
      meta_patrimonio: Math.max(1000, (rendaAlvoMensal * 12) / 0.04),
      declara_ir_completo: rendaBrutaMensal * 13 > 85000,
      anos_ate_aposentadoria: anosInvestimento,
    };

    try {
      const res = await executarSimulacao(payload);
      setResultado(res);
      await carregarHistorico();
    } catch (err: unknown) {
      setErro(err instanceof Error ? err.message : "Erro inesperado.");
    } finally {
      setCarregando(false);
    }
  };

  return (
    <div style={{ maxWidth: 960, margin: "0 auto", padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>Simulador de Previdência Privada</h1>
      <p>Projeção estocástica Monte Carlo e recomendação tributária (PGBL / VGBL).</p>

      <form
        onSubmit={handleSubmit}
        style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "2rem" }}
      >
        <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
          Renda bruta mensal (R$)
          <input
            type="number"
            min="0"
            step="0.01"
            value={rendaBrutaMensal}
            onChange={(e) => setRendaBrutaMensal(Number(e.target.value))}
            required
          />
        </label>

        <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
          Gasto mensal atual (R$)
          <input
            type="number"
            min="0"
            step="0.01"
            value={gastoMensalAtual}
            onChange={(e) => setGastoMensalAtual(Number(e.target.value))}
            required
          />
        </label>

        <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
          Quanto espera gastar quando se aposentar (R$/mês)
          <input
            type="number"
            min="1"
            step="0.01"
            value={gastoAposentadoria}
            onChange={(e) => setGastoAposentadoria(Number(e.target.value))}
            required
          />
        </label>

        <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
          Quanto você espera ganhar (R$/mês)
          <input
            type="number"
            min="1"
            step="0.01"
            value={ganhoEsperado}
            onChange={(e) => setGanhoEsperado(Number(e.target.value))}
            required
          />
          <small style={{ color: "#555" }}>
            Equivale a {(porcentagemGanho * 100).toFixed(2)}% da renda bruta
          </small>
        </label>

        <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
          Quantos anos você pretende investir
          <input
            type="number"
            min="1"
            value={anosInvestimento}
            onChange={(e) => setAnosInvestimento(Number(e.target.value))}
            required
          />
        </label>

        <label style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
          Quanto você pretende investir (R$/mês)
          <input
            type="number"
            min="0"
            step="0.01"
            value={aporteMensal}
            onChange={(e) => setAporteMensal(Number(e.target.value))}
            required
          />
        </label>

        <button type="submit" disabled={carregando} style={{ gridColumn: "span 2", padding: "0.75rem" }}>
          {carregando ? "Simulando 1.000 cenários..." : "Executar Simulação"}
        </button>
      </form>

      {erro && <p style={{ color: "red" }}>{erro}</p>}

      {resultado && (
        <section style={{ border: "1px solid #ccc", borderRadius: 8, padding: "1.5rem", marginBottom: "2rem" }}>
          <h2>Resultado da Simulação #{resultado.id_simulacao}</h2>
          <p><strong>Perfil Calculado:</strong> {resultado.perfil_calculado}</p>
          <p><strong>Plano Recomendado:</strong> {resultado.plano_recomendado}</p>
          <p><strong>Nota Tributária:</strong> {resultado.tributacao_nota}</p>
          <hr />
          <p><strong>Probabilidade de Sucesso:</strong> {resultado.simulacao.probabilidade_sucesso}%</p>
          <ul>
            <li>Cenário Conservador (P10): {formatarMoeda(resultado.simulacao.patrimonio_p10)}</li>
            <li>Cenário Mediano (P50): {formatarMoeda(resultado.simulacao.patrimonio_mediano_p50)}</li>
            <li>Cenário Otimista (P90): {formatarMoeda(resultado.simulacao.patrimonio_p90)}</li>
          </ul>
          <p><strong>Sustentável?</strong> {resultado.simulacao.sustentavel ? "Sim" : "Não"}</p>
        </section>
      )}

      <section>
        <h2>Histórico Recente</h2>
        <table width="100%" border={1} cellPadding={8} style={{ borderCollapse: "collapse" }}>
          <thead>
            <tr>
              <th>ID</th>
              <th>Perfil</th>
              <th>Plano</th>
              <th>Sucesso</th>
              <th>Mediana (P50)</th>
              <th>Sustentável</th>
            </tr>
          </thead>
          <tbody>
            {historico.map((item) => (
              <tr key={item.id_simulacao}>
                <td>#{item.id_simulacao}</td>
                <td>{item.perfil_risco}</td>
                <td>{item.plano_recomendado}</td>
                <td>{item.probabilidade_sucesso}%</td>
                <td>{formatarMoeda(item.patrimonio_mediano_p50)}</td>
                <td>{item.sustentavel ? "Sim" : "Não"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}

export default App;
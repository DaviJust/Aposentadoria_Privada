import { useEffect, useState } from "react";
import { buscarHistorico, executarSimulacao } from "./services/api";
import type { HistoricoItem, SimulacaoRequest, SimulacaoResponse } from "./types/simulacao";

const formatarMoeda = (valor: number) =>
  valor.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

export function App() {
  const [form, setForm] = useState<SimulacaoRequest>({
    renda_bruta_mensal: 5000,
    gasto_mensal_aposentadoria: 2500,
    margem_gasto_percentual: 0.15,
    aporte_mensal: 1500,
    patrimonio_atual: 30000,
    meta_patrimonio: 600000,
    declara_ir_completo: true,
    anos_ate_aposentadoria: 20,
  });

  const [resultado, setResultado] = useState<SimulacaoResponse | null>(null);
  const [historico, setHistorico] = useState<HistoricoItem[]>([]);
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);

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

    try {
      const res = await executarSimulacao(form);
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
        <label>
          Renda Bruta Mensal (R$)
          <input
            type="number"
            value={form.renda_bruta_mensal}
            onChange={(e) => setForm({ ...form, renda_bruta_mensal: Number(e.target.value) })}
            required
          />
        </label>

        <label>
          Gasto Mensal na Aposentadoria (R$)
          <input
            type="number"
            value={form.gasto_mensal_aposentadoria}
            onChange={(e) => setForm({ ...form, gasto_mensal_aposentadoria: Number(e.target.value) })}
            required
          />
        </label>

        <label>
          Margem de lucro(0 a 1, ex: 0.15)
          <input
            type="number"
            step="0.01"
            min="0"
            max="1"
            value={form.margem_gasto_percentual}
            onChange={(e) => setForm({ ...form, margem_gasto_percentual: Number(e.target.value) })}
            required
          />
        </label>

        <label>
          Aporte Mensal (R$)
          <input
            type="number"
            value={form.aporte_mensal}
            onChange={(e) => setForm({ ...form, aporte_mensal: Number(e.target.value) })}
            required
          />
        </label>

        <label>
          Patrimônio Atual (R$)
          <input
            type="number"
            value={form.patrimonio_atual}
            onChange={(e) => setForm({ ...form, patrimonio_atual: Number(e.target.value) })}
          />
        </label>

        <label>
          Meta de Patrimônio (R$)
          <input
            type="number"
            value={form.meta_patrimonio}
            onChange={(e) => setForm({ ...form, meta_patrimonio: Number(e.target.value) })}
            required
          />
        </label>

        <label>
          Anos até Aposentadoria
          <input
            type="number"
            value={form.anos_ate_aposentadoria}
            onChange={(e) => setForm({ ...form, anos_ate_aposentadoria: Number(e.target.value) })}
            required
          />
        </label>

        <label style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <input
            type="checkbox"
            checked={form.declara_ir_completo}
            onChange={(e) => setForm({ ...form, declara_ir_completo: e.target.checked })}
          />
          Faz declaração completa do IR?
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
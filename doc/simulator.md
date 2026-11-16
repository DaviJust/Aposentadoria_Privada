## Introdução (`src/simulator.py`)

* **Definição 1**: arquivo `src/simulator.py` concentra todo o motor matemático e tributário da aplicação. Ele recebe o formulário validado de `src/domain.py`, processa os 1.000 cenários estocásticos de forma vetorizada via NumPy e aplica a árvore de decisão fiscal brasileira.
* **Definição 2**: Calcula a probabilidade do usuário ter exito no investimento de aposentadoria.
---
## Bilioteca

---
## Qual Matemática Foi Aplicada?

### Simulação Monte Carlo
* **Definição 1**:As empresas usam métodos de Monte Carlo para avaliar riscos e fazer previsões exatas de longo prazo. Ex:  viabilidade de aumentar o orçamento de publicidade, previsões referente a variação de preços e rentabilidades no mercado financeiro, programadores de jogos usam o método de Monte Carlo para simular resultados e garantir uma experiência de jogo justo em apostas.
* **Definição 2**: O método Monte Carlo utiliza de diversos cenários possíveis de valores para calcular uma probabilidade mais exata.
* **Definição 3**: Simulação de Monte Carlo cria um modelo de resultados possíveis aproveitando uma distribuição de probabilidade, como uma distribuição uniforme ou normal, para qualquer variável que tenha incerteza inerente. Em seguida, ela recalcula os resultados repetidamente, cada vez usando um conjunto diferente de números aleatórios entre os valores mínimo e máximo. Em um experimento típico de Monte Carlo, esse exercício pode ser repetido milhares de vezes para produzir um grande número de resultados prováveis.

* **Exemplo**:
Ao usarmos essa ferramenta matemática, podemos observar as diferentes variações de uma função.
![alt text]({AE33BCFA-5DB1-4735-A683-F8ECC1FC324F}.png)
Ou seja, a Simulação de Monte Carlo troca a derivação matemática complexa pela repetição computacional: o algoritmo sorteia $N = 1.000$ trajetórias possíveis de carreira e mercado e verifica em quantas delas o patrimônio final $VF^{(i)}$ atinge ou supera a meta desejada:

$$\hat{P} = \frac{1}{N} \sum_{i=1}^{N} \mathbb{1}\left\{ VF^{(i)} \ge \text{Meta} \right\}$$

Na equação acima, o símbolo $\mathbb{1}\{\cdot\}$ (função indicadora) vale **1** quando o cenário sorteado atinge ou supera a meta de patrimônio, e **0** nos demais casos. Ao somar os sucessos e dividir pelo total de cenários $N$, obtemos a estimativa empírica da probabilidade de sucesso do plano. 


## Componentes

### 1. Função `simular_cenarios_monte_carlo(...)`

Executa a projeção probabilística de acumulação de patrimônio e cruza os resultados com diferentes faixas de custo de vida na aposentadoria.

* **`rng = np.random.default_rng(seed)`**:
  * **Definição 1**: Fixa a semente dos números aleatórios (como `seed = 42`) para garantir que rodar o sistema várias vezes com os mesmos dados gere sempre os mesmos 1.000 cenários.
  * **Definição 2**: Instancia um gerador pseudoaleatório isolado (`Generator` do NumPy) com estado determinístico, evitando efeitos colaterais globais em ambientes concorrentes como APIs.

* **`meses = perfil.anos_ate_aposentadoria * 12`**:
  * **Definição 1**: Converte o prazo restante até a aposentadoria de anos para meses, alinhando o tempo ao ritmo mensal dos aportes e juros compostos.
  * **Definição 2**: Calcula o número total de períodos discretos de capitalização ($n = t \times 12$).

* **`choque_renda = rng.normal(loc=0.0, scale=0.15, size=n_simulacoes)`**:
  * **Definição 1**: Sorteia 1.000 variações possíveis para a trajetória profissional do investidor (promoções, bônus ou períodos de aperto) que afetam quanto ele consegue guardar por mês.
  * **Definição 2**: Amostra $N$ realizações independentes de uma distribuição normal $\mathcal{N}(0, 0.15^2)$ representando choques estocásticos na capacidade de poupança.

* **`choque_mercado = rng.normal(loc=0.0, scale=volatilidade_base, size=n_simulacoes)`**:
  * **Definição 1**: Sorteia 1.000 cenários de oscilação da economia e do mercado financeiro respeitando o nível de risco (`volatilidade_base`) do perfil escolhido.
  * **Definição 2**: Amostra $N$ choques macroeconômicos de uma distribuição normal $\mathcal{N}(0, \sigma_{\text{perfil}}^2)$ que perturbam a taxa esperada de retorno real anual.

* **`fator_aporte = np.maximum(0.5, 1.0 + choque_renda)`**:
  * **Definição 1**: Calcula o multiplicador de cada aporte mensal aplicando um piso mínimo de `0.5` (50%), impedindo que uma queda brusca zere ou torne negativo o valor investido.
  * **Definição 2**: Aplica uma operação vetorizada de truncamento inferior (*floor*) sobre o fator de ajuste de renda para garantir aportes estritamente positivos.

* **`aporte_simulado = perfil.aporte_mensal * fator_aporte`**:
  * **Definição 1**: Define o valor efetivo em reais que será investido por mês em cada um dos 1.000 cenários simulados.
  * **Definição 2**: Vetor de fluxos mensais ajustados estocasticamente ($PMT_i$) para cada trajetória da simulação.

* **`retorno_anual_simulado = np.maximum(0.01, retorno_base + choque_mercado)`**:
  * **Definição 1**: Calcula o rendimento anual efetivo de cada cenário somando ou descontando as oscilações do mercado, garantindo um retorno mínimo de 1% ao ano.
  * **Definição 2**: Vetor de taxas anuais efetivas limitadas inferiormente a $1\%$ a.a. para evitar distorções de capitalização negativa extrema no horizonte de longo prazo.

* **`r_mensal = (1.0 + retorno_anual_simulado) ** (1.0 / 12.0) - 1.0`**:
  * **Definição 1**: Converte a taxa de rendimento anual em taxa mensal equivalente para aplicar os juros compostos mês a mês.
  * **Definição 2**: Transforma a taxa efetiva anual $i_a$ na taxa equivalente mensal $i_m = (1 + i_a)^{1/12} - 1$.

* **`fv_patrimonio = perfil.patrimonio_atual * fator_capitalizacao`**:
  * **Definição 1**: Calcula quanto o dinheiro que o usuário já tem guardado hoje vai render sozinho até o dia da aposentadoria.
  * **Definição 2**: Calcula o Valor Futuro ($VF$) do capital inicial sob capitalização composta: $VF_{\text{inicial}} = PV \cdot (1 + i_m)^n$.

* **`fv_aportes = aporte_simulado * ((fator_capitalizacao - 1.0) / r_mensal)`**:
  * **Definição 1**: Calcula o montante acumulado exclusivamente pelos novos aportes mensais feitos ao longo dos meses, somados aos juros compostos gerados por eles.
  * **Definição 2**: Calcula o Valor Futuro de uma série uniforme de pagamentos periódicos (anuidade ordinária): $VF_{\text{aportes}} = PMT \cdot \frac{(1 + i_m)^n - 1}{i_m}$.

* **`patrimonios_finais = fv_patrimonio + fv_aportes`**:
  * **Definição 1**: Soma o rendimento do patrimônio inicial com o total acumulado dos aportes mensais, gerando um array com os 1.000 saldos finais possíveis.
  * **Definição 2**: Vetor resultante da soma elemento a elemento dos valores futuros do estoque inicial e dos fluxos mensais acumulados.

* **`probabilidade_sucesso = float(np.mean(patrimonios_finais >= perfil.meta_patrimonio) * 100.0)`**:
  * **Definição 1**: Verifica em quantos dos 1.000 cenários o saldo final atingiu ou superou a meta do usuário e converte isso em um percentual de chance de sucesso.
  * **Definição 2**: Estima a probabilidade empírica $P(VF \ge \text{Meta})$ calculando a média aritmética de uma variável indicadora booleana sobre o espaço amostral simulado.

* **`p10, p50, p90 = np.percentile(patrimonios_finais, [10, 50, 90])`**:
  * **Definição 1**: Separa os resultados em três marcos: o cenário pessimista (`P10`), o cenário central/mais provável (`P50`) e o cenário otimista (`P90`).
  * **Definição 2**: Extrai os quantis de $10\%$, $50\%$ (mediana) e $90\%$ da distribuição empírica dos patrimônios finais para delimitar o intervalo de confiança da projeção.

* **`gasto_alvo_anual = perfil.gasto_mensal_aposentadoria * 12.0`**:
  * **Definição 1**: Multiplica o gasto mensal desejado na aposentadoria por 12 para obter o custo de vida anual.
  * **Definição 2**: Anualiza o fluxo de consumo alvo na fase de usufruto ($G_{\text{anual}} = G_{\text{mensal}} \times 12$).

* **`cenarios_gastos_anuais = np.linspace(...)`**:
  * **Definição 1**: Cria um array com 5 níveis de gasto anual igualmente espaçados, indo do menor gasto possível (gasto alvo menos a margem) até o maior gasto possível (gasto alvo mais a margem).
  * **Definição 2**: Gera uma partição linear de 5 pontos no intervalo $[G_{\text{anual}}(1 - m), G_{\text{anual}}(1 + m)]$ para análise de sensibilidade do padrão de consumo.

* **`matriz_taxas = (cenarios_gastos_anuais[None, :] / patrimonios_validos[:, None]) * 100.0`**:
  * **Definição 1**: Cruza todos os 1.000 patrimônios simulados com os 5 níveis de gasto (5.000 combinações) para saber qual percentual do patrimônio será consumido por ano em cada situação.
  * **Definição 2**: Utiliza *broadcasting* matricial ($N \times 5$) para computar o produto cartesiano das Taxas Seguras de Retirada ($SWR = \frac{\text{Gasto Anual}}{\text{Patrimônio Final}} \times 100$).

* **`taxa_retirada_media_combinada`, `taxa_retirada_mediana`, `desvio_padrao_taxa`**:
  * **Definição 1**: Resumem as 5.000 taxas de retirada em uma média geral, um valor central (mediana, que ignora cenários extremos) e o desvio padrão (que mede o risco de variação).
  * **Definição 2**: Estatísticas descritivas de tendência central ($\mu$, $Md$) e dispersão ($\sigma$) calculadas sobre a matriz combinatória de taxas de retirada.

* **`"sustentavel": bool(taxa_retirada_media_combinada <= (retorno_base * 100.0))`**:
  * **Definição 1**: Responde `True` (Sim) ou `False` (Não) se o dinheiro vai durar sem acabar, comparando se o percentual retirado por ano é menor ou igual ao rendimento anual esperado da carteira.
  * **Definição 2**: Critério booleano de perpetuidade patrimonial que verifica se a taxa média de retirada anual não excede a taxa esperada de retorno real do portfólio ($\overline{SWR} \le r_{\text{base}}$).

---

### 2. Função `_definir_estrategia_tributaria(...)`

Implementa a regra de escolha entre **PGBL** ou **VGBL** e entre as tabelas **Regressiva** ou **Progressiva** do Imposto de Renda.

* **`tabela_ir = "Regressiva" if perfil.anos_ate_aposentadoria >= 10 else "Progressiva"`**:
  * **Definição 1**: Escolhe a tabela **Regressiva** se o investimento ficar aplicado por 10 anos ou mais (onde o imposto cai até a alíquota mínima de 10%), ou **Progressiva** para prazos menores.
  * **Definição 2**: Seleciona o regime de tributação conforme a curva temporal de alíquotas decrescentes da Lei nº 11.053/2004.

* **`if perfil.declara_ir_completo and renda_anual > TETO_ISENCAO_SIMPLIFICADA_ANUAL:`**:
  * **Definição 1**: Verifica se o usuário faz declaração completa de IR e ganha acima do teto anual para recomendar o **PGBL** (abatendo até 12% da renda bruta); caso contrário, recomenda o **VGBL**.
  * **Definição 2**: Avalia a elegibilidade ao diferimento fiscal do PGBL versus a tributação exclusiva sobre rendimentos do VGBL.
  * **Vale a pena PGBL**: Quando a pessoa tem renda tributável alta (CLT, servidor público, etc.), utiliza o modelo **Completo** por ter outros gastos dedutíveis altos e reinveste a restituição de IR recebida anualmente.
  * **Vale a pena VGBL**: Quando a pessoa declara no modelo **Simplificado**, é isenta, é autônoma/MEI com baixa renda tributável ou deseja investir além do limite de 12% da renda bruta anual.

---

### 3. Função `recomendar_aposentadoria(...)`

* **`def recomendar_aposentadoria(perfil: PerfilInvestidor, n_simulacoes: int = 1000) -> Dict[str, Any]:`**:
  * **Definição 1**: É a função principal ("maestro") do simulador: calcula a renda anual com 13º salário, descobre o perfil de risco, roda a simulação de Monte Carlo, define a estratégia tributária e devolve tudo organizado em um dicionário.
  * **Definição 2**: Fachada (*Facade*) do módulo de simulação que orquestra o cálculo da renda bruta anual ($13 \times \text{renda mensal}$), a parametrização de risco, a execução estocástica e a consolidação do payload de saída.
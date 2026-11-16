## Introdução (`src/domain.py`)

* **Definição 1**: Responsável por armazenar as regras de negócio, as constantes de mercado e o formulário estruturado de entrada do investidor, garantindo que nenhum dado inválido chegue aos cálculos matemáticos ou ao banco de dados.
* **Definição 2**: Armazena os dados do usuário e possui as tipologias do usuário, como se fosse uma ficha e os tipos de conclusões que tiramos da ficha.

---

## Bilioteca
* **dataclasses**: Essa biblioteca permite a criação de objetos, tipo java, mas no python.

---


### 1. Constantes de Mercado e Tributação

* **`PARAMETROS_PERFIL = { ... }`**:
  * **Definição 1**: Funciona como uma tabela de referência ("switch") para saber qual é o retorno esperado e a volatilidade (risco) de acordo com o perfil do usuário (`conservador`, `moderado` ou `arrojado`).
  * **Definição 2**: Dicionário estático de configuração que mapeia cada classe de tolerância ao risco às suas respectivas taxas médias de retorno real anual e desvio padrão esperado.
- **Definição 3**: É onde o usuário vai se encaixar com base nas informações apresentadas na "ficha" (especificamente a margem de variação de gastos que ele aceita na aposentadoria)
    * **Tipos de usuários**:
        * **conservador**: Busca máxima previsibilidade e não aceita grandes cortes ou variações no orçamento futuro. O perfil do investidor cauteloso.
        * **moderado**: Aceita um equilíbrio entre segurança e crescimento, tolerando uma flexibilidade intermediária nos gastos futuros.
        * **arrojado**: Tem alta flexibilidade no padrão de vida futuro, aceitando maiores oscilações no curto prazo em busca de maior rentabilidade 

* **`TETO_ISENCAO_SIMPLIFICADA_ANUAL = 85000.0`**:
  * **Definição 1**: Define o valor mínimo de renda bruta anual a partir do qual o abatimento de 12% no Imposto de Renda via PGBL passa a compensar mais do que o desconto simplificado.
  * **Definição 2**: Limiar fiscal utilizado na árvore de decisão tributária para validar a viabilidade econômica do diferimento de IRPF no modelo de declaração completa.

---

### 2. Entidade `PerfilInvestidor`

* **`@dataclass(frozen=True) class PerfilInvestidor`**:
  * **Definição 1**: É o "formulário" que guarda todos os dados financeiros do usuário de forma protegida (`frozen=True`), impedindo que algum valor seja alterado por engano durante a simulação.
  * **Definição 2**: Entidade de domínio imutável gerada via `dataclasses` que encapsula os atributos financeiros e fiscais do investidor com tipagem estática explícita.

* **Atributos da Classe**:
  * **`renda_bruta_mensal`**: Salário ou renda mensal antes dos descontos (usado para calcular a renda anual com 13º e o limite do PGBL).
  * **`gasto_mensal_aposentadoria`**: Quanto o usuário deseja gastar por mês quando estiver aposentado (Gasto Alvo).
  * **`margem_gasto_percentual`**: Percentual de flexibilidade no orçamento futuro (ex.: `0.15` significa que aceita gastar 15% a mais ou a menos).
  * **`aporte_mensal`**: Valor que o usuário pretende investir todos os meses até se aposentar.
  * **`patrimonio_atual`**: Quanto dinheiro o usuário já tem guardado hoje.
  * **`meta_patrimonio`**: O valor total acumulado que o usuário quer atingir ao final do prazo.
  * **`declara_ir_completo`**: Indica (`True` ou `False`) se o usuário faz a declaração completa do Imposto de Renda.
  * **`anos_ate_aposentadoria`**: Quantos anos faltam até a data planejada para a aposentadoria.

* **`def __post_init__(self) -> None`**:
  * **Definição 1**: É uma trava de segurança automática que roda logo após preencher o formulário, bloqueando valores impossíveis (como anos negativos ou meta igual a zero) antes de iniciar qualquer conta.
  * **Definição 2**: Método de ciclo de vida das `dataclasses` que impõe invariantes de domínio e restrições de integridade, disparando `ValueError` caso algum parâmetro viole as regras financeiras.

* **`@property def tolerancia_risco(self) -> str`**:
  * **Definição 1**: Classifica automaticamente se o usuário é `conservador`, `moderado` ou `arrojado` olhando apenas para o tamanho da margem de variação de gastos que ele aceita na aposentadoria.
  * **Definição 2**: Propriedade computada que infere o perfil de risco do investidor a partir da elasticidade de seu consumo futuro (`<= 0.10` → conservador; `<= 0.20` → moderado; `> 0.20` → arrojado).
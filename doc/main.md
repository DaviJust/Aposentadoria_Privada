## Introdução (`main.py`)

* **Definição 1**:O arquivo `main.py` fica na raiz do projeto e funciona como a porta de entrada para execução rápida via terminal (CLI), unindo a criação do perfil, o cálculo estocástico, a gravação no banco de dados e a exibição do relatório final.
* **Definição 2**: Realiza a simulação, esse arquivo representa um teste prático do sistema.

---

## Bilioteca
- **`from src.domain import PerfilInvestidor`**:
  * **Definição 1**: Importa o molde ("ficha oficial") do investidor para que a API possa empacotar os dados recebidos da internet no formato exato que o simulador exige.
  * **Definição 2**: Importa a classe de domínio (`dataclass`) que define a estrutura tipada da entidade de negócio, desacoplando o contrato externo da API (`SimulacaoRequest`) das regras internas de cálculo.
  * **Definição 3**: Traz o padrão (molde da classe) usado para criar o objeto `perfil` com os dados limpos do usuário.

- **from src.simulator import recomendar_aposentadoria**: Importa o algoritmo que calcula a probabilidade disso.

---

## COMPONENTES

### 1. Importações e Conexão entre Módulos

* **`from src.domain import PerfilInvestidor`**:
  * **Definição 1**: Traz o molde de formulário do investidor para preencher os dados financeiros de teste.
  * **Definição 2**: Importa a entidade de domínio imutável responsável por encapsular e validar os parâmetros de entrada da simulação.
  * **Definição 3**: Importa a classe(objeto) investidor, assim o usuário vai ter a "ficha" para preencher.

* **`from src.simulator import recomendar_aposentadoria`**:
  * **Definição 1**: Traz o "cérebro" do sistema que roda os 1.000 cenários de Monte Carlo e escolhe entre PGBL ou VGBL.
  * **Definição 2**: Importa a função orquestradora do motor financeiro e tributário.

* **`from src.database import init_db, salvar_simulacao`**:
  * **Definição 1**: Traz as ferramentas que preparam as tabelas do banco de dados e salvam o histórico da simulação executada.
  * **Definição 2**: Importa as funções da camada de persistência ORM responsáveis pela inicialização do schema (`init_db`) e gravação transacional (`salvar_simulacao`).

---

### 2. Fluxo de Execução (`executar_demonstracao`)

* **`init_db()`**:
  * **Definição 1**: Garante que o banco de dados e as tabelas (`perfil` e `simulacoes_resultados`) existam antes de tentar gravar qualquer informação.
  * **Definição 2**: Executa o DDL declarativo do SQLAlchemy (`Base.metadata.create_all`), criando a estrutura relacional caso ainda não esteja provisionada.

* **`usuario = PerfilInvestidor(...)`**:
  * **Definição 1**: Cria um investidor de exemplo com renda de R$ 3.000, aporte de R$ 1.400, meta de R$ 500.000 em 20 anos e margem de gasto de ±15% (o que o classifica automaticamente como perfil `moderado`).
  * **Definição 2**: Instancia o objeto de domínio validado que servirá de entrada determinística para o motor de simulação.

* **`resultado = recomendar_aposentadoria(usuario)`**:
  * **Definição 1**: Dispara todo o processamento matemático e fiscal, guardando o dicionário completo de respostas na variável `resultado`.
  * **Definição 2**: Invoca a fachada do simulador para obter as métricas probabilísticas, percentis patrimoniais e a recomendação tributária.

* **`id_simulacao = salvar_simulacao(usuario, resultado)`**:
  * **Definição 1**: Grava os dados do usuário e o resultado calculado no banco de dados, devolvendo o número identificador (`id_simulacao`) do registro salvo.
  * **Definição 2**: Persiste de forma atômica o perfil e os indicadores resultantes nas tabelas relacionais e retorna a chave primária gerada.

* **`sim = resultado["simulacao"]`**:
  * **Definição 1**: Cria um atalho para acessar diretamente os números estatísticos da simulação (probabilidade de sucesso, percentis, taxas de retirada) sem precisar digitar `resultado["simulacao"]` várias vezes.
  * **Definição 2**: Extrai o sub-dicionário de métricas estocásticas para facilitar a formatação da saída no console.

* **Bloco `print(...)`**:
  * **Definição 1**: Formata e exibe no terminal o relatório legível com o ID salvo no banco, o perfil de risco identificado, o plano tributário sugerido, a chance de atingir a meta e o diagnóstico de sustentabilidade.
  * **Definição 2**: Camada de apresentação CLI que serializa os indicadores numéricos e booleanos em texto formatado para inspeção humana.

* **`if __name__ == "__main__":`**:
  * **Definição 1**: Garante que a simulação de exemplo só rode automaticamente quando você executar `python main.py` diretamente, e não quando outro arquivo importar funções dele.
  * **Definição 2**: Idioma padrão do Python que verifica o escopo de execução do módulo principal antes de disparar o ponto de entrada da aplicação.
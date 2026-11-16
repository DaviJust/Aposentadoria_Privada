## Introdução
Esse é o arquivo que serveas rotas para o front-end acessar as funções principai e o banco de dados. Ele é quem faz a entrega e o recebimento.

---

## Biblioteca

* **`from contextlib import asynccontextmanager`**:
  * **Definição 1**: Ferramenta nativa do Python usada para criar o bloco de "abertura e fechamento" da API (`lifespan`), garantindo que o banco de dados seja preparado antes do servidor começar a atender requisições.
  * **Definição 2**: Decorador da biblioteca padrão `contextlib` que transforma uma função geradora assíncrona em um gerenciador de contexto compatível com `async with`, utilizado pelo FastAPI para gerenciar eventos de *startup* e *shutdown* da aplicação.
  *  **Definição 3**: Permite uma conexão limpa e bem realizada com o banco de dados.

* **`from fastapi import FastAPI`**:
    * **Definição 1**: Vai realizar as requisições, esse é o motor de fato das API's
    * **Definição 2**: Classe central do framework ASGI FastAPI responsável pelo roteamento HTTP, injeção de dependências, serialização automática em JSON e geração do schema OpenAPI.

* **`from fastapi.middleware.cors import CORSMiddleware`**:
  * **Definição 1**: middleware é o agente que atua entre o recebimento e a entrega, ou seja, esse é o módulo responsável pela intermediação das inform que vem do front-end e vão para o banco de dadosações
  * **Definição 2**: Middleware ASGI que implementa o protocolo *Cross-Origin Resource Sharing* (CORS), adicionando os cabeçalhos HTTP necessários para autorizar requisições vindas de outras origens/domínios.

* **`from pydantic import BaseModel, Field`**:
  * **Definição 1**: Serve para validar o modelo do formulário.

* **`from src.database import SessionLocal, SimulacaoResultadoModel, init_db, salvar_simulacao`**:
  * **Definição 1**: Traz a parte que permite acessar as sessões referentes as trocas de dados.

* **`from src.domain import PerfilInvestidor`**:
  * **Definição 1**: Importa a "ficha oficial" do investidor para que a API possa empacotar os dados recebidos da internet no formato exato que o simulador exige.
  * **Definição 2**: Importação da entidade central de domínio (`dataclass`) que desacopla o contrato externo da API (`SimulacaoRequest`) das regras de negócio internas.


---


## 0. Configuraçao do servidor

- **`@asynccontextmanager async def lifespan(app: FastAPI):`**:
  * **Definição 1**: É a rotina de "abertura e fechamento" da API: garante que, assim que o servidor ligar (`init_db()`), as tabelas do banco de dados sejam criadas automaticamente antes de aceitar qualquer pedido dos usuários, mantendo a aplicação rodando no `yield`. A forma como abre, recebe e envia é assíncrona (`async`), ou seja, não trava o sistema esperando uma tarefa terminar para poder realizar outras operações.
  * **Definição 2**: Gerenciador de contexto assíncrono (*Lifespan Event Handler*) do FastAPI que executa a inicialização do schema do banco de dados na fase de *startup* da aplicação ASGI antes de liberar o fluxo de requisições no `yield`.

- **`app = FastAPI(...)`**:
  * **Definição 1**: Cria o motor principal da API, definindo o nome, a descrição e a versão do sistema, além de montar automaticamente a página interativa de testes no endereço `/docs`.
  * **Definição 2**: Quando criamos uma API precisamos de fato colocá-la de pé; aqui instanciamos a classe `FastAPI` e passamos parâmetros opcionais de configuração (`title`, `description`, `version` e `lifespan`) para personalizar o comportamento e a documentação dela[cite: 3].

- **`app.add_middleware(CORSMiddleware, ...)`**:
  * **Definição 1**: É o "porteiro de segurança" da API: libera que o front-end em React (rodando na porta `5173`) consiga enviar e receber dados do back-end em Python sem ser bloqueado pelo navegador.
  * **Definição 2**: Registra o middleware de *Cross-Origin Resource Sharing* (`CORSMiddleware`) na pilha HTTP, configurando os cabeçalhos de controle de acesso para origens autorizadas (`allow_origins`), credenciais (`allow_credentials`), métodos HTTP (`allow_methods`) e cabeçalhos (`allow_headers`).

- **app.add_middleware(**: O middleware é o agente que intermedia entre a entrega e o recebimento, aqui estamos adicionando regras para esse processo "logístico".
    * **CORSMiddleware,**: É basicamente regra pertinente ao conjunto relacionado a porta do computador.
    * **allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],**: A origem dos requests podem vir somente desses dois endereços.
    * **allow_credentials=True,**: É necessário estar credenciado.
    * **allow_methods=["*"],**: Permite todos os métodos.
    * **allow_headers=["*"],**: Libera o envio de qualquer cabeçalho HTTP na requisição (como o `Content-Type` avisando que os dados estão em formato JSON). Um header é composto por um nome, um signal de : e um valor. Então ao aceitar qualquer tipo de valor, coisas como "Content-Language: pt-br" são permitidas.
)

- **class SimulacaoRequest(BaseModel):**É necessário ter a forma como armazenar a classe para validação dos dados.

- **@app.post("/simular")**:No endereço "nome_site.com.br/simular" será realizado o request.

**def executar_simulacao(dados: SimulacaoRequest):**
  * **Definição 1**: É o ponto central de coordenação da arquitetura: recebe os dados do usuário pela API (`dados`), monta a ficha base no `domain` (`PerfilInvestidor`), envia para o `simulator` realizar o cálculo de Monte Carlo, repassa o resultado para o `database` armazenar no banco e devolve o diagnóstico completo em JSON para o front-end.
  * **Definição 2**: Endpoint RESTful (`POST /simular`) que atua como orquestrador da camada de aplicação, convertendo o DTO validado (`SimulacaoRequest`) em entidade de domínio (`PerfilInvestidor`), invocando o motor de cálculo (`recomendar_aposentadoria`), persistindo via `salvar_simulacao` e retornando o payload consolidado com o `id_simulacao` gerado.

- **resultado = recomendar_aposentadoria(perfil)**: O resultado é calculado
**id_simulacao = salvar_simulacao(perfil, resultado)**: A simulação é salva
- **`return {"id_simulacao": id_simulacao, **resultado}`**:
  * **Definição 1**: Junta o ID recém-criado no banco de dados (`id_simulacao`) com todas as informações calculadas dentro de `resultado` em um único pacote plano, usando o `**` para "desempacotar" os dados de `resultado` direto na resposta final para o front-end.

- **@app.get("/historico")**:No endereço "nome_site.com.br/historico" será realizado o request.
- **def listar_historico(limite: int = 10):**: Como próprio nome diz, vai mostrar as últimas 10 fichas cadastradas
    * **with SessionLocal() as db:** Cria a conexão temporário para realizar troca de dados.
- **registros = (...)**:
  * **Definição 1**: Consulta a tabela de resultados (`SimulacaoResultadoModel`) no banco de dados, ordena do ID mais recente para o mais antigo (ordem decrescente) e traz todas as últimas simulações encontradas até o limite definido (por padrão, os 10 registros mais recentes, sem pular nenhum).
  * **Definição 2**: Executa uma consulta ORM via `db.query(SimulacaoResultadoModel)` aplicando ordenação descendente pela chave primária (`.order_by(SimulacaoResultadoModel.id_simulacao.desc())`), fatiamento de quantidade (`.limit(limite)`) e materialização dos resultados em uma lista de instâncias Python (`.all()`).
# Documentação Técnica: Simulador de Aposentadoria Privada

Definição: Esse é um simulador de aposentadoria privada do quais tem dois produtos o VGBL e PGBL, o objetivo é usar matemática para saber quais as chances do usuário se aposentar.


!!! note "Atenção"
    O sistema foi modularizado para separar as regras de negócio, o motor matemático probabilístico e a execução principal, facilitando a manutenção, a realização de testes e a futura exposição via API (FastAPI) e interface web (React).

---

## 🔄 Fluxograma do Recomendador de Aposentadoria

O fluxograma a seguir ilustra a jornada de execução do sistema: desde a coleta dos dados do usuário até o cálculo de simulação estocástica e a definição do melhor produto tributário.

```mermaid
flowchart TD
    subgraph E1[1. Parâmetros de Entrada - src/domain.py]
        A[Dados Financeiros e Metas] --> B[Perfil de Risco e Tempo]
        C[Gasto Desejado e Margem Flexível] --> D[Tipo de Declaração de IR]
    end

    subgraph E2[2. Simulação Monte Carlo - src/simulator.py]
        B --> E[Amostragem Estocástica de Renda e Mercado]
        E --> F[Geração de 1.000 Cenários de Patrimônio]
        F --> G[Probabilidade de Atingir a Meta e Percentis]
    end

    subgraph E3[3. Matriz Combinatória de Custo de Vida - src/simulator.py]
        C --> H[Variação do Gasto na Aposentadoria]
        F & H --> I[Matriz N x M de Taxas de Retirada]
        I --> J[Taxa Média Combinada & Desvio Padrão]
    end

    subgraph E4[4. Decisão Tributária - src/simulator.py]
        D --> K{Declaração Completa?}
        K -- Sim --> L[PGBL - Abate de até 12%]
        K -- Não --> M[VGBL - Incidência sobre Lucros]
        
        B --> N{Prazo >= 10 anos?}
        N -- Sim --> O[Tabela Regressiva]
        N -- Não --> P[Tabela Progressiva]
    end

    subgraph E5[5. Saída - main.py / API]
        G & J & L & M & O & P --> Q[Relatório Final de Aposentadoria e Sustentabilidade]
    end
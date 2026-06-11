<div align="center">

# 🔍 Comparador de Algoritmos em Grafos

**Aplicação desktop para benchmarking empírico e visualização interativa de BFS, DFS e Dijkstra aplicados a uma rede geográfica de municípios do interior baiano.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![UI](https://img.shields.io/badge/UI-CustomTkinter-1E3A5F?style=flat-square&logo=tkinter&logoColor=white)](https://github.com/TomSchimansky/CustomTkinter)
[![Graph](https://img.shields.io/badge/Graph-NetworkX-FF6B35?style=flat-square)](https://networkx.org)
[![Viz](https://img.shields.io/badge/Viz-Matplotlib-11557C?style=flat-square&logo=python&logoColor=white)](https://matplotlib.org)
[![License](https://img.shields.io/badge/License-MIT-2ECC71?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey?style=flat-square)]()

[Funcionalidades](#-funcionalidades) · [Instalação](#-instalação) · [Uso](#-uso) · [Arquitetura](#-arquitetura-do-projeto) · [Resultados](#-resultados-de-referência) · [Referências](#-referências-acadêmicas)

</div>

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Funcionalidades](#-funcionalidades)
- [Algoritmos Implementados](#-algoritmos-implementados)
- [O Grafo](#-o-grafo)
- [Arquitetura do Projeto](#-arquitetura-do-projeto)
- [Instalação](#-instalação)
- [Uso](#-uso)
- [Métricas Coletadas](#-métricas-coletadas)
- [Resultados de Referência](#-resultados-de-referência)
- [Formato dos Exports](#-formato-dos-exports)
- [Dependências](#-dependências)
- [Referências Acadêmicas](#-referências-acadêmicas)
- [Licença](#-licença)

---

## 🎯 Visão Geral

O **Comparador de Algoritmos em Grafos** é uma aplicação desktop desenvolvida em Python 3.10+ que permite a **comparação empírica e visual** de três algoritmos clássicos de busca em grafos:

| Algoritmo | Classe | Complexidade Temporal | Garante Custo Mínimo |
|-----------|--------|-----------------------|----------------------|
| **BFS** — Breadth-First Search | Busca em largura | `O(V + E)` | Não¹ |
| **DFS** — Depth-First Search | Busca em profundidade | `O(V + E)` | Não |
| **Dijkstra** | Caminho mínimo | `O((V+E) log V)` | ✅ Sim |

> ¹ Em grafos não ponderados, BFS garante o menor número de arestas — não o menor custo.

A aplicação executa cada algoritmo **100 vezes** por par de vértices, coleta métricas estatísticas de desempenho temporal e apresenta os resultados em uma interface dark-themed com tabela comparativa dominante, painel de insights e visualização interativa do grafo com tooltip ao hover.

---

## ✨ Funcionalidades

- **Benchmark estatisticamente robusto** — 100 execuções por algoritmo com coleta de média, mediana, mínimo, máximo e desvio padrão (σ)
- **Tabela comparativa central** — ranking visual com medalhas 🥇🥈🥉, destaque ao vencedor e caminho exibido por extenso (`Amélia Rodrigues (A) → Feira (F) → Jaçanã (J)`)
- **Visualização interativa do grafo** — renderização georreferenciada via NetworkX + Matplotlib; caminho encontrado destacado em azul; tooltip com nome completo da cidade ao passar o mouse
- **Painel de insights** — 4 cards: vencedor em tempo, garantia de custo ótimo (Dijkstra), caminho detalhado nó a nó, e complexidade assintótica comparada
- **Estatísticas detalhadas** — mini-cards por algoritmo com 5 métricas alinhadas à direita
- **Histórico compacto** — últimas 5 execuções com rota, algoritmo vencedor, custo e horário
- **Exportação de resultados** — JSON (metadados completos) e CSV (dados tabulares) prontos para análise
- **Interface dark-themed** — paleta GitHub-dark, foco em legibilidade técnica e precisão acadêmica

---

## 🧮 Algoritmos Implementados

### Busca em Largura — BFS

Explora o grafo em camadas a partir da origem, visitando todos os vértices a distância `k` antes de avançar para distância `k+1`. Usa fila FIFO. Garante o **menor número de arestas** em grafos não ponderados; sem garantia de custo mínimo em ponderados.

```
Complexidade Temporal : O(V + E)
Complexidade Espacial : O(V)
Ótimo em grafos ponderados: Não
Estrutura auxiliar     : Fila (FIFO)
```

### Busca em Profundidade — DFS

Explora o grafo ao máximo em cada ramo antes de recuar (*backtracking*). Usa pilha (recursão ou explícita). Não oferece garantia de otimalidade, mas é eficiente para exploração completa e detecção de ciclos.

```
Complexidade Temporal : O(V + E)
Complexidade Espacial : O(V)
Ótimo em grafos ponderados: Não
Estrutura auxiliar     : Pilha (LIFO / recursão)
```

### Dijkstra

Resolve o **problema do caminho de custo mínimo** de fonte única em grafos ponderados com pesos não-negativos. Seleciona iterativamente o vértice de menor distância provisória via *min-heap*. Único dos três com garantia formal de solução ótima.

```
Complexidade Temporal : O((V + E) log V)
Complexidade Espacial : O(V)
Ótimo em grafos ponderados: ✅ Sim
Estrutura auxiliar     : Fila de prioridade (min-heap)
```

---

## 🗺️ O Grafo

O grafo modela uma rede de municípios do **interior da Bahia** com arestas ponderadas representando distâncias rodoviárias aproximadas em quilômetros. Inclui cidades como:

- **Feira de Santana (F)** — polo central da rede
- **Amélia Rodrigues (A)**, **Santo Amaro (SA)**, **Jaçanã (J)**
- e demais municípios adjacentes

As **coordenadas geográficas reais** dos municípios são usadas para posicionamento dos nós, tornando a visualização geograficamente fiel. O grafo é implementado como dicionário de adjacências Python e convertido para `nx.Graph` (NetworkX) para renderização.

---

## 🏗️ Arquitetura do Projeto

```
graph-algorithm-comparator/
│
├── core/                         # Lógica de negócio — sem dependência de UI
│   ├── graph.py                  # Definição do grafo, posições geográficas,
│   │                             #   NODE_LABELS e funções de formatação de caminho
│   ├── algorithms.py             # Implementações de BFS, DFS e Dijkstra;
│   │                             #   COMPLEXITIES e ALGORITHM_NOTES para UI
│   ├── benchmark.py              # Orquestrador: run_experiment() executa N rodadas
│   │                             #   e retorna ExperimentResult com estatísticas
│   ├── models.py                 # Data classes: AlgorithmResult, BenchmarkData,
│   │                             #   ExperimentResult (imutáveis, tipadas)
│   └── validators.py             # Validação estrutural do grafo em modo fail-fast
│
├── ui/                           # Camada de apresentação — customtkinter
│   ├── app.py                    # Janela principal: layout em grid 3×3,
│   │                             #   handlers, atualização de todos os componentes
│   ├── graph_view.py             # Componente Matplotlib/NetworkX com tooltip
│   │                             #   interativo e legenda simplificada
│   ├── components.py             # Fábrica de widgets reutilizáveis:
│   │                             #   card(), mono_label(), insight_card(), etc.
│   └── styles.py                 # Paleta de cores, tipografia e estilos TTK;
│                                 #   configure_ttk_styles() para o Treeview
│
├── exports/                      # Resultados exportados (gerado em runtime)
│   ├── benchmark_A_J_*.json      # Metadados completos
│   └── benchmark_A_J_*.csv       # Dados tabulares
│
├── main.py                       # Ponto de entrada: configura backend Matplotlib,
│                                 #   valida grafo e inicializa CTk
└── requirements.txt              # Dependências pinadas
```

### Fluxo de dados

```
Usuário seleciona (origem, destino)
        │
        ▼
run_experiment() ──► executa BFS / DFS / Dijkstra × N vezes
        │                       │
        │               perf_counter() antes/depois
        │
        ▼
ExperimentResult  (sorted_by_speed, fastest, results{})
        │
        ├──► _update_table()      → Treeview com caminho por extenso
        ├──► _update_stats()      → mini-cards com 5 métricas por algoritmo
        ├──► _update_insights()   → 4 cards: tempo / custo / caminho / complexidade
        ├──► _update_analysis()   → 3 bullets acadêmicos
        ├──► _update_history()    → últimas 5 execuções
        └──► GraphView.render()   → grafo redesenhado com caminho destacado
```

---

## 🚀 Instalação

### Pré-requisitos

- Python **3.10** ou superior
- `pip`

### Passo a passo

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/graph-algorithm-comparator.git
cd graph-algorithm-comparator

# 2. Crie um ambiente virtual (recomendado)
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute a aplicação
python main.py
```

> **Windows:** certifique-se de ter o Tcl/Tk instalado junto com o Python (opção padrão no instalador oficial).

---

## 🖥️ Uso

**Interface principal:**

1. Selecione a **Origem** e o **Destino** nos menus dropdown do painel esquerdo
2. Clique em **▶ Executar Benchmark**
3. Aguarde a conclusão das 100 execuções por algoritmo (barra de progresso indeterminada)
4. Analise os resultados na **tabela comparativa** (painel central — elemento dominante)
5. Explore os **insights** no painel direito e a **visualização do grafo** na parte inferior
6. Exporte em JSON/CSV com **↓ Exportar Resultado**

**Interações com o grafo:**

| Ação | Resultado |
|------|-----------|
| Hover sobre um nó | Tooltip com nome completo da cidade |
| Após benchmark | Caminho destacado em azul com distâncias por aresta |
| Origem | Nó verde (maior) |
| Destino | Nó vermelho (maior) |

---

## 📊 Métricas Coletadas

Para cada algoritmo, a partir de `N = 100` execuções usando `time.perf_counter()`:

| Métrica | Descrição | Uso |
|---------|-----------|-----|
| **Tempo Médio** | Estimador de tendência central | Ranking principal |
| **Mediana** | Estimador robusto a outliers | Validação da média |
| **Mínimo** | Melhor execução observada | Limite inferior |
| **Máximo** | Pior execução observada | Detecção de spikes |
| **Desvio Padrão (σ)** | Variabilidade e consistência | Confiabilidade |

> `time.perf_counter()` oferece resolução de **nanosegundos** e é recomendado pela documentação oficial do Python para benchmarking de curta duração.

---

## 📈 Resultados de Referência

**Experimento:** Amélia Rodrigues → Jaçanã (via Feira de Santana) · N = 100 execuções

| Rank | Algoritmo | Caminho | Custo | Tempo Médio | σ | Ótimo Garantido |
|------|-----------|---------|-------|-------------|---|-----------------|
| 🥇 | **BFS** | A → F → J | 53 km | **0,0059 ms** | ±0,0003 | Não |
| 🥈 | DFS | A → F → J | 53 km | 0,0071 ms | ±0,0002 | Não |
| 🥉 | Dijkstra | A → F → J | 53 km | 0,0160 ms | ±0,0004 | **Sim ✓** |

**Estatísticas detalhadas:**

| Algoritmo | Média | Mediana | Mínimo | Máximo | σ |
|-----------|-------|---------|--------|--------|---|
| BFS | 0,0059 ms | 0,0058 ms | 0,0057 ms | 0,0090 ms | 0,0003 ms |
| DFS | 0,0071 ms | 0,0070 ms | 0,0068 ms | 0,0095 ms | 0,0002 ms |
| Dijkstra | 0,0160 ms | 0,0158 ms | 0,0155 ms | 0,0190 ms | 0,0004 ms |

> Resultados variam conforme hardware e par de vértices. Os valores acima foram obtidos em Intel Core i5-12ª geração, 16 GB RAM, Windows 11.

---

## 📤 Formato dos Exports

```
exports/
├── benchmark_A_J_20260610_133301.json
└── benchmark_A_J_20260610_133301.csv
```

**JSON — estrutura completa:**

```json
{
  "timestamp": "2026-06-10T13:33:01",
  "config": {
    "start": "A",
    "start_name": "Amélia Rodrigues",
    "end": "J",
    "end_name": "Jaçanã",
    "executions": 100
  },
  "results": {
    "BFS": {
      "path": ["A", "F", "J"],
      "path_full": "Amélia Rodrigues (A) → Feira de Santana (F) → Jaçanã (J)",
      "cost_km": 53,
      "optimal_guaranteed": "Não",
      "mean_ms": 0.005912,
      "std_ms": 0.000287,
      "median_ms": 0.005834,
      "min_ms": 0.005701,
      "max_ms": 0.009031
    },
    "DFS": { "..." : "..." },
    "Dijkstra": { "..." : "..." }
  }
}
```

**CSV — colunas:**

```
algorithm, path_short, path_full, cost_km, optimal_guaranteed,
mean_ms, std_ms, median_ms, min_ms, max_ms
```

---

## 📦 Dependências

```
customtkinter>=5.2.0    # Interface gráfica dark-themed sobre tkinter
networkx>=3.0           # Representação e execução de algoritmos em grafos
matplotlib>=3.7.0       # Visualização do grafo com FigureCanvasTkAgg
```

Instalar todas:

```bash
pip install -r requirements.txt
```

---

## 📚 Referências Acadêmicas

1. CORMEN, T. H.; LEISERSON, C. E.; RIVEST, R. L.; STEIN, C. **Introduction to Algorithms**. 3. ed. Cambridge: MIT Press, 2009.
2. DIJKSTRA, E. W. A note on two problems in connexion with graphs. **Numerische Mathematik**, v. 1, n. 1, p. 269–271, 1959.
3. SEDGEWICK, R.; WAYNE, K. **Algorithms**. 4. ed. Upper Saddle River: Addison-Wesley, 2011.
4. SKIENA, S. S. **The Algorithm Design Manual**. 3. ed. New York: Springer, 2020.
5. NETWORKX DEVELOPERS. **NetworkX — Network Analysis in Python**. Disponível em: <https://networkx.org>.
6. PYTHON SOFTWARE FOUNDATION. **time — Time access and conversions**. Disponível em: <https://docs.python.org/3/library/time.html>.

---

## 📄 Licença

Distribuído sob a licença **MIT**. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.

---

<div align="center">

Desenvolvido como projeto acadêmico — Análise e Comparação de Algoritmos em Grafos Geográficos


</div>

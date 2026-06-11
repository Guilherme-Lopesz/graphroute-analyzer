"""
core/models.py
==============
Modelos de dados tipados para resultados de busca, benchmark e experimentos.
Todos os modelos usam ``@dataclass(slots=True)`` para eficiência de memória.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

# ─── Tipo alias ───────────────────────────────────────────────────────────────
Path = list[str]


@dataclass(slots=True)
class SearchResult:
    """
    Resultado de um algoritmo de busca.

    Attributes:
        path: Sequência de vértices do caminho encontrado, ou None se
              não houver caminho.
        cost: Custo total do caminho (soma dos pesos das arestas), ou
              ``float('inf')`` se não houver caminho.
    """
    path: Optional[Path]
    cost: int | float


@dataclass(slots=True)
class BenchmarkResult:
    """
    Estatísticas de desempenho de um único algoritmo após N execuções.

    Attributes:
        mean_ms:   Tempo médio em milissegundos.
        std_ms:    Desvio padrão amostral em milissegundos.
        median_ms: Mediana dos tempos em milissegundos.
        min_ms:    Menor tempo observado em milissegundos.
        max_ms:    Maior tempo observado em milissegundos.
        result:    Resultado da última execução do algoritmo.
    """
    mean_ms:   float
    std_ms:    float
    median_ms: float
    min_ms:    float
    max_ms:    float
    result:    SearchResult


@dataclass
class ExperimentResult:
    """
    Resultado completo de um experimento de comparação entre algoritmos.

    Encapsula todas as estatísticas de benchmark e metadados de configuração.
    Provê propriedades derivadas para análise e exibição.

    Attributes:
        start:        Vértice de origem do experimento.
        end:          Vértice de destino do experimento.
        n_executions: Número de execuções por algoritmo.
        timestamp:    Momento em que o experimento foi concluído.
        results:      Mapeamento de nome do algoritmo para BenchmarkResult.
    """
    start:        str
    end:          str
    n_executions: int
    timestamp:    datetime
    results:      dict[str, BenchmarkResult]

    @property
    def fastest(self) -> tuple[str, BenchmarkResult]:
        """Retorna (nome, dados) do algoritmo com menor tempo médio."""
        return min(self.results.items(), key=lambda x: x[1].mean_ms)

    @property
    def optimal_cost(self) -> tuple[str, BenchmarkResult]:
        """Retorna (nome, dados) do algoritmo com menor custo de caminho."""
        return min(self.results.items(), key=lambda x: x[1].result.cost)

    @property
    def sorted_by_speed(self) -> list[tuple[str, BenchmarkResult]]:
        """Retorna pares (nome, dados) ordenados do mais rápido ao mais lento."""
        return sorted(self.results.items(), key=lambda x: x[1].mean_ms)

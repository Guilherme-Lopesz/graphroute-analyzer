"""
core/benchmark.py
=================
Motor de benchmark isolado completamente da interface de usuário.

Mede exclusivamente a lógica pura dos algoritmos: warm-up, coleta de
amostras em nanosegundos via ``perf_counter_ns()`` e estatísticas completas
(média, desvio padrão amostral, mediana, mín, máx).
"""
from __future__ import annotations

import statistics
import time
from datetime import datetime

from core.algorithms import ALGORITHMS, SearchAlgorithm
from core.graph import GRAPH
from core.models import BenchmarkResult, ExperimentResult, SearchResult
from core.validators import validate_endpoints, validate_graph, validate_n


# ─── Benchmark individual ─────────────────────────────────────────────────────

def benchmark(
    func:  SearchAlgorithm,
    graph: dict[str, dict[str, int]],
    start: str,
    end:   str,
    n:     int = 100,
) -> BenchmarkResult:
    """
    Executa ``func`` por ``n`` iterações e retorna estatísticas completas.

    Uma execução de aquecimento é descartada antes das medições para
    eliminar variações de cache frio e compilação JIT do interpretador.
    Tempo medido em nanosegundos via ``perf_counter_ns()`` e convertido
    para milissegundos na saída.

    A interface nunca é chamada aqui: este módulo é puro I/O de dados.

    Args:
        func:  Algoritmo de busca a medir (assinatura SearchAlgorithm).
        graph: Dicionário de adjacência ponderada.
        start: Vértice de origem.
        end:   Vértice de destino.
        n:     Número de execuções efetivas de medição (warm-up não conta).

    Returns:
        BenchmarkResult com média, desvio padrão amostral, mediana,
        mín, máx e o resultado da última execução do algoritmo.
    """
    # Warm-up: descartado — elimina variação de cache e compilação
    func(graph, start, end)

    samples_ns: list[int] = []
    result = SearchResult(path=None, cost=float("inf"))

    for _ in range(n):
        t0     = time.perf_counter_ns()
        result = func(graph, start, end)
        tf     = time.perf_counter_ns()
        samples_ns.append(tf - t0)

    ms: list[float] = [t / 1_000_000 for t in samples_ns]

    return BenchmarkResult(
        mean_ms=statistics.mean(ms),
        std_ms=statistics.stdev(ms),       # desvio padrão amostral (n-1)
        median_ms=statistics.median(ms),
        min_ms=min(ms),
        max_ms=max(ms),
        result=result,
    )


# ─── Experimento completo ─────────────────────────────────────────────────────

def run_experiment(
    start: str,
    end:   str,
    n:     int = 100,
    graph: dict[str, dict[str, int]] | None = None,
) -> ExperimentResult:
    """
    Executa o benchmark completo de todos os algoritmos para o par (start, end).

    Valida entradas antes de executar. Cada algoritmo recebe ``n`` execuções
    independentes com warm-up descartado.

    Args:
        start: Vértice de origem.
        end:   Vértice de destino.
        n:     Número de execuções por algoritmo.
        graph: Grafo a usar; se None, utiliza o grafo padrão ``GRAPH``.

    Returns:
        ExperimentResult com resultados de todos os algoritmos.

    Raises:
        ValueError: Se endpoints forem inválidos ou o grafo for inválido.
    """
    g = graph if graph is not None else GRAPH

    validate_graph(g)
    validate_endpoints(g, start, end)
    validate_n(n)

    results: dict[str, BenchmarkResult] = {
        name: benchmark(func, g, start, end, n=n)
        for name, func in ALGORITHMS.items()
    }

    return ExperimentResult(
        start=start,
        end=end,
        n_executions=n,
        timestamp=datetime.now(),
        results=results,
    )

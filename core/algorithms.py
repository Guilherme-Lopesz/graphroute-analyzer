"""
core/algorithms.py
==================
Implementações de BFS, DFS e Dijkstra com type hints completos,
docstrings profissionais e comportamento estritamente determinístico.

Todos os algoritmos respeitam a assinatura uniforme ``SearchAlgorithm``.
Nenhuma lógica de I/O ou UI neste módulo.
"""
from __future__ import annotations

import heapq
from collections import deque
from collections.abc import Callable
from typing import Optional

from core.graph import SORTED_GRAPH
from core.models import Path, SearchResult

# ─── Tipo canônico para algoritmos de busca ───────────────────────────────────
SearchAlgorithm = Callable[
    [dict[str, dict[str, int]], str, str],
    SearchResult,
]


# ─── Utilitário interno ───────────────────────────────────────────────────────

def _reconstruct_path(
    parent: dict[str, Optional[str]],
    end: str,
) -> Path:
    """
    Reconstrói o caminho percorrendo o mapa de predecessores de trás para frente.

    Args:
        parent: Mapeamento vértice → predecessor (None para a raiz).
        end:    Vértice final do caminho.

    Returns:
        Lista de vértices do início ao fim, em ordem.
    """
    path: Path = []
    node: Optional[str] = end
    while node is not None:
        path.append(node)
        node = parent[node]
    return path[::-1]


# ─── BFS ──────────────────────────────────────────────────────────────────────

def bfs(
    graph: dict[str, dict[str, int]],
    start: str,
    end: str,
) -> SearchResult:
    """
    Busca em Largura (BFS — Breadth-First Search).

    Garante o caminho com o **menor número de arestas** em grafos não ponderados.
    Visitados marcados na **inserção** para evitar duplicatas na fila (FIFO).
    Custo acumulado rastreado incrementalmente via ``parent_cost``.

    Complexity: O(V + E)

    Args:
        graph: Dicionário de adjacência ponderada.
        start: Vértice de origem.
        end:   Vértice de destino.

    Returns:
        SearchResult com caminho e custo, ou path=None se inacessível.
    """
    visited:     set[str]                 = {start}
    parent:      dict[str, Optional[str]] = {start: None}
    parent_cost: dict[str, int]           = {start: 0}
    queue:       deque[str]               = deque([start])

    while queue:
        node = queue.popleft()
        if node == end:
            return SearchResult(
                path=_reconstruct_path(parent, end),
                cost=parent_cost[end],
            )
        for neighbor, weight in graph.get(node, {}).items():
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = node
                parent_cost[neighbor] = parent_cost[node] + weight
                queue.append(neighbor)

    return SearchResult(path=None, cost=float("inf"))


# ─── DFS ──────────────────────────────────────────────────────────────────────

def dfs(
    graph: dict[str, dict[str, int]],
    start: str,
    end: str,
) -> SearchResult:
    """
    Busca em Profundidade (DFS — Depth-First Search).

    Vizinhos pré-ordenados em ``SORTED_GRAPH`` eliminam o custo de
    ``sorted()`` a cada expansão. A inserção em pilha na **ordem reversa**
    garante que o menor vizinho lexicográfico seja expandido primeiro (LIFO).
    Custo acumulado rastreado incrementalmente via ``parent_cost``.

    Complexity: O(V + E)

    Args:
        graph: Dicionário de adjacência ponderada.
        start: Vértice de origem.
        end:   Vértice de destino.

    Returns:
        SearchResult com caminho e custo, ou path=None se inacessível.
    """
    visited:     set[str]                 = {start}
    parent:      dict[str, Optional[str]] = {start: None}
    parent_cost: dict[str, int]           = {start: 0}
    stack:       list[str]                = [start]

    while stack:
        node = stack.pop()
        if node == end:
            return SearchResult(
                path=_reconstruct_path(parent, end),
                cost=parent_cost[end],
            )
        for neighbor in reversed(SORTED_GRAPH.get(node, ())):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = node
                parent_cost[neighbor] = parent_cost[node] + graph[node][neighbor]
                stack.append(neighbor)

    return SearchResult(path=None, cost=float("inf"))


# ─── Dijkstra ─────────────────────────────────────────────────────────────────

def dijkstra(
    graph: dict[str, dict[str, int]],
    start: str,
    end: str,
) -> SearchResult:
    """
    Algoritmo de Dijkstra com heap de prioridade mínima.

    Garante o caminho de **menor custo total** em grafos com pesos não
    negativos. A tabela de distâncias mínimas garante que apenas caminhos
    estritamente melhores sejam inseridos na heap, evitando processamento
    redundante de estados dominados.

    Complexity: O((V + E) log V)

    Args:
        graph: Dicionário de adjacência ponderada.
        start: Vértice de origem.
        end:   Vértice de destino.

    Returns:
        SearchResult com caminho ótimo e custo mínimo garantido,
        ou path=None se inacessível.
    """
    distances: dict[str, float]          = {start: 0}
    parent:    dict[str, Optional[str]]  = {start: None}
    heap:      list[tuple[int, str]]     = [(0, start)]
    visited:   set[str]                  = set()

    while heap:
        cost, node = heapq.heappop(heap)
        if node in visited:
            continue
        visited.add(node)
        if node == end:
            return SearchResult(
                path=_reconstruct_path(parent, end),
                cost=cost,
            )
        for neighbor, weight in graph.get(node, {}).items():
            new_cost = cost + weight
            if new_cost < distances.get(neighbor, float("inf")):
                distances[neighbor] = new_cost
                parent[neighbor] = node
                heapq.heappush(heap, (new_cost, neighbor))

    return SearchResult(path=None, cost=float("inf"))


# ─── Registros centralizados ──────────────────────────────────────────────────

ALGORITHMS: dict[str, SearchAlgorithm] = {
    "BFS":      bfs,
    "DFS":      dfs,
    "Dijkstra": dijkstra,
}

COMPLEXITIES: dict[str, str] = {
    "BFS":      "O(V + E)",
    "DFS":      "O(V + E)",
    "Dijkstra": "O((V+E) log V)",
}

ALGORITHM_NOTES: dict[str, str] = {
    "BFS":      "Menor nº de arestas",
    "DFS":      "Primeira via profunda",
    "Dijkstra": "Custo mínimo garantido",
}

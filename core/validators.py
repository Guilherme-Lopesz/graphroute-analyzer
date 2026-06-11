"""
core/validators.py
==================
Funções de validação de entradas para algoritmos, benchmark e estrutura
do grafo. Isoladas da interface e dos algoritmos para facilitar testes.
"""
from __future__ import annotations


def validate_graph(graph: dict[str, dict[str, int]]) -> None:
    """
    Verifica a integridade estrutural completa do grafo.

    Valida:
    - Grafo não vazio.
    - Ausência de pesos negativos (requisito do Dijkstra).
    - Simetria bidirecional de todas as arestas.

    Args:
        graph: Dicionário de adjacência ponderada a validar.

    Raises:
        ValueError: Em qualquer violação estrutural detectada.
    """
    if not graph:
        raise ValueError("O grafo está vazio.")

    for node, neighbors in graph.items():
        for neighbor, weight in neighbors.items():
            if weight < 0:
                raise ValueError(
                    f"Peso negativo detectado: aresta {node}→{neighbor} = {weight}. "
                    "Dijkstra requer pesos não negativos."
                )
            reverse = graph.get(neighbor, {}).get(node)
            if reverse is None:
                raise ValueError(
                    f"Grafo assimétrico: aresta {node}→{neighbor} existe, "
                    f"mas {neighbor}→{node} está ausente."
                )
            if reverse != weight:
                raise ValueError(
                    f"Pesos assimétricos: {node}→{neighbor} = {weight}, "
                    f"mas {neighbor}→{node} = {reverse}."
                )


def validate_endpoints(
    graph: dict[str, dict[str, int]],
    start: str,
    end: str,
) -> None:
    """
    Verifica que origem e destino são vértices distintos e existentes no grafo.

    Args:
        graph: Dicionário de adjacência ponderada.
        start: Código do vértice de origem.
        end:   Código do vértice de destino.

    Raises:
        ValueError: Se origem ou destino forem inválidos, ausentes ou iguais.
    """
    if not start:
        raise ValueError("Selecione um vértice de origem.")
    if not end:
        raise ValueError("Selecione um vértice de destino.")
    if start == end:
        raise ValueError(
            f"Origem e destino devem ser diferentes (ambos são '{start}')."
        )
    if start not in graph:
        raise ValueError(
            f"Vértice de origem '{start}' não encontrado no grafo."
        )
    if end not in graph:
        raise ValueError(
            f"Vértice de destino '{end}' não encontrado no grafo."
        )


def validate_n(n: int) -> None:
    """
    Verifica que o número de execuções de benchmark é positivo.

    Args:
        n: Número de iterações a validar.

    Raises:
        ValueError: Se n <= 0.
    """
    if n <= 0:
        raise ValueError(
            f"O número de execuções deve ser maior que zero; recebido: {n}."
        )

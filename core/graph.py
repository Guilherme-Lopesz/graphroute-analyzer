"""
core/graph.py
=============
Definição do grafo geográfico de Feira de Santana (BA) e localidades
vizinhas, conforme Anexo I da atividade A3.

Inclui vizinhos pré-ordenados para DFS, posições fixas para renderização
do grafo e utilitários de acesso.
"""
from __future__ import annotations

from typing import Final

# ─── Grafo principal ──────────────────────────────────────────────────────────
# Adjacência ponderada bidirecional. Pesos em quilômetros.
GRAPH: Final[dict[str, dict[str, int]]] = {
    "F":   {"H": 12, "M": 15, "T": 18, "J": 22, "B": 25,
            "W": 20, "G": 28, "A": 31, "C": 20, "Cj": 28},
    "H":   {"F": 12, "M": 10, "A": 22},
    "M":   {"F": 15, "H": 10, "T": 9,  "W": 12, "Sg": 20},
    "T":   {"F": 18, "M": 9,  "I": 26},
    "J":   {"F": 22, "S": 18, "TQ": 16},
    "B":   {"F": 25},
    "W":   {"F": 20, "M": 12, "SFe": 22},
    "G":   {"F": 28},
    "A":   {"F": 31, "H": 22},
    "C":   {"F": 20},
    "Cj":  {"F": 28, "AM": 24, "SA": 32},
    "S":   {"J": 18},
    "TQ":  {"J": 16},
    "I":   {"T": 26},
    "Sg":  {"M": 20, "AM": 24},
    "AM":  {"Sg": 24, "Cj": 24},
    "SA":  {"Cj": 32},
    "SFe": {"W": 22},
}

# ─── Vizinhos pré-ordenados ───────────────────────────────────────────────────
# Elimina o custo de sorted() a cada expansão do DFS.
SORTED_GRAPH: Final[dict[str, tuple[str, ...]]] = {
    node: tuple(sorted(neighbors))
    for node, neighbors in GRAPH.items()
}

# ─── Nomes completos ──────────────────────────────────────────────────────────
NODE_LABELS: Final[dict[str, str]] = {
    "F":   "Feira de Santana",
    "H":   "Humildes",
    "M":   "Mairi",
    "T":   "Tanquinho",
    "J":   "Jaçanã",
    "B":   "Bonfim",
    "W":   "Wenceslau Guimarães",
    "G":   "Gavião",
    "A":   "Amélia Rodrigues",
    "C":   "Conceição",
    "Cj":  "Coité do Nóia",
    "S":   "Santanópolis",
    "TQ":  "Tanquinho Q.",
    "I":   "Ipirá",
    "Sg":  "São Gonçalo",
    "AM":  "Antônio Martins",
    "SA":  "Santo Amaro",
    "SFe": "Santa Fé",
}

# ─── Posições fixas para visualização ────────────────────────────────────────
# Coordenadas normalizadas que aproximam a geografia da região.
# F (Feira de Santana) é o hub central; SA (Santo Amaro) é o destino afastado.
FIXED_POS: Final[dict[str, tuple[float, float]]] = {
    "F":   ( 0.00,  0.00),   # Hub central
    "H":   (-0.65,  0.75),
    "M":   (-1.30,  0.30),
    "T":   (-1.45, -0.55),
    "J":   ( 0.85,  0.90),
    "B":   ( 0.55, -1.05),
    "W":   (-2.00,  0.80),
    "G":   (-0.50, -1.20),
    "A":   (-0.30,  1.35),
    "C":   ( 0.35, -1.25),
    "Cj":  ( 1.35, -0.30),
    "S":   ( 1.65,  1.60),
    "TQ":  ( 2.15,  1.05),
    "I":   (-2.30, -0.55),
    "Sg":  (-2.20,  0.35),
    "AM":  ( 0.95, -1.40),
    "SA":  ( 2.20, -0.60),
    "SFe": (-2.70,  0.90),
}


# ─── Utilitários ──────────────────────────────────────────────────────────────

def get_sorted_nodes() -> list[str]:
    """Retorna os nós ordenados pelo nome completo da cidade (para dropdowns)."""
    return sorted(GRAPH.keys(), key=lambda n: NODE_LABELS.get(n, n))


def get_node_label(node: str) -> str:
    """Retorna o nome completo de um nó, ou o código breve caso não encontrado."""
    return NODE_LABELS.get(node, node)


def format_node(node: str) -> str:
    """
    Formata um nó como ``'Nome da Cidade (SIGLA)'`` para exibição em dropdowns
    e no painel de histórico.

    Exemplo: ``format_node('F')`` → ``'Feira de Santana (F)'``
    """
    return f"{NODE_LABELS.get(node, node)} ({node})"


def parse_node(display: str) -> str:
    """
    Extrai a SIGLA de uma string no formato ``'Nome da Cidade (SIGLA)'``.

    Exemplo: ``parse_node('Feira de Santana (F)')`` → ``'F'``
    """
    if "(" in display and display.endswith(")"):
        return display.rsplit("(", 1)[-1][:-1]
    return display


def format_path_short(path: list[str]) -> str:
    """
    Formata o caminho usando apenas os **nomes das cidades** (sem siglas),
    ideal para colunas de tabela onde o espaço é limitado.

    Exemplo: ``'Santanópolis → Jaçanã → Feira de Santana → Coité → Santo Amaro'``
    """
    if not path:
        return "— sem caminho —"
    return " → ".join(NODE_LABELS.get(n, n) for n in path)


def format_path_full(path: list[str]) -> str:
    """
    Formata o caminho como ``'Nome (SIGLA) → Nome (SIGLA) → ...'``,
    ideal para o painel de insights onde o espaço é maior.
    """
    if not path:
        return "— sem caminho —"
    return " → ".join(format_node(n) for n in path)
"""
ui/graph_view.py
================
Componente de visualização do grafo usando NetworkX e Matplotlib
embutidos num widget customtkinter via FigureCanvasTkAgg.

Melhorias em relação à versão anterior:
- Legenda simplificada com rótulos diretos (Origem / Destino / Caminho).
- Labels dos nós com fonte ~10% maior e contraste melhorado.
- Tooltip de nome completo ao passar o mouse sobre um nó (mantido).
- Nós 15% maiores com melhor distinção visual.
"""
from __future__ import annotations

from typing import Optional

import matplotlib
matplotlib.use("TkAgg")

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.lines import Line2D

import customtkinter as ctk

from core.graph import NODE_LABELS
from ui.styles import (
    BG_APP, BG_BORDER, BG_SURFACE,
    GRAPH_BG, GRAPH_NODE, GRAPH_NODE_BORDER, GRAPH_EDGE,
    GRAPH_PATH_EDGE, GRAPH_ORIGIN, GRAPH_DEST, GRAPH_PATH_NODE,
    GRAPH_LABEL, GRAPH_LABEL_HL, GRAPH_WEIGHT_BG,
    TEXT_MUTED,
)


class GraphView:
    """
    Renderiza o grafo geográfico com caminho destacado e tooltip interativo.

    Após cada chamada a ``render()``, o grafo é redesenhado com as cores
    de origem, destino e caminho atualizadas.
    Hover sobre um nó exibe o nome completo da cidade.
    """

    # ── Tamanhos de nós ──────────────────────────────────────────────────────
    _SZ_DEFAULT = 440
    _SZ_PATH    = 600
    _SZ_ENDPT   = 700

    # ── Espessuras de aresta ─────────────────────────────────────────────────
    _EW_DEFAULT = 1.2
    _EW_PATH    = 3.5

    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        graph_data: dict[str, dict[str, int]],
        fixed_pos:  dict[str, tuple[float, float]],
    ) -> None:
        self._graph_data = graph_data
        self._fixed_pos  = fixed_pos
        self._nx_graph   = self._build_nx_graph(graph_data)
        self._tooltip    = None
        self._hover_cid: int | None = None

        self._configure_mpl()

        self._fig, self._ax = plt.subplots(figsize=(18, 3.8), dpi=88)
        self._fig.patch.set_facecolor(GRAPH_BG)
        self._fig.subplots_adjust(left=0.01, right=0.99, top=0.97, bottom=0.03)

        self._canvas = FigureCanvasTkAgg(self._fig, master=parent)
        self._canvas.get_tk_widget().pack(fill="both", expand=True, padx=2, pady=2)

        self.render(path=None, start=None, end=None)

    # ─── Setup ────────────────────────────────────────────────────────────────

    @staticmethod
    def _configure_mpl() -> None:
        plt.rcParams.update({
            "figure.facecolor":  GRAPH_BG,
            "axes.facecolor":    GRAPH_BG,
            "text.color":        GRAPH_LABEL,
            "font.family":       "monospace",
            "savefig.facecolor": GRAPH_BG,
        })

    @staticmethod
    def _build_nx_graph(graph_data: dict[str, dict[str, int]]) -> nx.Graph:
        G = nx.Graph()
        for node, neighbors in graph_data.items():
            G.add_node(node)
            for neighbor, weight in neighbors.items():
                if not G.has_edge(node, neighbor):
                    G.add_edge(node, neighbor, weight=weight)
        return G

    # ─── Tooltip ──────────────────────────────────────────────────────────────

    def _attach_tooltip(self) -> None:
        """Cria anotação de tooltip e conecta o evento de hover."""
        if self._hover_cid is not None:
            try:
                self._canvas.mpl_disconnect(self._hover_cid)
            except Exception:
                pass

        self._tooltip = self._ax.annotate(
            "",
            xy=(0, 0),
            xytext=(14, 14),
            textcoords="offset points",
            bbox=dict(
                boxstyle="round,pad=0.4",
                facecolor=BG_SURFACE,
                edgecolor=BG_BORDER,
                alpha=0.96,
                linewidth=1,
            ),
            fontsize=9,
            color="#e6edf3",
            fontfamily="monospace",
            visible=False,
            zorder=10,
        )

        self._hover_cid = self._canvas.mpl_connect(
            "motion_notify_event", self._on_hover
        )

    def _on_hover(self, event) -> None:
        """Mostra o nome completo da cidade ao passar o mouse sobre um nó."""
        if event.inaxes != self._ax or self._tooltip is None:
            if self._tooltip and self._tooltip.get_visible():
                self._tooltip.set_visible(False)
                self._canvas.draw_idle()
            return

        if event.x is None or event.y is None:
            return

        HIT_RADIUS_PX = 24

        for node, (x, y) in self._fixed_pos.items():
            px, py = self._ax.transData.transform((x, y))
            dist   = ((event.x - px) ** 2 + (event.y - py) ** 2) ** 0.5
            if dist < HIT_RADIUS_PX:
                label = NODE_LABELS.get(node, node)
                self._tooltip.set_text(f"  {label} ({node})  ")
                self._tooltip.xy = (x, y)
                self._tooltip.set_visible(True)
                self._canvas.draw_idle()
                return

        if self._tooltip.get_visible():
            self._tooltip.set_visible(False)
            self._canvas.draw_idle()

    # ─── Render ───────────────────────────────────────────────────────────────

    def render(
        self,
        path:  Optional[list[str]],
        start: Optional[str],
        end:   Optional[str],
    ) -> None:
        """
        Redesenha o grafo completo com o caminho destacado.

        Args:
            path:  Sequência ordenada de nós do caminho (ou None).
            start: Nó de origem — exibido em verde.
            end:   Nó de destino — exibido em vermelho.
        """
        self._ax.clear()

        G   = self._nx_graph
        pos = self._fixed_pos

        # ── Identifica arestas e nós do caminho ───────────────────────────
        path_edge_set: set[frozenset[str]] = set()
        path_nodes:    set[str]            = set()

        if path and len(path) >= 2:
            path_nodes = set(path)
            path_edge_set = {
                frozenset((path[i], path[i + 1]))
                for i in range(len(path) - 1)
            }

        all_edges       = list(G.edges())
        normal_edges    = [e for e in all_edges if frozenset(e) not in path_edge_set]
        highlight_edges = [e for e in all_edges if frozenset(e) in path_edge_set]

        # ── Arestas normais ────────────────────────────────────────────────
        nx.draw_networkx_edges(
            G, pos, ax=self._ax,
            edgelist=normal_edges,
            edge_color=GRAPH_EDGE,
            width=self._EW_DEFAULT,
            alpha=0.40,
        )

        # ── Arestas do caminho ─────────────────────────────────────────────
        if highlight_edges:
            nx.draw_networkx_edges(
                G, pos, ax=self._ax,
                edgelist=highlight_edges,
                edge_color=GRAPH_PATH_EDGE,
                width=self._EW_PATH,
                alpha=0.92,
            )
            edge_labels = {
                (u, v): f"{G[u][v]['weight']} km"
                for u, v in highlight_edges
                if G.has_edge(u, v)
            }
            nx.draw_networkx_edge_labels(
                G, pos, ax=self._ax,
                edge_labels=edge_labels,
                font_color=GRAPH_PATH_EDGE,
                font_size=8,
                font_family="monospace",
                bbox=dict(
                    boxstyle="round,pad=0.25",
                    facecolor=GRAPH_WEIGHT_BG,
                    edgecolor="none",
                    alpha=0.90,
                ),
            )

        # ── Nós ───────────────────────────────────────────────────────────
        node_list   = list(G.nodes())
        node_colors = []
        node_sizes  = []

        for node in node_list:
            if node == start:
                node_colors.append(GRAPH_ORIGIN)
                node_sizes.append(self._SZ_ENDPT)
            elif node == end:
                node_colors.append(GRAPH_DEST)
                node_sizes.append(self._SZ_ENDPT)
            elif node in path_nodes:
                node_colors.append(GRAPH_PATH_NODE)
                node_sizes.append(self._SZ_PATH)
            else:
                node_colors.append(GRAPH_NODE)
                node_sizes.append(self._SZ_DEFAULT)

        nx.draw_networkx_nodes(
            G, pos, ax=self._ax,
            nodelist=node_list,
            node_color=node_colors,
            node_size=node_sizes,
            linewidths=1.5,
            edgecolors=GRAPH_NODE_BORDER,
        )

        # ── Labels dos nós — fonte +10% para melhor legibilidade ──────────
        for node in node_list:
            x, y        = pos[node]
            highlighted = node in path_nodes or node == start or node == end
            self._ax.text(
                x, y, node,
                ha="center", va="center",
                fontsize=11 if highlighted else 10,   # era 10/9
                fontweight="bold" if highlighted else "normal",
                color="#ffffff" if highlighted else "#c0cad6",  # contraste melhorado
                fontfamily="monospace",
                zorder=5,
            )

        # ── Legenda simplificada ───────────────────────────────────────────
        legend_items = []
        if start:
            legend_items.append(
                mpatches.Patch(color=GRAPH_ORIGIN, label="Origem")
            )
        if end:
            legend_items.append(
                mpatches.Patch(color=GRAPH_DEST, label="Destino")
            )
        if path_nodes - ({start} if start else set()) - ({end} if end else set()):
            legend_items.append(
                mpatches.Patch(color=GRAPH_PATH_NODE, label="Caminho")
            )
        # "Demais cidades" sempre presente para referência
        legend_items.append(
            mpatches.Patch(color=GRAPH_NODE, label="Demais cidades")
        )

        self._ax.legend(
            handles=legend_items,
            loc="upper right",
            facecolor=GRAPH_BG,
            edgecolor=BG_BORDER,
            labelcolor=GRAPH_LABEL,
            fontsize=9,
            framealpha=0.93,
            borderpad=0.6,
            labelspacing=0.4,
        )

        # ── Hint de estado vazio ───────────────────────────────────────────
        if not path:
            self._ax.text(
                0.5, 0.04,
                "Passe o mouse sobre um nó para ver o nome da cidade  ·  "
                "Execute um benchmark para destacar o caminho",
                transform=self._ax.transAxes,
                ha="center", va="bottom",
                fontsize=8.5, color=TEXT_MUTED,
                fontfamily="monospace",
            )

        self._ax.set_axis_off()
        self._ax.set_facecolor(GRAPH_BG)

        # Tooltip: recriar após ax.clear() e reconectar evento
        self._attach_tooltip()

        self._canvas.draw_idle()
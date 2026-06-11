"""
ui/styles.py
============
Paleta de cores, tipografia, dimensões e configuração de estilo TTK
para o tema escuro técnico da aplicação.

Centraliza todas as constantes visuais — nenhum valor de cor ou fonte
deve ser definido diretamente nos widgets.
"""
from __future__ import annotations

from tkinter import ttk

# ─── Paleta principal ─────────────────────────────────────────────────────────
BG_APP      = "#0d1117"    # Fundo da janela principal
BG_SURFACE  = "#161b22"    # Superfície de cards e painéis
BG_SURFACE2 = "#21262d"    # Superfície secundária / cabeçalhos de tabela
BG_HOVER    = "#1c2128"    # Estado de hover em linhas
BG_BORDER   = "#30363d"    # Bordas e divisores

# ─── Texto ────────────────────────────────────────────────────────────────────
TEXT_PRIMARY   = "#e6edf3"  # Texto principal
TEXT_SECONDARY = "#8b949e"  # Texto secundário / labels
TEXT_MUTED     = "#484f58"  # Texto inativo / seções

# ─── Cores de destaque ────────────────────────────────────────────────────────
ACCENT_BLUE   = "#388bfd"   # Azul primário (botão, links)
ACCENT_BLUE_H = "#2f7de8"   # Hover do azul primário
ACCENT_GREEN  = "#3fb950"   # Sucesso / vencedor / origem no grafo
ACCENT_GREEN_D = "#0d2018"  # Verde escuro de fundo (linha vencedora)
ACCENT_YELLOW = "#e3b341"   # Aviso / segunda posição
ACCENT_RED    = "#f85149"   # Erro / destino no grafo
ACCENT_ORANGE = "#d29922"   # Tertiary

# ─── Grafo / Matplotlib ───────────────────────────────────────────────────────
GRAPH_BG        = "#0d1117"
GRAPH_NODE      = "#21262d"
GRAPH_NODE_BORDER = "#30363d"
GRAPH_EDGE      = "#30363d"
GRAPH_PATH_EDGE = "#388bfd"
GRAPH_ORIGIN    = "#3fb950"
GRAPH_DEST      = "#f85149"
GRAPH_PATH_NODE = "#1f6feb"
GRAPH_LABEL     = "#8b949e"
GRAPH_LABEL_HL  = "#e6edf3"
GRAPH_WEIGHT_BG = "#0d1117"

# ─── Dimensões ────────────────────────────────────────────────────────────────
CORNER         = 8     # Raio de canto padrão (px)
PAD_XS         = 4
PAD_S          = 8
PAD_M          = 14
PAD_L          = 20
PAD_XL         = 28

PANEL_LEFT_W   = 252   # Largura do painel esquerdo (px) — reduzido ~12%
PANEL_RIGHT_W  = 285   # Largura do painel direito (px)
GRAPH_H        = 340   # Altura da área do grafo (px)
HEADER_H       = 62    # Altura do cabeçalho (px)

# ─── Configuração de benchmark ────────────────────────────────────────────────
N_EXECUTIONS   = 100

# ─── Configuração de TTK Treeview ─────────────────────────────────────────────

def configure_ttk_styles() -> None:
    """
    Configura o estilo escuro personalizado do Treeview TTK.
    Deve ser chamado após a janela principal ser criada.
    """
    style = ttk.Style()
    style.theme_use("clam")

    # ── Treeview body ──
    style.configure(
        "Results.Treeview",
        background=BG_SURFACE,
        foreground=TEXT_PRIMARY,
        rowheight=44,
        fieldbackground=BG_SURFACE,
        borderwidth=0,
        relief="flat",
        font=("Consolas", 11),
    )

    # ── Treeview headings ──
    style.configure(
        "Results.Treeview.Heading",
        background=BG_SURFACE2,
        foreground=TEXT_SECONDARY,
        borderwidth=0,
        relief="flat",
        font=("Consolas", 10),
        padding=(10, 12),
    )
    style.map(
        "Results.Treeview.Heading",
        background=[("active", BG_SURFACE2)],
        relief=[("active", "flat")],
    )

    # ── Selection ──
    style.map(
        "Results.Treeview",
        background=[("selected", "#1f6feb")],
        foreground=[("selected", "#ffffff")],
    )

    # Remove o ícone de árvore (usamos show="headings")
    style.layout("Results.Treeview", [
        ("Treeview.treearea", {"sticky": "nswe"})
    ])

    # ── Scrollbar ──
    style.configure(
        "Dark.Vertical.TScrollbar",
        background=BG_SURFACE2,
        troughcolor=BG_SURFACE,
        arrowcolor=TEXT_MUTED,
        borderwidth=0,
        relief="flat",
    )
    style.map(
        "Dark.Vertical.TScrollbar",
        background=[("active", BG_BORDER)],
    )
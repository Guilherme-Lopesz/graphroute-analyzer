"""
main.py
=======
Ponto de entrada da aplicação Comparador de Algoritmos em Grafos.

Define o backend do Matplotlib antes de qualquer import que o utilize,
valida o grafo em modo fail-fast e inicializa a janela customtkinter.
"""
from __future__ import annotations

import sys
from pathlib import Path

# ── Garante que o diretório raiz esteja no path de importação ─────────────────
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ── Backend do Matplotlib: deve ser definido antes de pyplot ──────────────────
import matplotlib
matplotlib.use("TkAgg")

import customtkinter as ctk

from core.graph import GRAPH
from core.validators import validate_graph
from ui.app import App


def main() -> None:
    """Inicializa e executa a aplicação desktop."""
    # Fail-fast: garante integridade do grafo antes de abrir a UI
    try:
        validate_graph(GRAPH)
    except ValueError as exc:
        print(f"[ERRO CRÍTICO] Grafo inválido:\n  {exc}", file=sys.stderr)
        sys.exit(1)

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()

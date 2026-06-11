"""
ui/app.py
=========
Janela principal da aplicação — revisão 3.

Melhorias em relação à v2:
• Tabela comparativa principal ocupa posição dominante no centro.
• Card de Análise compacto: máx. 3 bullets curtos, linguagem acadêmica.
• Estatísticas com Tempo Médio adicionado, tipografia +15%, números à direita.
• Card de Caminho no painel direito exibe nós verticalmente com nome completo.
• Grafo: cabeçalho informativo com custo, conexões e algoritmo exibido.
• Histórico: últimas 5 execuções no formato compacto.
• Espaçamento vertical melhorado entre seções.
"""
from __future__ import annotations

import csv
import json
import threading
from pathlib import Path
from tkinter import ttk

import customtkinter as ctk

from core.algorithms import ALGORITHM_NOTES, COMPLEXITIES
from core.benchmark import run_experiment
from core.graph import (
    FIXED_POS, GRAPH, NODE_LABELS, format_node, format_path_full,
    format_path_short, get_sorted_nodes, parse_node,
)
from core.models import ExperimentResult
from ui.components import (
    body_label, card, insight_card, mono_label,
    option_menu, section_label, separator, v_separator,
)
from ui.graph_view import GraphView
from ui.styles import (
    ACCENT_BLUE, ACCENT_BLUE_H, ACCENT_GREEN, ACCENT_GREEN_D,
    ACCENT_RED, BG_APP, BG_BORDER, BG_SURFACE, BG_SURFACE2,
    CORNER, GRAPH_H, HEADER_H, N_EXECUTIONS,
    PAD_L, PAD_M, PAD_S, PAD_XL, PAD_XS,
    PANEL_LEFT_W, PANEL_RIGHT_W, TEXT_MUTED, TEXT_PRIMARY,
    TEXT_SECONDARY, configure_ttk_styles,
)

_EXPORTS = Path("exports")
_EXPORTS.mkdir(exist_ok=True)
_MAX_HISTORY = 5          # últimas 5 execuções no histórico

_OPTIMAL: dict[str, str] = {
    "BFS":      "Não",
    "DFS":      "Não",
    "Dijkstra": "Sim  ✓",
}


class App(ctk.CTk):
    """Janela raiz da aplicação Comparador de Algoritmos em Grafos."""

    def __init__(self) -> None:
        super().__init__()

        self.title("Comparador de Algoritmos em Grafos")
        self.geometry("1440x900")
        self.minsize(1200, 820)
        self.configure(fg_color=BG_APP)

        self._current_result: ExperimentResult | None = None
        self._history:        list[ExperimentResult]  = []
        self._running:        bool                    = False

        configure_ttk_styles()
        self._build()

    # ═══════════════════════════════════════════════════════════════════════════
    # Layout principal
    # ═══════════════════════════════════════════════════════════════════════════

    def _build(self) -> None:
        self.grid_rowconfigure(0, weight=0, minsize=HEADER_H)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0, minsize=GRAPH_H)

        self.grid_columnconfigure(0, weight=0, minsize=PANEL_LEFT_W)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0, minsize=PANEL_RIGHT_W)

        self._build_header()
        self._build_left()
        self._build_center()
        self._build_right()
        self._build_graph()

    # ─── Cabeçalho ────────────────────────────────────────────────────────────

    def _build_header(self) -> None:
        hdr = ctk.CTkFrame(self, fg_color=BG_SURFACE, corner_radius=0)
        hdr.grid(row=0, column=0, columnspan=3, sticky="nsew")
        hdr.grid_columnconfigure(0, weight=1)

        ctk.CTkFrame(hdr, fg_color=BG_BORDER, height=1, corner_radius=0).place(
            relx=0, rely=1.0, relwidth=1.0, anchor="sw"
        )

        title_row = ctk.CTkFrame(hdr, fg_color="transparent")
        title_row.grid(row=0, column=0, sticky="w", padx=PAD_XL)

        ctk.CTkLabel(
            title_row,
            text="Comparador de Algoritmos em Grafos",
            font=ctk.CTkFont("Segoe UI", 19, weight="bold"),
            text_color=TEXT_PRIMARY,
        ).pack(side="left")

        ctk.CTkLabel(
            title_row,
            text="   BFS  ·  DFS  ·  Dijkstra",
            font=ctk.CTkFont("Segoe UI", 12),
            text_color=TEXT_MUTED,
        ).pack(side="left", pady=(3, 0))

    # ─── Painel esquerdo ──────────────────────────────────────────────────────

    def _build_left(self) -> None:
        panel = ctk.CTkFrame(self, fg_color=BG_APP, corner_radius=0)
        panel.grid(row=1, column=0, sticky="nsew")
        panel.grid_rowconfigure(1, weight=1)
        panel.grid_columnconfigure(0, weight=1)
        v_separator(panel, relx=1.0, rely=0, relheight=1.0, anchor="ne")

        self._build_config(panel)
        self._build_history(panel)

    def _build_config(self, parent: ctk.CTkFrame) -> None:
        cfg = card(parent, row=0, column=0, sticky="new",
                   padx=PAD_M, pady=(PAD_M, PAD_S))

        section_label(cfg, "CONFIGURAÇÃO",
                      row=0, column=0, sticky="w", padx=PAD_M, pady=(PAD_M, PAD_S))

        nodes   = get_sorted_nodes()
        options = [format_node(n) for n in nodes]

        body_label(cfg, "Origem", size=12,
                   row=1, column=0, sticky="w", padx=PAD_M)
        self._origin_var = ctk.StringVar(value=format_node("S"))
        option_menu(cfg, self._origin_var, options,
                    command=self._clear_error,
                    row=2, column=0, sticky="ew",
                    padx=PAD_M, pady=(3, PAD_S))

        body_label(cfg, "Destino", size=12,
                   row=3, column=0, sticky="w", padx=PAD_M)
        self._dest_var = ctk.StringVar(value=format_node("SA"))
        option_menu(cfg, self._dest_var, options,
                    command=self._clear_error,
                    row=4, column=0, sticky="ew",
                    padx=PAD_M, pady=(3, PAD_S))

        self._err_lbl = ctk.CTkLabel(
            cfg, text="",
            font=ctk.CTkFont("Segoe UI", 10),
            text_color=ACCENT_RED,
            wraplength=220, justify="left",
        )
        self._err_lbl.grid(row=5, column=0, padx=PAD_M, pady=(0, PAD_XS), sticky="ew")

        body_label(cfg, f"{N_EXECUTIONS} execuções por algoritmo",
                   color=TEXT_MUTED, size=10,
                   row=6, column=0, sticky="w", padx=PAD_M, pady=(0, PAD_S))

        separator(cfg, row=7, column=0, sticky="ew", padx=PAD_M, pady=(0, PAD_M))

        self._run_btn = ctk.CTkButton(
            cfg,
            text="▶   Executar Benchmark",
            command=self._on_run,
            fg_color=ACCENT_BLUE,
            hover_color=ACCENT_BLUE_H,
            text_color="#ffffff",
            font=ctk.CTkFont("Segoe UI", 13, weight="bold"),
            height=44,
            corner_radius=CORNER,
        )
        self._run_btn.grid(row=8, column=0, padx=PAD_M, pady=(0, PAD_S), sticky="ew")

        self._progress = ctk.CTkProgressBar(
            cfg,
            mode="indeterminate",
            height=3,
            corner_radius=2,
            progress_color=ACCENT_BLUE,
            fg_color=BG_SURFACE2,
        )

        self._export_btn = ctk.CTkButton(
            cfg,
            text="↓  Exportar Resultado",
            command=self._export,
            fg_color=BG_SURFACE2,
            hover_color=BG_BORDER,
            border_color=BG_BORDER,
            border_width=1,
            text_color=TEXT_SECONDARY,
            font=ctk.CTkFont("Segoe UI", 11),
            height=36,
            corner_radius=CORNER,
            state="disabled",
        )
        self._export_btn.grid(row=9, column=0, padx=PAD_M, pady=(0, PAD_M), sticky="ew")

    def _build_history(self, parent: ctk.CTkFrame) -> None:
        hist = card(parent, row=1, column=0, sticky="nsew",
                    padx=PAD_M, pady=(0, PAD_M))
        hist.grid_rowconfigure(1, weight=1)

        section_label(hist, f"HISTÓRICO  (últimas {_MAX_HISTORY})",
                      row=0, column=0, sticky="w", padx=PAD_M, pady=(PAD_M, PAD_XS))

        self._hist_scroll = ctk.CTkScrollableFrame(
            hist, fg_color="transparent",
            scrollbar_button_color=BG_BORDER,
            scrollbar_button_hover_color=TEXT_MUTED,
        )
        self._hist_scroll.grid(row=1, column=0, sticky="nsew", padx=PAD_S, pady=(0, PAD_S))
        self._hist_scroll.grid_columnconfigure(0, weight=1)

        self._hist_empty = body_label(
            self._hist_scroll,
            "Nenhuma execução recente.",
            color=TEXT_MUTED, size=11,
        )
        self._hist_empty.pack(pady=PAD_L)

    # ─── Painel central ───────────────────────────────────────────────────────

    def _build_center(self) -> None:
        panel = ctk.CTkFrame(self, fg_color=BG_APP, corner_radius=0)
        panel.grid(row=1, column=1, sticky="nsew")
        panel.grid_rowconfigure(0, weight=0)   # RESULTADOS header
        panel.grid_rowconfigure(1, weight=0)   # tabela — altura fixa
        panel.grid_rowconfigure(2, weight=0)   # análise — card compacto
        panel.grid_rowconfigure(3, weight=1)   # estatísticas — preenche restante
        panel.grid_columnconfigure(0, weight=1)
        v_separator(panel, relx=1.0, rely=0, relheight=1.0, anchor="ne")

        # ── Header de seção ────────────────────────────────────────────
        hrow = ctk.CTkFrame(panel, fg_color="transparent")
        hrow.grid(row=0, column=0, sticky="ew", padx=PAD_XL, pady=(PAD_L, PAD_M))
        hrow.grid_columnconfigure(0, weight=1)

        section_label(hrow, "RESULTADOS", row=0, column=0, sticky="w")

        body_label(hrow,
                   f"{N_EXECUTIONS} execuções por algoritmo",
                   color=TEXT_MUTED, size=10,
                   row=0, column=1, sticky="e")

        # ── Tabela comparativa — elemento central dominante ─────────────
        tbl_frame = card(panel, row=1, column=0, sticky="ew",
                         padx=PAD_XL, pady=(0, PAD_M))
        tbl_frame.grid_rowconfigure(0, weight=0)
        tbl_frame.grid_columnconfigure(0, weight=1)

        self._tree = ttk.Treeview(
            tbl_frame,
            columns=("rank", "algo", "path", "cost", "mean", "std", "optimal"),
            show="headings",
            style="Results.Treeview",
            selectmode="none",
            height=3,          # exatamente 3 linhas — sem scrollbar
        )

        cols = {
            "rank":    ("#",                    50,  "center"),
            "algo":    ("ALGORITMO",           110,  "center"),
            "path":    ("CAMINHO ENCONTRADO",  280,  "w"),
            "cost":    ("CUSTO (km)",           80,  "center"),
            "mean":    ("TEMPO MÉDIO",         130,  "center"),
            "std":     ("DESVIO PADRÃO",       130,  "center"),
            "optimal": ("ÓTIMO?",               68,  "center"),
        }
        for cid, (label, width, anchor) in cols.items():
            self._tree.heading(cid, text=label)
            self._tree.column(cid, width=width, anchor=anchor,
                              minwidth=40, stretch=True)

        self._tree.tag_configure("rank1",
            background=ACCENT_GREEN_D, foreground=ACCENT_GREEN)
        self._tree.tag_configure("rank2",
            background=BG_SURFACE, foreground=TEXT_PRIMARY)
        self._tree.tag_configure("rank3",
            background=BG_SURFACE, foreground=TEXT_SECONDARY)

        self._tree.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)

        self._tbl_empty = ctk.CTkLabel(
            tbl_frame,
            text="Execute um benchmark para ver os resultados.",
            font=ctk.CTkFont("Segoe UI", 12),
            text_color=TEXT_MUTED,
        )
        self._tbl_empty.place(relx=0.5, rely=0.5, anchor="center")

        # ── Card de Análise — compacto, máx. 3 bullets ─────────────────
        self._analysis_card = card(panel, row=2, column=0, sticky="ew",
                                   padx=PAD_XL, pady=(0, PAD_M))
        section_label(self._analysis_card, "ANÁLISE",
                      row=0, column=0, sticky="w",
                      padx=PAD_M, pady=(PAD_S, 4))

        self._analysis_lbl = ctk.CTkLabel(
            self._analysis_card,
            text="Execute um benchmark para gerar a análise automática.",
            font=ctk.CTkFont("Segoe UI", 11),
            text_color=TEXT_MUTED,
            wraplength=0,
            justify="left",
            anchor="nw",
        )
        self._analysis_lbl.grid(row=1, column=0, sticky="ew",
                                padx=PAD_M, pady=(0, PAD_S))

        # ── Estatísticas detalhadas — mini-cards alinhados ──────────────
        self._build_stats(panel, row=3)

    def _build_stats(self, parent: ctk.CTkFrame, row: int) -> None:
        """Mini-cards de estatísticas detalhadas por algoritmo."""
        outer = card(parent, row=row, column=0, sticky="nsew",
                     padx=PAD_XL, pady=(0, PAD_M))
        outer.grid_rowconfigure(1, weight=1)          # mini-cards expandem verticalmente
        outer.grid_columnconfigure((0, 1, 2), weight=1)

        section_label(outer, "ESTATÍSTICAS DETALHADAS",
                      row=0, column=0, columnspan=3,
                      sticky="w", padx=PAD_M, pady=(PAD_M, PAD_S))

        self._stat_labels: dict[str, dict[str, ctk.CTkLabel]] = {}

        for col_idx, algo in enumerate(["BFS", "DFS", "Dijkstra"]):
            mini = ctk.CTkFrame(outer, fg_color=BG_SURFACE2, corner_radius=6)
            mini.grid(row=1, column=col_idx, sticky="nsew",
                      padx=(PAD_M if col_idx == 0 else PAD_S,
                            PAD_M if col_idx == 2 else PAD_S),
                      pady=(0, PAD_M))
            mini.grid_columnconfigure(0, weight=1)    # label à esquerda expande
            mini.grid_columnconfigure(1, weight=0)    # valor à direita — fixo

            mono_label(mini, algo, bold=True, color=TEXT_PRIMARY,
                       size=13, row=0, column=0, columnspan=2,
                       sticky="w", padx=PAD_M, pady=(PAD_M, PAD_S))

            stat_rows = {}
            entries = [
                ("mean",   "Tempo médio"),
                ("median", "Mediana"),
                ("min",    "Mínimo"),
                ("max",    "Máximo"),
                ("std",    "σ (desvio)"),
            ]
            for r, (key, lbl) in enumerate(entries, start=1):
                body_label(mini, lbl, color=TEXT_MUTED, size=11,
                           row=r, column=0, sticky="w",
                           padx=(PAD_M, PAD_S), pady=3)
                val = mono_label(mini, "—", color=TEXT_SECONDARY,
                                 size=12, row=r, column=1, sticky="e",
                                 padx=(0, PAD_M), pady=3)
                stat_rows[key] = val

            body_label(mini, "ms", color=TEXT_MUTED, size=9,
                       row=len(entries) + 1, column=0, columnspan=2,
                       sticky="e", padx=PAD_M, pady=(0, PAD_M))

            self._stat_labels[algo] = stat_rows

    # ─── Painel direito ───────────────────────────────────────────────────────

    def _build_right(self) -> None:
        panel = ctk.CTkFrame(self, fg_color=BG_APP, corner_radius=0)
        panel.grid(row=1, column=2, sticky="nsew")
        panel.grid_rowconfigure(1, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        section_label(panel, "INSIGHTS",
                      row=0, column=0, sticky="w",
                      padx=PAD_XL, pady=(PAD_L, PAD_S))

        scroll = ctk.CTkScrollableFrame(
            panel, fg_color="transparent",
            scrollbar_button_color=BG_BORDER,
            scrollbar_button_hover_color=TEXT_MUTED,
        )
        scroll.grid(row=1, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        # ── Mais rápido ────────────────────────────────────────────────
        fast_card, _ = insight_card(scroll, "🥇  MAIS RÁPIDO", row=0)
        self._fast_name = mono_label(fast_card, "—",
                                     bold=True, size=20, color=ACCENT_GREEN,
                                     row=1, column=0, sticky="w",
                                     padx=PAD_M, pady=(0, 2))
        self._fast_time = mono_label(fast_card, "",
                                     size=11, color=TEXT_SECONDARY,
                                     row=2, column=0, sticky="w",
                                     padx=PAD_M, pady=(0, PAD_M))

        # ── Custo ótimo ────────────────────────────────────────────────
        cost_card, _ = insight_card(scroll, "CUSTO ÓTIMO GARANTIDO", row=1)
        self._cost_name = mono_label(cost_card, "—",
                                     bold=True, size=18, color=ACCENT_BLUE,
                                     row=1, column=0, sticky="w",
                                     padx=PAD_M, pady=(0, 2))
        self._cost_val = mono_label(cost_card, "",
                                    size=10, color=TEXT_SECONDARY,
                                    row=2, column=0, sticky="w",
                                    padx=PAD_M, pady=(0, PAD_M))

        # ── Caminho — expandido com nome completo por nó ───────────────
        path_card, _ = insight_card(scroll, "CAMINHO  (DIJKSTRA)", row=2)
        self._path_lbl = ctk.CTkLabel(
            path_card,
            text="—",
            font=ctk.CTkFont("Consolas", 10),
            text_color=TEXT_PRIMARY,
            wraplength=0,
            justify="left",
            anchor="nw",
        )
        self._path_lbl.grid(row=1, column=0, sticky="w",
                            padx=PAD_M, pady=(0, 4))
        self._path_meta = mono_label(path_card, "",
                                     size=10, color=TEXT_MUTED,
                                     row=2, column=0, sticky="w",
                                     padx=PAD_M, pady=(0, PAD_M))

        # ── Complexidade assintótica ────────────────────────────────────
        cplx_card, _ = insight_card(scroll, "COMPLEXIDADE ASSINTÓTICA", row=3)
        for i, (algo, cplx) in enumerate(COMPLEXITIES.items()):
            row_f = ctk.CTkFrame(cplx_card, fg_color="transparent")
            row_f.grid(row=i + 1, column=0, sticky="ew", padx=PAD_M, pady=2)
            mono_label(row_f, f"{algo:<9}", bold=True, color=TEXT_PRIMARY).pack(side="left")
            mono_label(row_f, cplx, color=TEXT_SECONDARY).pack(side="left", padx=(6, 0))

        note_f = ctk.CTkFrame(cplx_card, fg_color="transparent")
        note_f.grid(row=len(COMPLEXITIES) + 1, column=0, sticky="ew",
                    padx=PAD_M, pady=(PAD_S, PAD_M))
        for algo, note in ALGORITHM_NOTES.items():
            body_label(note_f, f"{algo}: {note}", color=TEXT_MUTED, size=9).pack(anchor="w")

    # ─── Área do grafo ────────────────────────────────────────────────────────

    def _build_graph(self) -> None:
        ctk.CTkFrame(self, fg_color=BG_BORDER, height=1, corner_radius=0).grid(
            row=2, column=0, columnspan=3, sticky="ew"
        )

        area = ctk.CTkFrame(self, fg_color=BG_APP, corner_radius=0, height=GRAPH_H)
        area.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=(1, 0))
        area.grid_propagate(False)
        area.grid_rowconfigure(2, weight=1)
        area.grid_columnconfigure(0, weight=1)

        # ── Cabeçalho do grafo — título + algoritmo exibido ────────────
        hdr_row = ctk.CTkFrame(area, fg_color="transparent")
        hdr_row.grid(row=0, column=0, sticky="ew", padx=PAD_XL, pady=(PAD_M, 0))
        hdr_row.grid_columnconfigure(0, weight=1)

        section_label(hdr_row, "VISUALIZAÇÃO DO GRAFO",
                      row=0, column=0, sticky="w")

        self._graph_algo_lbl = ctk.CTkLabel(
            hdr_row,
            text="",
            font=ctk.CTkFont("Consolas", 10),
            text_color=TEXT_MUTED,
        )
        self._graph_algo_lbl.grid(row=0, column=1, sticky="e")

        # ── Resumo do caminho ──────────────────────────────────────────
        self._path_summary = ctk.CTkLabel(
            area,
            text="Passe o mouse sobre um nó para ver o nome da cidade",
            font=ctk.CTkFont("Segoe UI", 10),
            text_color=TEXT_MUTED,
        )
        self._path_summary.grid(row=1, column=0, sticky="w",
                                padx=PAD_XL, pady=(2, PAD_XS))

        graph_card = card(area, row=2, column=0, sticky="nsew",
                          padx=PAD_XL, pady=(0, PAD_M))
        graph_card.grid_rowconfigure(0, weight=1)
        graph_card.grid_columnconfigure(0, weight=1)

        self._graph_view = GraphView(graph_card, GRAPH, FIXED_POS)

    # ═══════════════════════════════════════════════════════════════════════════
    # Handlers
    # ═══════════════════════════════════════════════════════════════════════════

    def _clear_error(self, _: str = "") -> None:
        self._err_lbl.configure(text="")

    def _set_error(self, msg: str) -> None:
        self._err_lbl.configure(text=msg)

    def _on_run(self) -> None:
        origin_display = self._origin_var.get()
        dest_display   = self._dest_var.get()
        origin = parse_node(origin_display)
        dest   = parse_node(dest_display)

        if not origin:
            self._set_error("Selecione um vértice de origem.")
            return
        if not dest:
            self._set_error("Selecione um vértice de destino.")
            return
        if origin == dest:
            self._set_error("Origem e destino devem ser diferentes.")
            return

        self._set_error("")
        self._set_loading(True)

        def _worker() -> None:
            try:
                result = run_experiment(origin, dest, N_EXECUTIONS)
                self.after(0, lambda: self._on_done(result))
            except Exception as exc:  # noqa: BLE001
                self.after(0, lambda: self._on_error(str(exc)))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_done(self, result: ExperimentResult) -> None:
        self._current_result = result
        self._history.insert(0, result)
        if len(self._history) > _MAX_HISTORY:
            self._history.pop()

        self._update_table(result)
        self._update_stats(result)
        self._update_insights(result)
        self._update_analysis(result)
        self._update_history()
        self._update_path_summary(result)
        self._graph_view.render(
            path=result.fastest[1].result.path,
            start=result.start,
            end=result.end,
        )
        self._set_loading(False)
        self._export_btn.configure(state="normal")

    def _on_error(self, msg: str) -> None:
        self._set_error(msg)
        self._set_loading(False)

    # ═══════════════════════════════════════════════════════════════════════════
    # Atualização de componentes
    # ═══════════════════════════════════════════════════════════════════════════

    def _update_table(self, result: ExperimentResult) -> None:
        """Preenche a tabela com caminho legível por extenso (nome completo)."""
        for row in self._tree.get_children():
            self._tree.delete(row)
        self._tbl_empty.place_forget()

        medals = {0: "  🥇", 1: "  🥈", 2: "  🥉"}
        tags   = {0: "rank1", 1: "rank2", 2: "rank3"}

        for rank, (name, data) in enumerate(result.sorted_by_speed):
            path     = data.result.path
            # Usa nome completo: Amélia Rodrigues (A) → Feira (F) → Jaçanã (J)
            path_str = format_path_full(path) if path else "— sem caminho —"

            MAX = 58
            if len(path_str) > MAX:
                path_str = path_str[:MAX - 1] + "…"

            cost     = data.result.cost
            cost_str = str(int(cost)) if cost != float("inf") else "—"

            self._tree.insert(
                "", "end",
                values=(
                    medals[rank],
                    name,
                    f"  {path_str}",
                    cost_str,
                    f"{data.mean_ms:.4f} ms",
                    f"± {data.std_ms:.4f}",
                    _OPTIMAL.get(name, "—"),
                ),
                tags=(tags[rank],),
            )

    def _update_stats(self, result: ExperimentResult) -> None:
        """Atualiza todos os 5 valores dos mini-cards de estatísticas."""
        for algo, rows in self._stat_labels.items():
            data = result.results.get(algo)
            if not data:
                continue
            rows["mean"].configure(text=f"{data.mean_ms:.6f}")
            rows["median"].configure(text=f"{data.median_ms:.6f}")
            rows["min"].configure(text=f"{data.min_ms:.6f}")
            rows["max"].configure(text=f"{data.max_ms:.6f}")
            rows["std"].configure(text=f"{data.std_ms:.6f}")

    def _update_insights(self, result: ExperimentResult) -> None:
        """Atualiza os 4 cards de insights no painel direito."""
        fast_name, fast_data = result.fastest
        self._fast_name.configure(text=fast_name)
        self._fast_time.configure(
            text=f"{fast_data.mean_ms:.4f} ms  (med: {fast_data.median_ms:.4f})"
        )

        dijk = result.results.get("Dijkstra")
        self._cost_name.configure(text="Dijkstra")
        if dijk and dijk.result.cost != float("inf"):
            self._cost_val.configure(
                text=f"{int(dijk.result.cost)} km  (mínimo garantido)"
            )
        else:
            self._cost_val.configure(text="— sem caminho encontrado —")

        # Caminho vertical: cada nó em sua linha com nome completo
        if dijk and dijk.result.path:
            path  = dijk.result.path
            lines = []
            for i, node in enumerate(path):
                full_name = NODE_LABELS.get(node, node)
                prefix = "→ " if i > 0 else "   "
                lines.append(f"{prefix}{full_name} ({node})")
            self._path_lbl.configure(text="\n".join(lines))

            cost     = dijk.result.cost
            hops     = len(path) - 1
            conn_str = "conexão" if hops == 1 else "conexões"
            self._path_meta.configure(text=f"{int(cost)} km  ·  {hops} {conn_str}")
        else:
            self._path_lbl.configure(text="— sem caminho encontrado —")
            self._path_meta.configure(text="")

    def _update_analysis(self, result: ExperimentResult) -> None:
        """Gera e exibe a análise automática compacta (máx. 3 bullets)."""
        text = self._generate_analysis(result)
        self._analysis_lbl.configure(
            text=text, text_color=TEXT_PRIMARY,
            wraplength=max(300, self.winfo_width() - PANEL_LEFT_W - PANEL_RIGHT_W - 80),
        )

    @staticmethod
    def _generate_analysis(result: ExperimentResult) -> str:
        """
        Retorna no máximo 3 bullets curtos com linguagem acadêmica.
        Evita afirmações absolutas sobre convergência de rota.
        """
        fast_name, fast_data = result.fastest
        dijk = result.results.get("Dijkstra")

        lines: list[str] = []

        # Bullet 1 — vencedor em tempo
        lines.append(
            f"• {fast_name} apresentou o menor tempo médio neste cenário "
            f"({fast_data.mean_ms:.4f} ms)."
        )

        # Bullet 2 — Dijkstra e custo ótimo (se não for o vencedor)
        if fast_name != "Dijkstra" and dijk:
            lines.append(
                "• Dijkstra garantiu formalmente o menor custo, "
                "sendo a escolha ideal para rotas críticas."
            )

        # Bullet 3 — convergência de rotas
        paths = [
            tuple(d.result.path)
            for d in result.results.values()
            if d.result.path
        ]
        if paths and len(set(paths)) == 1:
            lines.append(
                "• Neste experimento, todos os algoritmos encontraram a mesma rota."
            )
        elif len(set(paths)) > 1:
            lines.append(
                "• Os algoritmos encontraram rotas distintas — "
                "Dijkstra retorna o menor custo garantido."
            )

        return "\n".join(lines[:3])

    def _update_history(self) -> None:
        """Renderiza os últimos _MAX_HISTORY experimentos no formato compacto."""
        for w in self._hist_scroll.winfo_children():
            w.destroy()

        if not self._history:
            self._hist_empty.pack(pady=PAD_L)
            return

        for exp in self._history:
            fast_name, fast_data = exp.fastest

            start_full  = NODE_LABELS.get(exp.start, exp.start)
            end_full    = NODE_LABELS.get(exp.end, exp.end)

            # Nome curto: primeira palavra se o nome for longo
            start_short = start_full  if len(start_full) <= 13 else start_full.split()[0]
            end_short   = end_full    if len(end_full) <= 13   else end_full.split()[0]

            ts = exp.timestamp.strftime("%H:%M")

            # Custo de referência (Dijkstra)
            dijk_data = exp.results.get("Dijkstra")
            cost_str  = ""
            if dijk_data and dijk_data.result.cost != float("inf"):
                cost_str = f"  ·  {int(dijk_data.result.cost)} km"

            item = ctk.CTkFrame(self._hist_scroll, fg_color=BG_SURFACE2, corner_radius=6)
            item.pack(fill="x", padx=PAD_XS, pady=(0, 4))
            item.grid_columnconfigure(0, weight=1)

            mono_label(item, f"{start_short}  →  {end_short}",
                       bold=True, color=TEXT_PRIMARY, size=11,
                       row=0, column=0, sticky="w",
                       padx=PAD_S, pady=(PAD_S, 2))

            body_label(item,
                       f"{fast_name}{cost_str}  ·  {ts}",
                       color=TEXT_MUTED, size=10,
                       row=1, column=0, sticky="w",
                       padx=PAD_S, pady=(0, PAD_S))

    def _update_path_summary(self, result: ExperimentResult) -> None:
        """Atualiza o resumo de custo/conexões e o algoritmo exibido no grafo."""
        fast_name, fast_data = result.fastest
        path = fast_data.result.path
        if path:
            hops     = len(path) - 1
            cost     = fast_data.result.cost
            conn_str = "conexão" if hops == 1 else "conexões"
            start_name = NODE_LABELS.get(result.start, result.start)
            end_name   = NODE_LABELS.get(result.end, result.end)
            self._path_summary.configure(
                text=(
                    f"{int(cost)} km  ·  {hops} {conn_str}  ·  "
                    f"{start_name} → {end_name}"
                ),
                text_color=TEXT_SECONDARY,
            )
            self._graph_algo_lbl.configure(text=f"Algoritmo exibido: {fast_name}")
        else:
            self._path_summary.configure(
                text="Nenhum caminho encontrado para este par.",
                text_color=ACCENT_RED,
            )
            self._graph_algo_lbl.configure(text="")

    def _set_loading(self, loading: bool) -> None:
        self._running = loading
        if loading:
            self._run_btn.configure(
                text="⏳   Executando benchmark…",
                state="disabled",
                fg_color=BG_SURFACE2,
                text_color=TEXT_SECONDARY,
            )
            self._progress.grid(row=10, column=0, padx=PAD_M,
                                pady=(0, PAD_M), sticky="ew")
            self._progress.start()
        else:
            self._progress.stop()
            self._progress.grid_forget()
            self._run_btn.configure(
                text="▶   Executar Benchmark",
                state="normal",
                fg_color=ACCENT_BLUE,
                text_color="#ffffff",
            )

    # ═══════════════════════════════════════════════════════════════════════════
    # Exportação
    # ═══════════════════════════════════════════════════════════════════════════

    def _export(self) -> None:
        if not self._current_result:
            return

        res  = self._current_result
        ts   = res.timestamp.strftime("%Y%m%d_%H%M%S")
        stem = _EXPORTS / f"benchmark_{res.start}_{res.end}_{ts}"

        payload = {
            "timestamp": res.timestamp.isoformat(),
            "config": {
                "start":      res.start,
                "start_name": NODE_LABELS.get(res.start, res.start),
                "end":        res.end,
                "end_name":   NODE_LABELS.get(res.end, res.end),
                "executions": res.n_executions,
            },
            "results": {
                name: {
                    "path":                 data.result.path,
                    "path_full":            format_path_full(data.result.path) if data.result.path else None,
                    "cost_km":              data.result.cost if data.result.cost != float("inf") else None,
                    "optimal_guaranteed":   _OPTIMAL.get(name, "Não"),
                    "mean_ms":              round(data.mean_ms,   6),
                    "std_ms":               round(data.std_ms,    6),
                    "median_ms":            round(data.median_ms, 6),
                    "min_ms":               round(data.min_ms,    6),
                    "max_ms":               round(data.max_ms,    6),
                }
                for name, data in res.results.items()
            },
        }
        stem.with_suffix(".json").write_text(
            json.dumps(payload, indent=4, ensure_ascii=False), encoding="utf-8"
        )

        csv_path = stem.with_suffix(".csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow([
                "algorithm", "path_short", "path_full", "cost_km",
                "optimal_guaranteed", "mean_ms", "std_ms",
                "median_ms", "min_ms", "max_ms",
            ])
            for name, data in res.results.items():
                pshort = format_path_short(data.result.path) if data.result.path else ""
                pfull  = format_path_full(data.result.path)  if data.result.path else ""
                cost   = data.result.cost if data.result.cost != float("inf") else ""
                w.writerow([
                    name, pshort, pfull, cost,
                    _OPTIMAL.get(name, "Não"),
                    round(data.mean_ms,   6), round(data.std_ms,    6),
                    round(data.median_ms, 6), round(data.min_ms,    6),
                    round(data.max_ms,    6),
                ])
"""
ui/components.py
================
Fábrica de widgets reutilizáveis. Centraliza padrões de criação de
componentes para manter ``app.py`` coeso e eliminar duplicação visual.
"""
from __future__ import annotations

import customtkinter as ctk

from ui.styles import (
    BG_SURFACE, BG_SURFACE2, BG_BORDER,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    CORNER, PAD_M, PAD_S,
)


def section_label(
    parent: ctk.CTkBaseClass,
    text: str,
    **grid_kwargs,
) -> ctk.CTkLabel:
    """Cria um label de seção em letras maiúsculas e tom muted."""
    lbl = ctk.CTkLabel(
        parent,
        text=text,
        font=ctk.CTkFont("Segoe UI", 10, weight="bold"),
        text_color=TEXT_MUTED,
    )
    if grid_kwargs:
        lbl.grid(**grid_kwargs)
    return lbl


def body_label(
    parent: ctk.CTkBaseClass,
    text: str,
    color: str = TEXT_SECONDARY,
    size: int = 11,
    **grid_kwargs,
) -> ctk.CTkLabel:
    """Cria um label de corpo com tamanho e cor configuráveis."""
    lbl = ctk.CTkLabel(
        parent,
        text=text,
        font=ctk.CTkFont("Segoe UI", size),
        text_color=color,
    )
    if grid_kwargs:
        lbl.grid(**grid_kwargs)
    return lbl


def mono_label(
    parent: ctk.CTkBaseClass,
    text: str,
    size: int = 11,
    color: str = TEXT_PRIMARY,
    bold: bool = False,
    wrap: int = 0,
    **grid_kwargs,
) -> ctk.CTkLabel:
    """Label com fonte monospace, ideal para paths, valores numéricos e código."""
    weight = "bold" if bold else "normal"
    lbl = ctk.CTkLabel(
        parent,
        text=text,
        font=ctk.CTkFont("Consolas", size, weight=weight),
        text_color=color,
        wraplength=wrap if wrap else 0,
        justify="left",
    )
    if grid_kwargs:
        lbl.grid(**grid_kwargs)
    return lbl


def card(
    parent: ctk.CTkBaseClass,
    fg: str = BG_SURFACE,
    radius: int = CORNER,
    **grid_kwargs,
) -> ctk.CTkFrame:
    """Cria um frame card com fundo e canto arredondado padronizados."""
    f = ctk.CTkFrame(parent, fg_color=fg, corner_radius=radius)
    f.grid_columnconfigure(0, weight=1)
    if grid_kwargs:
        f.grid(**grid_kwargs)
    return f


def separator(
    parent: ctk.CTkBaseClass,
    **grid_kwargs,
) -> ctk.CTkFrame:
    """Divisor horizontal de 1px."""
    sep = ctk.CTkFrame(
        parent,
        fg_color=BG_BORDER,
        height=1,
        corner_radius=0,
    )
    if grid_kwargs:
        sep.grid(**grid_kwargs)
    return sep


def v_separator(
    parent: ctk.CTkBaseClass,
    **place_kwargs,
) -> ctk.CTkFrame:
    """Divisor vertical de 1px posicionado via place()."""
    sep = ctk.CTkFrame(
        parent,
        fg_color=BG_BORDER,
        width=1,
        corner_radius=0,
    )
    if place_kwargs:
        sep.place(**place_kwargs)
    return sep


def insight_card(
    parent: ctk.CTkBaseClass,
    title: str,
    row: int,
) -> tuple[ctk.CTkFrame, ctk.CTkLabel]:
    """
    Cria um card de insight com título padronizado.

    Returns:
        Tupla (card_frame, title_label) para customização posterior.
    """
    f = card(parent, row=row, column=0, sticky="ew", padx=PAD_M, pady=(0, PAD_S))

    title_lbl = section_label(
        f, title,
        row=0, column=0, sticky="w", padx=PAD_M, pady=(PAD_M, 4),
    )
    return f, title_lbl


def option_menu(
    parent: ctk.CTkBaseClass,
    variable: ctk.StringVar,
    values: list[str],
    command=None,
    **grid_kwargs,
) -> ctk.CTkOptionMenu:
    """OptionMenu com tema escuro padronizado."""
    menu = ctk.CTkOptionMenu(
        parent,
        variable=variable,
        values=values,
        command=command,
        fg_color=BG_SURFACE2,
        button_color=BG_BORDER,
        button_hover_color=BG_BORDER,
        dropdown_fg_color=BG_SURFACE2,
        text_color=TEXT_PRIMARY,
        dropdown_text_color=TEXT_PRIMARY,
        font=ctk.CTkFont("Consolas", 12),
        dropdown_font=ctk.CTkFont("Consolas", 11),
        corner_radius=CORNER,
        dynamic_resizing=False,
        anchor="w",
    )
    if grid_kwargs:
        menu.grid(**grid_kwargs)
    return menu

"""Paleta clara compartida por los módulos de PyMatrix."""

import customtkinter as ctk
from customtkinter import ThemeManager


LIGHT = {
    "background": "#d7e4f2",
    "panel": "#e3edf5",
    "card": "#e4f0ef",
    "card_alt": "#e8e9f6",
    "raised": "#dcebf3",
    "field": "#f1f0f8",
    "ink": "#17233c",
    "muted": "#475569",
    "border": "#91a8bf",
    "primary": "#2448b8",
    "primary_hover": "#1e3a8a",
    "cyan": "#075985",
    "green": "#047857",
    "teal": "#0f766e",
    "violet": "#6d28d9",
    "amber": "#92400e",
    "orange": "#9a3412",
    "red": "#b91c1c",
}

SIDEBAR = {
    "background": ("#142640", "#0f172a"),
    "text": ("#eaf3ff", "#e2e8f0"),
    "muted": ("#c5d7ed", "#cbd5e1"),
    "hover": ("#254567", "#1e3a5f"),
    "active": ("#315ee4", "#0284c7"),
}

LIGHT_TEXT = {
    "#38bdf8": LIGHT["cyan"],
    "#0284c7": LIGHT["primary"],
    "#34d399": LIGHT["green"],
    "#10b981": LIGHT["green"],
    "#059669": LIGHT["green"],
    "#f43f5e": LIGHT["red"],
    "#ef4444": LIGHT["red"],
    "#fbbf24": LIGHT["amber"],
    "#f59e0b": LIGHT["amber"],
    "#a78bfa": LIGHT["violet"],
    "#7c3aed": LIGHT["violet"],
    "#d97706": LIGHT["amber"],
    "gray": LIGHT["muted"],
    "gray50": LIGHT["muted"],
    "gray60": LIGHT["muted"],
    "gray70": LIGHT["muted"],
    "gray80": LIGHT["muted"],
}

LIGHT_BACKGROUNDS = {
    "gray92": LIGHT["background"],
    "gray86": LIGHT["panel"],
    "gray81": LIGHT["panel"],
    "gray85": LIGHT["panel"],
    "#f1f5f9": LIGHT["background"],
    "#f8fafc": LIGHT["raised"],
    "#ffffff": LIGHT["card"],
}

LIGHT_BUTTONS = {
    "#0284c7": LIGHT["primary"],
    "#0369a1": LIGHT["primary"],
    "#38bdf8": LIGHT["primary"],
    "#3b8ed0": LIGHT["primary"],
    "#1d4ed8": LIGHT["primary"],
    "#059669": LIGHT["green"],
    "#10b981": LIGHT["green"],
    "#34d399": LIGHT["green"],
    "#0d9488": LIGHT["teal"],
    "#0f766e": LIGHT["teal"],
    "#7c3aed": LIGHT["violet"],
    "#ea580c": LIGHT["orange"],
    "#d97706": LIGHT["amber"],
    "#ef4444": LIGHT["red"],
    "#475569": "#334155",
}

LIGHT_HOVERS = {
    "#0369a1": LIGHT["primary_hover"],
    "#075985": LIGHT["primary_hover"],
    "#0284c7": LIGHT["primary_hover"],
    "#047857": "#065f46",
    "#059669": "#065f46",
    "#0f766e": "#115e59",
    "#334155": "#1e293b",
    "#b91c1c": "#991b1b",
}


def card_style(color: str) -> tuple[str, str, str, str, str]:
    """Devuelve título y estados del botón de una tarjeta en ambos temas."""
    title_dark = {
        "#1d4ed8": "#93c5fd", "#7c3aed": "#c4b5fd", "#0d9488": "#5eead4",
        "#b45309": "#fcd34d", "#0891b2": "#67e8f9", "#0f766e": "#6ee7b7",
    }.get(color, "#e2e8f0")
    title_light = {
        "#1d4ed8": LIGHT["primary"], "#7c3aed": LIGHT["violet"],
        "#0d9488": LIGHT["teal"], "#b45309": LIGHT["amber"],
        "#0891b2": LIGHT["cyan"], "#0f766e": LIGHT["teal"],
    }.get(color, LIGHT["ink"])
    button_dark = {"#0d9488": "#0f766e", "#0891b2": "#0e7490"}.get(color, color)
    hover_light = {
        LIGHT["primary"]: LIGHT["primary_hover"], LIGHT["violet"]: "#5b21b6",
        LIGHT["teal"]: "#115e59", LIGHT["amber"]: "#78350f",
        LIGHT["cyan"]: "#0c4a6e",
    }.get(title_light, LIGHT["primary_hover"])
    hover_dark = {
        "#1d4ed8": "#1e40af", "#7c3aed": "#6d28d9", "#0f766e": "#115e59",
        "#b45309": "#92400e", "#0e7490": "#155e75",
    }.get(button_dark, button_dark)
    return title_light, title_dark, button_dark, hover_light, hover_dark


def dashboard_card_surface(color: str) -> str:
    """Da variedad suave a las tarjetas del inicio sin perder la jerarquía."""
    return {
        "#1d4ed8": "#e3ebf8",
        "#7c3aed": "#eae8f7",
        "#0d9488": "#dfeeea",
        "#b45309": "#f2eadb",
        "#0891b2": "#e0edf3",
        "#0f766e": "#e2efe6",
    }.get(color, LIGHT["card"])


def configure_light_defaults() -> None:
    """Define los colores Light de los controles que usan el tema base."""
    defaults = {
        "CTk": {"fg_color": LIGHT["background"]},
        "CTkFrame": {"fg_color": LIGHT["panel"], "top_fg_color": LIGHT["raised"],
                     "border_color": LIGHT["border"]},
        "CTkLabel": {"text_color": LIGHT["ink"]},
        "CTkButton": {"fg_color": LIGHT["primary"], "hover_color": LIGHT["primary_hover"],
                      "text_color": "#ffffff"},
        "CTkSegmentedButton": {
            "fg_color": "#e2e9f4", "selected_color": LIGHT["primary"],
            "selected_hover_color": LIGHT["primary_hover"],
            "unselected_color": "#334155", "unselected_hover_color": "#1e293b",
            "text_color": "#ffffff",
        },
        "CTkOptionMenu": {
            "fg_color": LIGHT["primary"], "button_color": LIGHT["primary_hover"],
            "button_hover_color": "#172f74", "text_color": "#ffffff",
        },
        "CTkEntry": {"fg_color": LIGHT["field"], "border_color": LIGHT["border"],
                     "text_color": LIGHT["ink"], "placeholder_text_color": LIGHT["muted"]},
        "CTkTextbox": {"fg_color": LIGHT["card_alt"], "text_color": LIGHT["ink"]},
        "CTkCheckBox": {"fg_color": LIGHT["primary"], "hover_color": LIGHT["primary_hover"],
                        "text_color": LIGHT["ink"]},
        "CTkTabview": {"fg_color": LIGHT["panel"]},
        "CTkScrollbar": {"button_color": "#94a8c3", "button_hover_color": "#617997"},
    }
    for widget, options in defaults.items():
        theme = ThemeManager.theme.get(widget, {})
        for option, light in options.items():
            original = theme.get(option)
            if isinstance(original, list) and len(original) == 2:
                original[0] = light


def _light_value(value: str | tuple[str, str] | list[str], palette: dict[str, str]) -> str | tuple[str, str]:
    if isinstance(value, (tuple, list)):
        first = palette.get(value[0].lower(), value[0])
        return (first, value[1])
    if isinstance(value, str):
        return palette.get(value.lower(), value)
    return value


def _parent_surface(widget: ctk.CTkBaseClass | ctk.CTkScrollableFrame) -> str | None:
    parent = widget.master
    while parent is not None:
        if isinstance(parent, (ctk.CTkBaseClass, ctk.CTkScrollableFrame)):
            color = parent.cget("fg_color")
            if color != "transparent":
                return color[0] if isinstance(color, (tuple, list)) else color
        parent = parent.master
    return None


def apply_light_palette(root: ctk.CTkBaseClass, light: bool) -> None:
    """Aplica Light y restaura los colores originales al volver a Dark."""
    widgets = [root]
    while widgets:
        widget = widgets.pop()
        widgets.extend(widget.winfo_children())
        if not isinstance(widget, (ctk.CTkBaseClass, ctk.CTkScrollableFrame)):
            continue
        saved = getattr(widget, "_pymatrix_original_colors", None)
        if not light:
            if saved:
                widget.configure(**saved)
                del widget._pymatrix_original_colors
            continue
        if saved:
            continue
        palettes = {}
        if isinstance(widget, ctk.CTkScrollableFrame) and widget.cget("fg_color") == "transparent":
            surface = _parent_surface(widget)
            if surface is not None:
                palettes["fg_color"] = {"transparent": surface}
        elif isinstance(widget, ctk.CTkLabel):
            palettes["text_color"] = LIGHT_TEXT
        elif isinstance(widget, ctk.CTkButton):
            palettes["fg_color"] = LIGHT_BUTTONS
            palettes["hover_color"] = LIGHT_HOVERS
        elif isinstance(widget, ctk.CTkEntry):
            palettes["fg_color"] = {"#ffffff": LIGHT["field"]}
        elif isinstance(widget, (ctk.CTkFrame, ctk.CTkScrollableFrame, ctk.CTkTabview, ctk.CTkTextbox)):
            palettes["fg_color"] = LIGHT_BACKGROUNDS

        originals = {}
        updates = {}
        for option, palette in palettes.items():
            original = widget.cget(option)
            updated = _light_value(original, palette)
            if updated != original:
                originals[option] = original
                updates[option] = updated
        if updates:
            widget.configure(**updates)
            widget._pymatrix_original_colors = originals

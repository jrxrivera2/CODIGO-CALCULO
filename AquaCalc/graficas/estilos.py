"""Estilo visual compartido para las gráficas de Matplotlib."""

from matplotlib.figure import Figure

COLORES = {
    "constante": "#1F6F8B",
    "racional": "#E07A3D",
    "acento": "#0B6E4F",
    "secundario": "#5B8E7D",
    "fondo": "#F7FBFC",
    "rejilla": "#D5E3EA",
    "texto": "#1C2B33",
    "gota1": "#1565C0",
    "gota2": "#00838F",
    "gota3": "#2E7D32",
    "gota5": "#C62828",
}


def aplicar_estilo(figura: Figure) -> None:
    """Aplica un aspecto limpio y profesional a una figura."""
    figura.patch.set_facecolor(COLORES["fondo"])
    for eje in figura.get_axes():
        eje.set_facecolor("white")
        eje.grid(True, linestyle="--", linewidth=0.7, color=COLORES["rejilla"], alpha=0.9)
        eje.spines["top"].set_visible(False)
        eje.spines["right"].set_visible(False)
        eje.tick_params(colors=COLORES["texto"])
        eje.xaxis.label.set_color(COLORES["texto"])
        eje.yaxis.label.set_color(COLORES["texto"])
        eje.title.set_color(COLORES["texto"])
        leyenda = eje.get_legend()
        if leyenda is not None:
            leyenda.get_frame().set_facecolor("white")
            leyenda.get_frame().set_edgecolor(COLORES["rejilla"])

"""Punto de entrada de AquaCalc."""

from __future__ import annotations

import sys
from pathlib import Path

# Permite ejecutar el programa desde cualquier directorio de trabajo.
RAIZ = Path(__file__).resolve().parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import matplotlib

matplotlib.use("TkAgg")

from interfaz.ventana_principal import VentanaPrincipal


def main() -> None:
    aplicacion = VentanaPrincipal()
    aplicacion.mainloop()


if __name__ == "__main__":
    main()

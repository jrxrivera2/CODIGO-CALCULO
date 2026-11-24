"""Exportación a CSV, PNG y PDF a partir del estado de cálculo actual."""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure

from calculos.constantes import TIEMPOS_COMPARACION
from calculos.modelo_constante import ModeloConstante
from calculos.modelo_racional import ModeloRacional
from calculos.validacion_numerica import InformeValidacion
from graficas.graficas_modelos import GraficadorModelos


class GeneradorReportes:
    """Genera archivos de salida a partir de los modelos actuales."""

    def __init__(
        self,
        constante: ModeloConstante,
        racional: ModeloRacional,
        r: float,
        v: float,
        informe: InformeValidacion,
    ):
        self.constante = constante
        self.racional = racional
        self.r = r
        self.v = v
        self.informe = informe
        self.graficador = GraficadorModelos(constante, racional)

    def filas_comparacion(self) -> list[dict]:
        filas = []
        for etiqueta, T in TIEMPOS_COMPARACION.items():
            filas.append(
                {
                    "tiempo": etiqueta,
                    "segundos": T,
                    "constante_L": self.constante.volumen_litros(T),
                    "racional_L": self.racional.volumen_litros(T),
                }
            )
        filas.append(
            {
                "tiempo": "Infinito",
                "segundos": "",
                "constante_L": "Diverge" if self.constante.A > 0 else 0.0,
                "racional_L": self.racional.volumen_infinito_litros(),
            }
        )
        return filas

    def exportar_csv(self, ruta: str) -> None:
        with open(ruta, "w", newline="", encoding="utf-8") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(["AquaCalc – Calculadora de Desperdicio de Agua"])
            escritor.writerow(["Fecha", datetime.now().strftime("%Y-%m-%d %H:%M")])
            escritor.writerow([])
            escritor.writerow(["Parámetros"])
            escritor.writerow(["Frecuencia r (gotas/s)", self.r])
            escritor.writerow(["Volumen de gota v (ml)", self.v])
            escritor.writerow(["Tasa A (ml/s)", self.constante.A])
            escritor.writerow(["a (1/s)", self.racional.a])
            escritor.writerow(["b (1/s)", self.racional.b])
            escritor.writerow([])
            escritor.writerow(["Tiempo", "Modelo constante (L)", "Modelo racional (L)"])
            for fila in self.filas_comparacion():
                c = fila["constante_L"]
                if isinstance(c, float):
                    c = f"{c:.6f}"
                r = fila["racional_L"]
                if isinstance(r, float):
                    r = f"{r:.6f}"
                escritor.writerow([fila["tiempo"], c, r])
            escritor.writerow([])
            impropia = self.racional.integral_impropia()
            escritor.writerow(["Integral impropia constante", "Diverge" if self.constante.A > 0 else "0"])
            escritor.writerow(["Integral impropia racional (ml)", f"{impropia.volumen_infinito_ml:.6f}"])
            escritor.writerow(["Integral impropia racional (L)", f"{impropia.volumen_infinito_L:.6f}"])

    def guardar_graficas_png(self, carpeta: str) -> list[str]:
        destino = Path(carpeta)
        destino.mkdir(parents=True, exist_ok=True)
        rutas = []
        tareas = [
            ("grafica1_gota_por_segundo.png", self.graficador.grafica_goteo_24h),
            ("grafica2_frecuencias.png", self.graficador.grafica_frecuencias),
            ("grafica3_integrales_parciales.png", self.graficador.grafica_integrales_parciales),
            ("grafica4_comparacion.png", self.graficador.grafica_comparacion),
        ]
        for nombre, dibujar in tareas:
            figura = Figure(figsize=(9.5, 5.2), dpi=120)
            dibujar(figura)
            ruta = destino / nombre
            self.graficador.guardar_png(figura, str(ruta))
            rutas.append(str(ruta))
        return rutas

    def exportar_pdf(self, ruta: str) -> None:
        """PDF con parámetros, tablas, validación, conclusión y gráficas."""
        with PdfPages(ruta) as pdf:
            self._pagina_portada(pdf)
            self._pagina_resultados(pdf)
            for dibujar, titulo in (
                (self.graficador.grafica_goteo_24h, "Gráfica 1"),
                (self.graficador.grafica_frecuencias, "Gráfica 2"),
                (self.graficador.grafica_integrales_parciales, "Gráfica 3"),
                (self.graficador.grafica_comparacion, "Gráfica 4"),
                (self.graficador.grafica_analisis_impropia, "Análisis de integrales impropias"),
            ):
                figura = Figure(figsize=(11, 8.5), dpi=120)
                dibujar(figura)
                figura.suptitle(titulo, y=0.98, fontsize=12)
                pdf.savefig(figura, bbox_inches="tight")

    def _pagina_portada(self, pdf: PdfPages) -> None:
        figura = Figure(figsize=(11, 8.5), dpi=120)
        figura.patch.set_facecolor("#F7FBFC")
        eje = figura.add_subplot(111)
        eje.axis("off")
        texto = (
            "AquaCalc – Calculadora de Desperdicio de Agua\n\n"
            "Reporte de análisis mediante integrales definidas e impropias\n"
            f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
            "Parámetros utilizados\n"
            f"  • Frecuencia de goteo r = {self.r:g} gotas/s\n"
            f"  • Volumen de gota v = {self.v:g} ml\n"
            f"  • Tasa A = r × v = {self.constante.A:.8g} ml/s\n"
            f"  • Constante a = {self.racional.a:.8g} s⁻¹\n"
            f"  • Constante b = {self.racional.b:.8g} s⁻¹\n\n"
            "Modelos\n"
            "  1. Tasa constante: q(t) = A\n"
            "  2. Tasa racional: q(t) = A / [(1 + at)(1 + bt)]\n"
        )
        eje.text(0.06, 0.94, texto, va="top", ha="left", fontsize=12, family="DejaVu Sans")
        pdf.savefig(figura)

    def _pagina_resultados(self, pdf: PdfPages) -> None:
        figura = Figure(figsize=(11, 8.5), dpi=120)
        figura.patch.set_facecolor("#F7FBFC")
        eje = figura.add_subplot(111)
        eje.axis("off")
        lineas = ["Comparación entre modelos\n"]
        lineas.append(f"{'Tiempo':<14}{'Constante (L)':>18}{'Racional (L)':>18}")
        for fila in self.filas_comparacion():
            c = fila["constante_L"]
            r = fila["racional_L"]
            c_txt = f"{c:.4f}" if isinstance(c, float) else str(c)
            r_txt = f"{r:.4f}" if isinstance(r, float) else str(r)
            lineas.append(f"{fila['tiempo']:<14}{c_txt:>18}{r_txt:>18}")

        imp_c = self.constante.integral_impropia()
        imp_r = self.racional.integral_impropia()
        lineas.append("\nIntegrales impropias")
        lineas.append(f"  Constante: {imp_c.limite_descripcion}  ({'diverge' if imp_c.diverge else 'converge'})")
        lineas.append(
            f"  Racional: V(∞) = {imp_r.volumen_infinito_ml:.4f} ml "
            f"= {imp_r.volumen_infinito_L:.4f} L  (converge)"
        )
        lineas.append(f"  Expresión analítica: {imp_r.expresion}")

        lineas.append("\nValidación numérica")
        for comp in self.informe.comparaciones:
            estado = "OK" if comp.coincide else "ADVERTENCIA"
            err = "" if comp.error_relativo is None else f"  err. rel. = {comp.error_relativo:.3e}"
            lineas.append(f"  [{estado}] {comp.nombre}{err}")
        if self.informe.advertencias:
            lineas.append("\nAdvertencias:")
            for adv in self.informe.advertencias:
                lineas.append(f"  • {adv}")

        lineas.append("\nConclusión")
        lineas.append(
            "El modelo de tasa constante produce una integral impropia divergente\n"
            "cuando A > 0: el desperdicio crece sin cota si la fuga no se repara.\n"
            "El modelo racional decreciente produce una integral convergente;\n"
            "el volumen se aproxima a un máximo finito V(∞) = [A/(a−b)] ln(a/b)."
        )
        eje.text(
            0.05,
            0.96,
            "\n".join(lineas),
            va="top",
            ha="left",
            fontsize=10,
            family="DejaVu Sans",
        )
        pdf.savefig(figura)

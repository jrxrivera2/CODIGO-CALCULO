"""Resultados, validación numérica y exportación de reportes."""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from graficas.graficas_modelos import GraficadorModelos
from interfaz.componentes import PanelGrafica, fmt, tarjeta
from interfaz.estado import AppState
from reportes.generador_reportes import GeneradorReportes


class VistaResultados(ttk.Frame):
    def __init__(self, padre, estado: AppState):
        super().__init__(padre)
        self.estado = estado
        self.graficas: dict[str, PanelGrafica] = {}
        self.tabla_val = None
        self.aviso = tk.StringVar()
        self._construir()
        estado.suscribir(self.refrescar)
        self.refrescar()

    def _construir(self) -> None:
        ttk.Label(self, text="Resultados y reportes", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(
            self,
            text="Validación analítica frente a scipy.integrate.quad y exportación de resultados.",
            style="Subtitulo.TLabel",
        ).pack(anchor="w", pady=(0, 8))

        acciones = tarjeta(self, "Exportación")
        fila = ttk.Frame(acciones, style="Card.TFrame")
        ttk.Button(fila, text="Exportar CSV", style="Acento.TButton", command=self.exportar_csv).pack(
            side="left", padx=4
        )
        ttk.Button(fila, text="Generar reporte PDF", style="Acento.TButton", command=self.exportar_pdf).pack(
            side="left", padx=4
        )
        ttk.Button(fila, text="Guardar gráficas PNG", command=self.exportar_png).pack(
            side="left", padx=4
        )
        ttk.Button(fila, text="Recalcular validación", command=self.refrescar).pack(
            side="left", padx=4
        )
        fila.pack(anchor="w")
        acciones.pack(fill="x", pady=6)

        val = tarjeta(self, "Validación matemática y numérica")
        ttk.Label(val, textvariable=self.aviso, style="Card.TLabel", wraplength=860).pack(anchor="w")
        columnas = ("nombre", "analitico", "numerico", "error", "estado")
        self.tabla_val = ttk.Treeview(val, columns=columnas, show="headings", height=7)
        encabezados = {
            "nombre": "Comprobación",
            "analitico": "Analítico",
            "numerico": "Numérico",
            "error": "Error relativo",
            "estado": "¿Coincide?",
        }
        anchos = {"nombre": 280, "analitico": 140, "numerico": 140, "error": 140, "estado": 100}
        for col in columnas:
            self.tabla_val.heading(col, text=encabezados[col])
            self.tabla_val.column(col, width=anchos[col], anchor="center")
        self.tabla_val.pack(fill="x", pady=8)
        val.pack(fill="x", pady=6)

        titulos = [
            ("g1", "Gráfica 1. Desperdicio acumulado para una gota por segundo (24 h)"),
            ("g2", "Gráfica 2. Comparación según la frecuencia de goteo"),
            ("g3", "Gráfica 3. Integral parcial cuando el tiempo aumenta"),
            ("g4", "Gráfica 4. Comparación entre tasa constante y tasa racional"),
        ]
        for clave, titulo in titulos:
            card = tarjeta(self, titulo)
            panel = PanelGrafica(card, figsize=(8.4, 3.8), con_toolbar=False)
            panel.pack(fill="both", expand=True)
            self.graficas[clave] = panel
            card.pack(fill="both", expand=True, pady=6)

    def _generador(self) -> GeneradorReportes:
        informe = self.estado.validar()
        return GeneradorReportes(
            self.estado.modelo_constante(),
            self.estado.modelo_racional(),
            self.estado.r,
            self.estado.v,
            informe,
        )

    def refrescar(self) -> None:
        informe = self.estado.validar()
        for item in self.tabla_val.get_children():
            self.tabla_val.delete(item)
        for comp in informe.comparaciones:
            analitico = "∞" if comp.analitico == float("inf") else fmt(comp.analitico, 6)
            numerico = "—" if comp.numerico is None else fmt(comp.numerico, 6)
            error = "—" if comp.error_relativo is None else f"{comp.error_relativo:.3e}"
            self.tabla_val.insert(
                "",
                "end",
                values=(
                    comp.nombre,
                    analitico,
                    numerico,
                    error,
                    "Sí" if comp.coincide else "No",
                ),
            )
        if informe.todo_correcto:
            self.aviso.set(
                "Las fórmulas analíticas, la integración numérica (intervalos finitos) y el "
                "límite analítico coinciden dentro de la tolerancia."
            )
        else:
            self.aviso.set("Advertencia: " + " ".join(informe.advertencias))

        graficador = GraficadorModelos(
            self.estado.modelo_constante(), self.estado.modelo_racional()
        )
        self.graficas["g1"].redibujar(graficador.grafica_goteo_24h)
        self.graficas["g2"].redibujar(graficador.grafica_frecuencias)
        self.graficas["g3"].redibujar(graficador.grafica_integrales_parciales)
        self.graficas["g4"].redibujar(graficador.grafica_comparacion)

    def exportar_csv(self) -> None:
        ruta = filedialog.asksaveasfilename(
            title="Guardar CSV",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
        )
        if not ruta:
            return
        try:
            self._generador().exportar_csv(ruta)
            messagebox.showinfo("Exportación", f"CSV guardado en:\n{ruta}")
        except OSError as error:
            messagebox.showerror("Error al guardar", str(error))

    def exportar_pdf(self) -> None:
        ruta = filedialog.asksaveasfilename(
            title="Guardar reporte PDF",
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
        )
        if not ruta:
            return
        try:
            self._generador().exportar_pdf(ruta)
            messagebox.showinfo("Exportación", f"PDF guardado en:\n{ruta}")
        except Exception as error:  # noqa: BLE001
            messagebox.showerror("Error al generar el PDF", str(error))

    def exportar_png(self) -> None:
        carpeta = filedialog.askdirectory(title="Carpeta para las imágenes PNG")
        if not carpeta:
            return
        try:
            rutas = self._generador().guardar_graficas_png(carpeta)
            messagebox.showinfo(
                "Exportación",
                "Se guardaron las siguientes imágenes:\n" + "\n".join(rutas),
            )
        except OSError as error:
            messagebox.showerror("Error al guardar", str(error))

"""Pruebas matemáticas de los modelos constante y racional."""

from __future__ import annotations

import math
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import matplotlib

matplotlib.use("Agg")

from calculos.constantes import (
    A_PREDETERMINADO,
    A_PREDETERMINADO_S,
    B_PREDETERMINADO_S,
    TIEMPOS_COMPARACION,
    VOLUMEN_GOTA_ML,
)
from calculos.modelo_constante import ModeloConstante
from calculos.modelo_racional import ModeloRacional
from calculos.validacion_numerica import validar_modelos
from calculos.validaciones import ValidacionError, validar_parametros
from reportes.generador_reportes import GeneradorReportes


class TestModeloConstante(unittest.TestCase):
    def setUp(self) -> None:
        self.modelo = ModeloConstante.desde_goteo(1.0, VOLUMEN_GOTA_ML)

    def test_tasa_igual_a_A(self) -> None:
        self.assertAlmostEqual(self.modelo.tasa(0), 0.25)
        self.assertAlmostEqual(self.modelo.tasa(10_000), 0.25)

    def test_volumen_una_hora(self) -> None:
        self.assertAlmostEqual(self.modelo.volumen_litros(3600), 0.9, places=6)

    def test_tabla_tiempos(self) -> None:
        esperados = {
            "1 hora": 0.90,
            "6 horas": 5.40,
            "12 horas": 10.80,
            "24 horas": 21.60,
            "1 semana": 151.20,
        }
        for etiqueta, litros in esperados.items():
            T = TIEMPOS_COMPARACION[etiqueta]
            self.assertAlmostEqual(self.modelo.volumen_litros(T), litros, places=6)

    def test_tiempo_cero(self) -> None:
        self.assertEqual(self.modelo.volumen_ml(0), 0.0)

    def test_frecuencia_cero(self) -> None:
        nulo = ModeloConstante.desde_goteo(0.0, 0.25)
        self.assertEqual(nulo.volumen_ml(86400), 0.0)
        self.assertFalse(nulo.integral_impropia().diverge)

    def test_impropia_diverge(self) -> None:
        resultado = self.modelo.integral_impropia()
        self.assertTrue(resultado.diverge)
        self.assertIn("divergente", resultado.mensaje.lower())


class TestModeloRacional(unittest.TestCase):
    def setUp(self) -> None:
        self.modelo = ModeloRacional(
            A_PREDETERMINADO, A_PREDETERMINADO_S, B_PREDETERMINADO_S
        )

    def test_fracciones_parciales(self) -> None:
        fp = self.modelo.fracciones_parciales()
        self.assertAlmostEqual(fp.P, 6.0 / 23.0, places=12)
        self.assertAlmostEqual(fp.Q, -0.25 / 23.0, places=12)
        self.assertAlmostEqual(fp.P + fp.Q, self.modelo.A, places=12)
        self.assertLess(self.modelo.verificar_descomposicion(3600), 1e-12)

    def test_volumen_infinito_referencia(self) -> None:
        ml = self.modelo.volumen_infinito_ml()
        self.assertAlmostEqual(ml, 2984.61, delta=0.02)
        self.assertAlmostEqual(self.modelo.volumen_infinito_litros(), 2.985, delta=0.001)

    def test_tabla_tiempos(self) -> None:
        esperados = {
            "1 hora": 0.61,
            "6 horas": 1.62,
            "12 horas": 2.03,
            "24 horas": 2.37,
            "1 semana": 2.86,
        }
        for etiqueta, litros in esperados.items():
            T = TIEMPOS_COMPARACION[etiqueta]
            self.assertAlmostEqual(
                self.modelo.volumen_litros(T), litros, delta=0.015, msg=etiqueta
            )

    def test_impropia_converge(self) -> None:
        resultado = self.modelo.integral_impropia()
        self.assertTrue(resultado.converge)
        self.assertIn("convergente", resultado.mensaje.lower())
        # El límite analítico debe coincidir con un T enorme, sin integrar hasta inf.
        self.assertAlmostEqual(
            self.modelo.volumen_ml(1e12),
            resultado.volumen_infinito_ml,
            delta=1e-3,
        )

    def test_caso_a_igual_b(self) -> None:
        a = 1.0 / 3600.0
        modelo = ModeloRacional(0.25, a, a)
        self.assertTrue(modelo.factores_iguales)
        self.assertAlmostEqual(modelo.volumen_ml(3600), 0.25 * 3600 / 2.0)
        self.assertAlmostEqual(modelo.volumen_infinito_ml(), 0.25 / a)

    def test_tiempo_cero(self) -> None:
        self.assertEqual(self.modelo.volumen_ml(0), 0.0)


class TestValidaciones(unittest.TestCase):
    def test_negativos(self) -> None:
        with self.assertRaises(ValidacionError):
            validar_parametros(-1, 0.25)
        with self.assertRaises(ValidacionError):
            ModeloConstante(-0.1)

    def test_vacios(self) -> None:
        with self.assertRaises(ValidacionError):
            validar_parametros("", 0.25)
        with self.assertRaises(ValidacionError):
            validar_parametros("  ", 0.25)

    def test_no_numerico(self) -> None:
        with self.assertRaises(ValidacionError):
            validar_parametros("abc", 0.25)

    def test_a_b_no_positivos(self) -> None:
        with self.assertRaises(ValidacionError):
            ModeloRacional(0.25, 0, 1 / 86400)
        with self.assertRaises(ValidacionError):
            ModeloRacional(0.25, 1 / 3600, -1)

    def test_coma_decimal(self) -> None:
        datos = validar_parametros("1,5", "0,25")
        self.assertAlmostEqual(datos["A"], 0.375)

    def test_valores_extremos(self) -> None:
        with self.assertRaises(ValidacionError):
            validar_parametros(float("inf"), 0.25)


class TestValidacionNumerica(unittest.TestCase):
    def test_informe_predeterminado(self) -> None:
        cte = ModeloConstante(A_PREDETERMINADO)
        rac = ModeloRacional(A_PREDETERMINADO, A_PREDETERMINADO_S, B_PREDETERMINADO_S)
        informe = validar_modelos(cte, rac, T=3600.0)
        self.assertTrue(informe.todo_correcto, informe.advertencias)
        for comp in informe.comparaciones:
            self.assertTrue(comp.coincide, comp)


class TestReportes(unittest.TestCase):
    def test_csv_y_pdf(self) -> None:
        cte = ModeloConstante(A_PREDETERMINADO)
        rac = ModeloRacional(A_PREDETERMINADO, A_PREDETERMINADO_S, B_PREDETERMINADO_S)
        informe = validar_modelos(cte, rac, T=3600.0)
        gen = GeneradorReportes(cte, rac, 1.0, VOLUMEN_GOTA_ML, informe)
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "salida.csv"
            pdf_path = Path(tmp) / "reporte.pdf"
            gen.exportar_csv(str(csv_path))
            gen.exportar_pdf(str(pdf_path))
            pngs = gen.guardar_graficas_png(tmp)
            self.assertTrue(csv_path.exists() and csv_path.stat().st_size > 0)
            self.assertTrue(pdf_path.exists() and pdf_path.stat().st_size > 0)
            self.assertEqual(len(pngs), 4)
            texto = csv_path.read_text(encoding="utf-8")
            self.assertIn("Infinito", texto)


if __name__ == "__main__":
    unittest.main(verbosity=2)

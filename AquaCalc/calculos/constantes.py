"""Constantes físicas y valores predeterminados del proyecto."""

# Volumen de referencia de una gota de agua (ml).
VOLUMEN_GOTA_ML = 0.25

# Tasa inicial predeterminada: 1 gota/s × 0,25 ml/gota.
A_PREDETERMINADO = VOLUMEN_GOTA_ML

# Escala de atenuación rápida: una hora (s^-1).
A_PREDETERMINADO_S = 1.0 / 3600.0

# Escala de atenuación lenta: un día (s^-1).
B_PREDETERMINADO_S = 1.0 / 86400.0

# Factores de conversión de tiempo a segundos.
UNIDADES_TIEMPO = {
    "segundos": 1.0,
    "minutos": 60.0,
    "horas": 3600.0,
    "días": 86400.0,
}

ML_POR_LITRO = 1000.0

# Tiempos de comparación (segundos).
TIEMPOS_COMPARACION = {
    "1 hora": 3600.0,
    "6 horas": 6 * 3600.0,
    "12 horas": 12 * 3600.0,
    "24 horas": 24 * 3600.0,
    "1 semana": 7 * 86400.0,
}

# Tolerancia relativa para validaciones numéricas.
TOLERANCIA_RELATIVA = 1e-6

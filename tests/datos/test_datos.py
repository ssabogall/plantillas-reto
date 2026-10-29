"""Pruebas de calidad de datos sobre turnos_hoy.csv (no dependen del back ni del front).

Uso (desde la raiz del repo):
    pytest tests/datos/test_datos.py -v
Si el CSV esta en otra ruta:
    $env:CSV_TURNOS = "ruta\\turnos_hoy.csv"; pytest tests/datos/test_datos.py -v
"""
import csv
import os
from collections import Counter

import pytest

RUTA = os.getenv("CSV_TURNOS", "turnos_hoy.csv")
COLUMNAS = {"numero", "hora_solicitud", "hora_atencion", "estado"}
ESTADOS = {"pendiente", "atendido", "cancelado"}


def a_minutos(valor):
    valor = (valor or "").strip()
    if not valor:
        return None
    if ":" in valor:
        h, m = valor.split(":")[:2]
        return int(h) * 60 + int(m)
    return round(float(valor) * 1440)  # hora como fraccion del dia (formato Excel)


@pytest.fixture(scope="module")
def filas():
    if not os.path.exists(RUTA):
        pytest.skip(f"No se encontro {RUTA}")
    with open(RUTA, newline="", encoding="utf-8-sig") as f:
        muestra = f.read(2048)
        f.seek(0)
        dialecto = csv.Sniffer().sniff(muestra, delimiters=",;")
        datos = list(csv.DictReader(f, dialect=dialecto))
    for d in datos:
        d["estado"] = d["estado"].strip().lower()
        d["min_sol"] = a_minutos(d["hora_solicitud"])
        d["min_at"] = a_minutos(d["hora_atencion"])
        d["numero"] = int(float(d["numero"]))
    return datos


def test_dat_01_columnas_esperadas(filas):
    assert COLUMNAS.issubset(filas[0].keys())


def test_dat_02_cantidad_de_registros(filas):
    assert len(filas) == 11


def test_dat_03_estados_validos(filas):
    assert {f["estado"] for f in filas} <= ESTADOS


def test_dat_04_todos_tienen_hora_solicitud(filas):
    assert all(f["min_sol"] is not None for f in filas)


def test_dat_05_atendidos_tienen_hora_atencion(filas):
    assert all(f["min_at"] is not None for f in filas if f["estado"] == "atendido")


def test_dat_06_pendientes_sin_hora_atencion(filas):
    assert all(f["min_at"] is None for f in filas if f["estado"] == "pendiente")


def test_dat_07_atencion_no_antes_de_solicitud(filas):
    assert all(f["min_at"] >= f["min_sol"] for f in filas if f["min_at"] is not None)


def test_dat_08_hallazgo_numero_duplicado(filas):
    """Hallazgo documentado: el 7 se repite (uno cancelado y otro pendiente)."""
    duplicados = [n for n, c in Counter(f["numero"] for f in filas).items() if c > 1]
    assert duplicados == [7]
    estados_7 = sorted(f["estado"] for f in filas if f["numero"] == 7)
    assert estados_7 == ["cancelado", "pendiente"]


def test_dat_09_hallazgo_archivo_no_ordenado(filas):
    """Hallazgo documentado: el archivo no viene en orden de llegada."""
    horas = [f["min_sol"] for f in filas]
    assert horas != sorted(horas)


def test_dat_10_orden_de_llegada_esperado(filas):
    pendientes = sorted((f for f in filas if f["estado"] == "pendiente"), key=lambda f: f["min_sol"])
    assert [f["numero"] for f in pendientes] == [6, 7, 8, 9, 10]


def test_dat_11_espera_promedio_esperada(filas):
    esperas = [f["min_at"] - f["min_sol"] for f in filas if f["estado"] == "atendido"]
    assert round(sum(esperas) / len(esperas), 1) == 12.2


def test_dat_12_proximo_numero_es_11(filas):
    assert max(f["numero"] for f in filas) + 1 == 11

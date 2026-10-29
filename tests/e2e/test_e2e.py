"""Pruebas end-to-end con Selenium sobre la pantalla del front.

Ejecutar (con back y front corriendo y el back recien reiniciado):
    pytest tests/e2e/test_e2e.py -v --html=tests/e2e/reporte-e2e.html --self-contained-html

Si el front corre en otra URL:  $env:FRONT_URL = "http://localhost:4200"
Ajustar los SELECTORES con los ids reales que defina el front.
"""
import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select

URL = os.getenv("FRONT_URL", "http://localhost:4200")

# ---------------- Selectores (confirmar con Ruben) ----------------
CAMPO_NOMBRE = (By.XPATH, "//input[@id='nombre' or @name='nombre' or @formcontrolname='nombre']")
CAMPO_SERVICIO = (By.XPATH, "//select[@id='servicio' or @name='servicio' or @formcontrolname='servicio']")
BOTON_OBTENER = (By.XPATH, "//button[contains(normalize-space(.), 'Obtener mi turno')]")
SERVICIOS = ["Atención general", "Pagos y consultas", "Información"]
# Vista del asesor: pendiente de que el front defina los ids
BOTON_LLAMAR = (By.XPATH, "//button[contains(normalize-space(.), 'Llamar')]")
VISTA_ASESOR = os.getenv("ASESOR_URL", URL)


@pytest.fixture(scope="module")
def driver():
    d = webdriver.Chrome()
    yield d
    d.quit()


def texto_pagina(driver):
    return driver.find_element(By.TAG_NAME, "body").text


def abrir(driver, url=URL):
    driver.get(url)
    WebDriverWait(driver, 10).until(lambda d: d.execute_script("return document.readyState") == "complete")


def pedir_turno(driver, nombre, servicio):
    campo = driver.find_element(*CAMPO_NOMBRE)
    campo.clear()
    campo.send_keys(nombre)
    Select(driver.find_element(*CAMPO_SERVICIO)).select_by_visible_text(servicio)
    driver.find_element(*BOTON_OBTENER).click()


# ---------------- Cliente ----------------

def test_e2e_01_servicios_disponibles(driver):
    """El cliente ve exactamente las 3 opciones de servicio."""
    abrir(driver)
    opciones = [o.text.strip() for o in Select(driver.find_element(*CAMPO_SERVICIO)).options
                if o.get_attribute("value")]
    assert opciones == SERVICIOS


def test_e2e_02_cliente_obtiene_turno(driver):
    """R2: al pedir turno recibe el 11 (maximo + 1) y queda en espera."""
    abrir(driver)
    pedir_turno(driver, "Ana Perez", "Atención general")
    WebDriverWait(driver, 10).until(lambda d: "11" in texto_pagina(d))
    assert "esperando" in texto_pagina(driver).lower()


def test_e2e_03_numero_no_se_repite(driver):
    """R2: un segundo cliente recibe el 12."""
    abrir(driver)
    pedir_turno(driver, "Luis Gomez", "Pagos y consultas")
    WebDriverWait(driver, 10).until(lambda d: "12" in texto_pagina(d))


def test_e2e_04_nombre_obligatorio(driver):
    """El nombre es obligatorio: sin nombre no se registra turno."""
    abrir(driver)
    driver.find_element(*CAMPO_NOMBRE).clear()
    Select(driver.find_element(*CAMPO_SERVICIO)).select_by_visible_text("Información")
    driver.find_element(*BOTON_OBTENER).click()
    time.sleep(1)
    assert "13" not in texto_pagina(driver)


# ---------------- Asesor (activar cuando el front tenga la vista) ----------------

@pytest.mark.skip(reason="Pendiente: ids de la vista del asesor")
def test_e2e_05_asesor_llama_primero_al_6(driver):
    """R1: el asesor llama primero al 6, el primero en llegar."""
    abrir(driver, VISTA_ASESOR)
    driver.find_element(*BOTON_LLAMAR).click()
    WebDriverWait(driver, 10).until(lambda d: "6" in texto_pagina(d))


@pytest.mark.skip(reason="Pendiente: ids de la vista del asesor")
def test_e2e_06_orden_de_llegada_no_de_archivo(driver):
    """R1: el segundo llamado es el 7, no el 9."""
    abrir(driver, VISTA_ASESOR)
    driver.find_element(*BOTON_LLAMAR).click()
    WebDriverWait(driver, 10).until(lambda d: "7" in texto_pagina(d))


@pytest.mark.skip(reason="Pendiente: ids de la vista del asesor")
def test_e2e_07_fila_vacia(driver):
    """R3: con la fila vacia se muestra un aviso y no se llama a nadie."""
    abrir(driver, VISTA_ASESOR)
    for _ in range(20):
        driver.find_element(*BOTON_LLAMAR).click()
        time.sleep(0.4)
        if "no hay personas en espera" in texto_pagina(driver).lower():
            break
    assert "no hay personas en espera" in texto_pagina(driver).lower()

"""Pruebas end-to-end con Selenium sobre el front (Angular, TurnoFacil).

Ejecutar con el front corriendo (ng serve):
    pytest tests/e2e/test_e2e.py -v --html=tests/e2e/reporte-e2e.html --self-contained-html
Otra URL:  $env:FRONT_URL = "http://localhost:4200"

Las pruebas corren en orden sobre la MISMA pagina (no se recarga entre pruebas,
porque el front guarda la fila en memoria).
"""
import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select

URL = os.getenv("FRONT_URL", "http://localhost:4200")
SERVICIOS = ["Atención general", "Pagos y consultas", "Información"]

# Selectores reales del front
NOMBRE = (By.ID, "customerName")
SERVICIO = (By.ID, "service")
OBTENER = (By.XPATH, "//button[contains(normalize-space(.), 'Obtener mi turno')]")
AVISO = (By.CSS_SELECTOR, ".notice")
TAB_ASESOR = (By.XPATH, "//nav//button[contains(normalize-space(.), 'Panel del asesor')]")
LLAMAR = (By.XPATH, "//button[contains(normalize-space(.), 'Llamar siguiente')]")
CONTADOR_FILA = (By.CSS_SELECTOR, ".count-badge")
NUMEROS_FILA = (By.CSS_SELECTOR, ".queue-number")
TURNO_ACTUAL = (By.CSS_SELECTOR, ".big-ticket")
HORA_ACTUAL = (By.CSS_SELECTOR, ".current-meta strong")
PROMEDIO = (By.XPATH, "//article[.//span[contains(., 'Tiempo promedio')]]//div[contains(@class,'stat-value')]")


@pytest.fixture(scope="module")
def driver():
    d = webdriver.Chrome()
    d.get(URL)
    WebDriverWait(d, 15).until(lambda x: x.find_elements(*NOMBRE))
    yield d
    d.quit()


def esperar_aviso(driver, texto):
    WebDriverWait(driver, 10).until(lambda d: texto.lower() in d.find_element(*AVISO).text.lower())
    return driver.find_element(*AVISO).text


def pedir_turno(driver, nombre, servicio):
    campo = driver.find_element(*NOMBRE)
    campo.clear()
    campo.send_keys(nombre)
    Select(driver.find_element(*SERVICIO)).select_by_visible_text(servicio)
    driver.find_element(*OBTENER).click()


# ---------------- Cliente ----------------

def test_e2e_01_servicios_disponibles(driver):
    """El cliente ve exactamente las 3 opciones de servicio."""
    opciones = [o.text.strip() for o in Select(driver.find_element(*SERVICIO)).options]
    assert opciones == SERVICIOS


def test_e2e_02_cliente_obtiene_turno_11(driver):
    """R2: el primer turno nuevo es el 11 (continua desde el 10 de la manana)."""
    pedir_turno(driver, "Ana Perez", "Atención general")
    assert "#11" in esperar_aviso(driver, "tu turno es")


def test_e2e_03_numero_no_se_repite(driver):
    """R2: el siguiente cliente recibe el 12."""
    pedir_turno(driver, "Luis Gomez", "Pagos y consultas")
    assert "#12" in esperar_aviso(driver, "#12")


def test_e2e_04_nombre_obligatorio(driver):
    """Sin nombre no se registra el turno 13."""
    driver.find_element(*NOMBRE).clear()
    driver.find_element(*OBTENER).click()
    time.sleep(1)
    falta = driver.execute_script("return document.getElementById('customerName').validity.valueMissing")
    assert falta, "El campo nombre deberia ser obligatorio"
    assert "#13" not in driver.find_element(By.TAG_NAME, "body").text


# ---------------- Asesor ----------------

def test_e2e_05_fila_en_orden_de_llegada(driver):
    """R1: la fila muestra 7 en espera y empieza por el 6."""
    driver.find_element(*TAB_ASESOR).click()
    WebDriverWait(driver, 10).until(lambda d: d.find_elements(*LLAMAR))
    assert driver.find_element(*CONTADOR_FILA).text.strip() == "7"
    numeros = [e.text.strip() for e in driver.find_elements(*NUMEROS_FILA)]
    assert numeros[:5] == ["6", "7", "8", "9", "10"]


def test_e2e_06_espera_promedio(driver):
    """Requisito: la espera promedio de la manana es 12.2 min."""
    assert driver.find_element(*PROMEDIO).text.startswith("12.2")


def test_e2e_07_llama_primero_al_6(driver):
    """R1: el primer llamado es el turno 6."""
    driver.find_element(*LLAMAR).click()
    assert "#6" in esperar_aviso(driver, "puede pasar")


def test_e2e_08_turno_7_correcto(driver):
    """R1 y datos: el segundo llamado es el 7, el pendiente de las 08:34 (no el cancelado de las 08:30)."""
    driver.find_element(*LLAMAR).click()
    esperar_aviso(driver, "#7")
    assert driver.find_element(*TURNO_ACTUAL).text.strip() == "#7"
    assert driver.find_element(*HORA_ACTUAL).text.strip() == "08:34"


def test_e2e_09_fila_vacia(driver):
    """R3: con la fila vacia no se llama a nadie y se muestra un aviso."""
    for _ in range(20):
        driver.find_element(*LLAMAR).click()
        time.sleep(0.3)
        if "no hay turnos pendientes" in driver.find_element(*AVISO).text.lower():
            break
    assert "no hay turnos pendientes" in driver.find_element(*AVISO).text.lower()

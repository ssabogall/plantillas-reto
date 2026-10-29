import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = "http://localhost:8080"

# ---- Formulario del cliente (ajustar selectores con los ids reales de Ruben) ----
CAMPO_NOMBRE = (By.XPATH, "//input[@id='nombre' or @name='nombre']")
CAMPO_SERVICIO = (By.XPATH, "//select[@id='servicio' or @name='servicio']")
SERVICIOS = ["Atención general", "Pagos y consultas", "Información"]


def boton_obtener_turno(driver):
    return driver.find_element(By.XPATH, "//button[contains(normalize-space(.), 'Obtener mi turno')]")


def llenar_formulario(driver, nombre, servicio):
    from selenium.webdriver.support.ui import Select
    campo = driver.find_element(*CAMPO_NOMBRE)
    campo.clear()
    campo.send_keys(nombre)
    Select(driver.find_element(*CAMPO_SERVICIO)).select_by_visible_text(servicio)



@pytest.fixture(scope="module")
def driver():
    d = webdriver.Chrome()
    yield d
    d.quit()


def abrir(driver):
    driver.get(URL)
    WebDriverWait(driver, 10).until(lambda d: d.find_element(By.ID, "en-espera").text != "-")


def lista(driver):
    return [li.text for li in driver.find_elements(By.CSS_SELECTOR, "#lista li")]


def esperar_texto(driver, id_elemento, texto):
    WebDriverWait(driver, 10).until(EC.text_to_be_present_in_element((By.ID, id_elemento), texto))


def test_e2e_01_pantalla_inicial(driver):
    abrir(driver)
    assert driver.find_element(By.ID, "en-espera").text == "5"
    assert driver.find_element(By.ID, "espera-promedio").text == "12.2"
    assert "Turno 6" in lista(driver)[0]


def test_e2e_02_cancelado_no_se_muestra(driver):
    abrir(driver)
    assert not any("08:30" in item for item in lista(driver))


def test_e2e_03_cliente_pide_turno(driver):
    abrir(driver)
    llenar_formulario(driver, "Ana Perez", "Atención general")
    boton_obtener_turno(driver).click()
    WebDriverWait(driver, 10).until(lambda d: "11" in d.find_element(By.TAG_NAME, "body").text)
    texto = driver.find_element(By.TAG_NAME, "body").text.lower()
    assert "pendiente" in texto


def test_e2e_04_asesor_llama_al_primero(driver):
    abrir(driver)
    driver.find_element(By.ID, "btn-siguiente").click()
    esperar_texto(driver, "llamado", "turno 6")


def test_e2e_05_orden_de_llegada_no_de_archivo(driver):
    abrir(driver)
    driver.find_element(By.ID, "btn-siguiente").click()
    esperar_texto(driver, "llamado", "turno 7")


def test_e2e_06_fila_vacia(driver):
    abrir(driver)
    for _ in range(20):
        driver.find_element(By.ID, "btn-siguiente").click()
        time.sleep(0.4)
        if "vacia" in driver.find_element(By.ID, "error").text.lower():
            break
    assert "vacia" in driver.find_element(By.ID, "error").text.lower()


def test_e2e_07_servicios_disponibles(driver):
    from selenium.webdriver.support.ui import Select
    abrir(driver)
    opciones = [o.text.strip() for o in Select(driver.find_element(*CAMPO_SERVICIO)).options if o.get_attribute("value")]
    assert opciones == SERVICIOS


def test_e2e_08_sin_nombre_no_registra(driver):
    abrir(driver)
    antes = driver.find_element(By.ID, "en-espera").text
    driver.find_element(*CAMPO_NOMBRE).clear()
    boton_obtener_turno(driver).click()
    time.sleep(1)
    assert driver.find_element(By.ID, "en-espera").text == antes

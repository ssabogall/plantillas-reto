import time
from selenium import webdriver

driver = webdriver.Chrome()
driver.get("http://localhost:8000/docs")
time.sleep(2)
print("Titulo:", driver.title)
assert "Swagger UI" in driver.title
driver.quit()
print("SELENIUM OK")

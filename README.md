# TurnoFácil — Sistema de fila virtual

Aplicación para solicitar y administrar turnos de atención sin filas físicas. El repositorio reúne una **demo web funcional**, el **código fuente de una API de turnos**, dos APIs CRUD de ejemplo y pruebas automatizadas.

> **Estado actual:** la interfaz Angular trabaja con datos de demostración en memoria y todavía no consume la API Java de turnos. El código de esa API está en `back/`, pero esa carpeta aún no incluye `pom.xml` ni Maven Wrapper. Las carpetas `api/` y `api-python/` son CRUD de `items`, independientes del sistema de turnos.

## Funcionalidades

- **Cliente:** solicita un turno indicando nombre y servicio, consulta el número asignado y puede cancelar su turno pendiente.
- **Asesor:** visualiza la fila, llama al siguiente, marca el turno actual como atendido y cancela turnos pendientes.
- **Fila:** organiza los turnos por número, muestra cuántas personas esperan y presenta el tiempo promedio de espera.
- **Servicios disponibles en la demo:** Atención general, Pagos y consultas e Información.
- **Datos de inicio:** la demo comienza con turnos de ejemplo del 6 al 10. Los cambios se mantienen solo mientras la página está abierta; al recargar, se restablece el estado inicial.

## Estructura del repositorio

| Ruta | Contenido |
|---|---|
| `front/` | Aplicación web Angular de TurnoFácil. Demo cliente/asesor con datos locales en memoria. |
| `back/` | Fuentes Java de Spring Boot para la lógica de fila virtual, carga inicial CSV y endpoints de turnos. Aún falta configuración de compilación/ejecución. |
| `api/` | API independiente en Spring Boot para CRUD de `items`, con persistencia JPA/H2. |
| `api-python/` | API independiente en FastAPI para CRUD de `items`, con almacenamiento en memoria. |
| `tests/datos/` | Validaciones de calidad del CSV de turnos. |
| `tests/e2e/` | Pruebas end-to-end con Selenium contra la aplicación Angular. |
| `tests/postman/` | Colección Postman de pruebas de la API de turnos. |
| `docs/` | Contrato de API y casos de prueba documentados. |

## Tecnologías

- **Frontend:** Angular, TypeScript, HTML y CSS.
- **API de turnos:** Java, Spring Boot, Spring Data JPA y Jakarta Persistence (fuentes en `back/`).
- **CRUD de ejemplo:** Spring Boot/JPA/H2 en `api/` y FastAPI/Pydantic en `api-python/`.
- **Pruebas:** Selenium, pytest y Postman/Newman.

## Requisitos

Instala las herramientas necesarias según el módulo que vayas a ejecutar:

- Node.js y npm para Angular.
- Java 17 o superior para `api/` y, cuando se configure, `back/`.
- Python 3 para `api-python/` y las pruebas con pytest/Selenium.
- Google Chrome para las pruebas Selenium.

## Ejecutar la aplicación web

En PowerShell, desde la raíz del repositorio:

```powershell
cd front
npm install
npm start
```

Abre [http://localhost:4200](http://localhost:4200). La aplicación permite cambiar entre **Solicitar turno** y **Panel del asesor** desde la navegación superior. Detén el servidor con `Ctrl+C`.

Para compilar o ejecutar las pruebas unitarias de Angular:

```powershell
npm run build
npm test
```

> El frontend es actualmente una demo independiente: no requiere iniciar ningún backend. Sus turnos, avisos y métricas se gestionan localmente en el componente y no persisten en una base de datos.

## API de turnos — código disponible en `back/`

El backend implementa los estados `ESPERANDO`, `LLAMADO`, `ATENDIDO` y `CANCELADO`, una carga inicial desde `turnos_iniciales.csv` y estos endpoints:

| Método | Ruta | Uso |
|---|---|---|
| `POST` | `/turnos` | Solicitar un turno. Responde `201` con el turno asignado. |
| `GET` | `/turnos/{id}` | Consultar un turno por su identificador de base de datos. |
| `POST` | `/turnos/siguiente` | Llamar al siguiente turno en espera. |
| `POST` | `/turnos/actual/atendido` | Marcar como atendido el turno llamado actualmente. |
| `GET` | `/fila/espera` | Consultar cantidad en espera y número del turno actual. |
| `POST` | `/turnos/{id}/cancelar` | Cancelar un turno que todavía no haya sido atendido. |

Las reglas incluyen atender por orden de número, continuar la numeración desde los datos existentes y rechazar operaciones no válidas con `404` o `409`, según el caso. El parámetro `{id}` es el identificador interno del turno, no su número visible.

**Para poder ejecutar este backend hace falta completar `back/` con un `pom.xml` (o equivalente) y la configuración de aplicación/base de datos.** No uses las instrucciones antiguas de Maven para esta carpeta: el wrapper disponible está en `api/`, que es otro proyecto CRUD. El contrato detallado está en [`docs/contrato-api.md`](docs/contrato-api.md).

> La espera promedio aparece como requisito en los casos documentados, pero no está expuesta por los endpoints de `back/` actuales. Además, el valor de la demo Angular está definido localmente. Conviene alinear estas implementaciones antes de integrar la métrica.

## APIs CRUD de ejemplo

Estas APIs son proyectos de ejemplo para `items`; **no implementan los endpoints de turnos**.

### Java — `api/` (puerto 8080)

```powershell
cd api
.\mvnw.cmd spring-boot:run
```

| Método | Ruta | Acción |
|---|---|---|
| `GET` | `/api/items` | Listar items |
| `GET` | `/api/items/{id}` | Consultar un item |
| `POST` | `/api/items` | Crear un item |
| `PUT` | `/api/items/{id}` | Actualizar un item |
| `DELETE` | `/api/items/{id}` | Eliminar un item |

Cuerpo de ejemplo para `POST` y `PUT`:

```json
{"nombre":"Prueba","descripcion":"Primer item"}
```

Ejecuta sus pruebas automatizadas con:

```powershell
.\mvnw.cmd test
```

La aplicación usa JPA y H2; revisa [`api/src/main/resources/application.properties`](api/src/main/resources/application.properties) si cambias la configuración.

### Python — `api-python/` (puerto 8000)

```powershell
cd api-python
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install fastapi "uvicorn[standard]"
py -m uvicorn main:app --reload --port 8000
```

La documentación interactiva está en [http://localhost:8000/docs](http://localhost:8000/docs). Los endpoints CRUD son los mismos que los de la API Java (`/api/items`). La información se guarda en memoria y se pierde al reiniciar el proceso. Para salir del entorno virtual, ejecuta `deactivate`.

## Pruebas automatizadas

### Calidad del CSV

Desde la raíz, instala pytest si aún no está disponible y ejecuta:

```powershell
py -m pip install pytest
py -m pytest tests/datos/test_datos.py -v
```

El test busca por defecto `turnos_hoy.csv` en la raíz. El CSV versionado está en `back/src/main/resources/turnos_iniciales.csv`; para usarlo, indica la ruta explícitamente en PowerShell:

```powershell
$env:CSV_TURNOS = "back/src/main/resources/turnos_iniciales.csv"
py -m pytest tests/datos/test_datos.py -v
Remove-Item Env:CSV_TURNOS
```

La suite verifica columnas, estados, horas, duplicados conocidos, orden cronológico, espera promedio y numeración. Sin el archivo esperado, pytest omite las pruebas.

### End-to-end con Selenium

Inicia Angular en una terminal (`cd front; npm start`) y, desde otra terminal en la raíz, instala las dependencias de prueba y ejecútalas:

```powershell
py -m pip install selenium pytest pytest-html
py -m pytest tests/e2e/test_e2e.py -v --html=tests/e2e/reporte-e2e.html --self-contained-html
```

Selenium abre Chrome y prueba el flujo del cliente y del asesor sobre la misma instancia de la demo. Para usar otra URL en PowerShell:

```powershell
$env:FRONT_URL = "http://localhost:4200"
```

### Postman

La colección está en [`tests/postman/fila-turnos.json`](tests/postman/fila-turnos.json). Está pensada para ejecutarse contra la API de turnos y en un estado inicial limpio. Para generar reporte HTML con Newman:

```powershell
npm install --global newman newman-reporter-htmlextra
newman run tests/postman/fila-turnos.json -r htmlextra --reporter-htmlextra-export tests/postman/reporte-postman.html
```

Ten en cuenta que el backend de `back/` todavía requiere configuración de compilación y ejecución antes de poder correr esta colección contra él. El alcance y los resultados esperados están en [`docs/casos-de-prueba.md`](docs/casos-de-prueba.md).

## Puertos locales

| Aplicación | Puerto | Dirección |
|---|---:|---|
| Angular | 4200 | [http://localhost:4200](http://localhost:4200) |
| CRUD Java (`api/`) | 8080 | [http://localhost:8080/api/items](http://localhost:8080/api/items) |
| CRUD Python (`api-python/`) | 8000 | [http://localhost:8000/docs](http://localhost:8000/docs) |
| API de turnos (`back/`) | Sin configurar | Requiere completar configuración del proyecto. |

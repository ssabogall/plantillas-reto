# Plantillas Reto Accenture — Changemakers Tech

Plantillas listas para arrancar rápido en el reto: un backend en **Java (Spring Boot)**, un backend en **Python (FastAPI)**, un test automatizado con **Selenium** y un frontend en **Angular**.

Las dos APIs hacen lo mismo: un CRUD de `items` (crear, listar, consultar, actualizar y eliminar). Se usa la que elija el equipo.

---

## Estructura

```
entrevistaAccenture/
├── api/              → Backend Java con Spring Boot (puerto 8080)
├── api-python/       → Backend Python con FastAPI (puerto 8000) + test de Selenium
├── front/            → Frontend Angular (puerto 4200)
├── .gitignore        → Archivos que Git no debe subir
└── README.md         → Este archivo
```

---

## Herramientas usadas

| Herramienta | Para qué sirve |
|---|---|
| **Git** | Control de versiones: guarda el historial de cambios del código. |
| **GitHub CLI (`gh`)** | Maneja GitHub desde la terminal: iniciar sesión, crear repos y hacer push sin pedir contraseña. |
| **Java 17 (Temurin)** | Lenguaje y entorno que necesita Spring Boot. Debe ser 17 o mayor. |
| **Maven (`mvnw`)** | Descarga las dependencias y compila/ejecuta el proyecto Java. `mvnw` es un "wrapper" que trae Maven incluido. |
| **Spring Boot** | Framework de Java para crear APIs REST rápido. |
| **H2** | Base de datos en memoria. No hay que instalar nada, pero se borra al apagar el servidor. |
| **Python 3** | Lenguaje del backend alterno y del test de Selenium. |
| **venv** | Entorno virtual de Python: aísla las librerías de este proyecto del resto del computador. |
| **FastAPI** | Framework de Python para crear APIs REST. Genera documentación interactiva en `/docs`. |
| **Uvicorn** | Servidor que ejecuta la aplicación FastAPI. |
| **Selenium** | Automatiza el navegador (abre Chrome, navega y verifica cosas). Se usa para pruebas end-to-end. |
| **Node.js + npm** | Entorno para ejecutar JavaScript fuera del navegador y su gestor de paquetes. Angular lo necesita. |
| **Angular CLI (`ng`)** | Herramienta para crear, ejecutar y generar partes de un proyecto Angular. |
| **Postman** | Prueba APIs manualmente (enviar GET, POST, PUT, DELETE). |
| **VS Code / IntelliJ** | Editores de código. |

---

## 1. Backend Java — Spring Boot

### Prender

```powershell
cd "C:\Users\Lenovo\Documents\Universidad\2026-2\entrevistaAccenture\api"
.\mvnw.cmd spring-boot:run
```

- `cd ...` → entra a la carpeta del proyecto.
- `.\mvnw.cmd spring-boot:run` → compila y arranca el servidor.

Está listo cuando aparece **`Started ApiApplication`**. La terminal queda ocupada mientras el servidor corre; para probarlo, abre otra.

### Apagar

`Ctrl + C` en la terminal donde está corriendo.

### Endpoints

| Método | URL | Qué hace |
|---|---|---|
| GET | `http://localhost:8080/api/items` | Lista todos los items |
| GET | `http://localhost:8080/api/items/{id}` | Consulta un item |
| POST | `http://localhost:8080/api/items` | Crea un item |
| PUT | `http://localhost:8080/api/items/{id}` | Actualiza un item |
| DELETE | `http://localhost:8080/api/items/{id}` | Elimina un item |

Cuerpo JSON para POST y PUT:

```json
{ "nombre": "Prueba", "descripcion": "Primer item" }
```

### Probar desde PowerShell

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8080/api/items -ContentType "application/json" -Body '{"nombre":"Prueba","descripcion":"Primer item"}'
Invoke-RestMethod http://localhost:8080/api/items
```

- `Invoke-RestMethod` → hace peticiones HTTP desde PowerShell (como Postman, pero en la terminal).
- `-Method Post` → tipo de petición. `-Body` → los datos en JSON.

### Archivos importantes

```
api/src/main/java/com/reto/api/
├── ApiApplication.java    → Punto de entrada (arranca la app)
├── Item.java              → Entidad: define la tabla y sus campos
├── ItemRepository.java    → Acceso a datos (Spring genera el SQL)
└── ItemController.java    → Endpoints REST
```

Para agregar una entidad nueva, copia el patrón: entidad → repositorio → controlador.

### Equivalencias con NestJS

| NestJS | Spring Boot |
|---|---|
| `@Controller()` | `@RestController` + `@RequestMapping` |
| `@Get()`, `@Post()` | `@GetMapping`, `@PostMapping` |
| `@Injectable()` | `@Service` |
| Repositorio TypeORM | `JpaRepository<Entidad, Long>` |
| `@Body()`, `@Param()` | `@RequestBody`, `@PathVariable` |

---

## 2. Backend Python — FastAPI

### Prender

```powershell
cd "C:\Users\Lenovo\Documents\Universidad\2026-2\entrevistaAccenture\api-python"
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload --port 8000
```

- `.\venv\Scripts\Activate.ps1` → activa el entorno virtual. Aparece `(venv)` al inicio de la línea.
- `uvicorn main:app` → ejecuta el objeto `app` del archivo `main.py`.
- `--reload` → reinicia solo cada vez que guardas un cambio.
- `--port 8000` → puerto donde escucha.

Documentación interactiva para probar el CRUD desde el navegador: **http://localhost:8000/docs**

### Apagar

`Ctrl + C`. Para salir del entorno virtual: `deactivate`.

### Endpoints

Los mismos que Spring Boot, pero en el puerto **8000**: `http://localhost:8000/api/items`.

Los datos se guardan en memoria (un diccionario), así que se borran al apagar el servidor.

### Instalar librerías nuevas

```powershell
pip install nombre-libreria
pip freeze > requirements.txt
```

- `pip install` → instala una librería dentro del venv.
- `pip freeze > requirements.txt` → guarda la lista de librerías para que otros las instalen igual.

### Si clonas el repo en otro computador

```powershell
cd api-python
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

- `py -m venv venv` → crea el entorno virtual (la carpeta `venv` no se sube a GitHub).
- `pip install -r requirements.txt` → instala todo lo que está en la lista.

---

## 3. Test de Selenium

Requiere que **FastAPI esté corriendo** (sección 2) en otra terminal.

```powershell
cd "C:\Users\Lenovo\Documents\Universidad\2026-2\entrevistaAccenture\api-python"
.\venv\Scripts\Activate.ps1
python test_selenium.py
```

- Abre Chrome automáticamente, entra a `http://localhost:8000/docs`, verifica el título de la página y lo cierra.
- Si todo sale bien imprime **`SELENIUM OK`**.

Para probar otra página, cambia la URL en `driver.get(...)` y la condición del `assert`.

---

## 4. Frontend — Angular

### Prender

```powershell
cd "C:\Users\Lenovo\Documents\Universidad\2026-2\entrevistaAccenture\front"
ng serve --open
```

- `ng serve` → compila y levanta el servidor de desarrollo. Recarga solo al guardar cambios.
- `--open` → abre el navegador en **http://localhost:4200**.

### Apagar

`Ctrl + C`.

### Comandos útiles

```powershell
ng generate component nombre    # Crea un componente (vista)
ng generate service nombre      # Crea un servicio (para llamar a la API)
npm install                     # Instala dependencias si clonaste el repo
```

Para consumir la API desde Angular se usa `HttpClient` apuntando a `http://localhost:8080/api/items` (Spring) o `http://localhost:8000/api/items` (FastAPI). Las dos APIs ya permiten CORS, así que el frontend puede llamarlas sin bloqueos.

---

## 5. Postman

1. Abre Postman y crea una petición nueva.
2. Elige el método (GET, POST, PUT, DELETE).
3. Escribe la URL, por ejemplo `http://localhost:8080/api/items`.
4. Para POST o PUT: pestaña **Body → raw → JSON** y pega:
   ```json
   { "nombre": "Prueba", "descripcion": "Primer item" }
   ```
5. Clic en **Send**.

---

## 6. Git y GitHub

### Guardar y subir cambios

```powershell
git add .
git commit -m "Descripcion del cambio"
git push
```

- `git add .` → prepara todos los archivos modificados.
- `git commit -m "..."` → guarda un punto en el historial con un mensaje.
- `git push` → sube los commits a GitHub.

### Trabajo en equipo (recomendado en el reto)

```powershell
git pull                          # Trae los cambios de los demás
git checkout -b feature/nombre    # Crea una rama para tu tarea
git push -u origin feature/nombre # Sube tu rama por primera vez
```

Cada quien trabaja en su rama y se unen a `main` con un Pull Request. Así se evitan conflictos.

### Clonar el repo

```powershell
gh repo clone ssabogall/plantillas-reto
```

### Verificar sesión de GitHub

```powershell
gh auth status
```

---

## 7. Resumen rápido de puertos

| Servicio | Puerto | URL |
|---|---|---|
| Spring Boot | 8080 | http://localhost:8080/api/items |
| FastAPI | 8000 | http://localhost:8000/docs |
| Angular | 4200 | http://localhost:4200 |

---

## 8. Problemas comunes

**"Port 8080 was already in use"** (o 8000 / 4200)
Ya hay algo corriendo en ese puerto, seguramente un servidor que dejaste abierto. Ciérralo con `Ctrl + C` en su terminal o mira qué lo usa:

```powershell
netstat -ano | findstr :8080
taskkill /PID <numero> /F
```

- `netstat -ano | findstr :8080` → muestra qué proceso usa el puerto (el último número es el PID).
- `taskkill /PID <numero> /F` → cierra ese proceso.

**"running scripts is disabled on this system"** al activar el venv o usar `ng`

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force
```

Permite ejecutar scripts locales en PowerShell para tu usuario.

**`java -version` muestra 1.8**
El computador también tiene Java 8. Cierra todas las terminales y abre una nueva; si sigue igual, reinicia el computador. Spring Boot necesita la 17.

**`uvicorn` o `pip` no se reconocen**
Falta activar el entorno virtual: `.\venv\Scripts\Activate.ps1`.

**Spring Boot tarda mucho la primera vez**
Es normal: descarga dependencias. Las siguientes veces arranca en segundos.

# Casos de prueba - Fila virtual de turnos

**Alcance de pruebas:** API con **Postman** y end-to-end con **Selenium**. Reportes en HTML.

## Caso de negocio
Una oficina de atención quiere eliminar las filas físicas. El **cliente** pide turno desde el celular y sabe cuándo le toca. El **asesor** llama al siguiente y ve cuántas personas esperan. El sistema continúa desde lo registrado en la mañana (`turnos_hoy (1).csv`).

## Reglas del caso
- **R1.** Se atiende en **orden de llegada**.
- **R2.** Los números **no se repiten**.
- **R3.** No se puede llamar al siguiente si la **fila está vacía**.
- **Requisito:** mostrar la **espera promedio**.

## Hallazgos en los datos
| Hallazgo | Riesgo | Cómo lo cubrimos |
|---|---|---|
| El turno 9 (08:41) está en el archivo antes que el 7 (08:34) y el 8 (08:38) | Atender por orden de archivo viola R1 | P08 / E2E-06: el segundo llamado es el 7, no el 9 |
| El número 7 aparece dos veces (cancelado y pendiente) | Ambigüedad y choque con R2 | La carga omite el cancelado; P03 valida que el 7 cargado es el de las 08:34 y E2E-08 que la pantalla lo muestra así |
| Solo los atendidos tienen hora de atención | La espera promedio solo puede usar atendidos | P02: promedio 12.2 min |

## Estado esperado al iniciar (según `CargaInicial`)
La carga **omite los cancelados**, así que queda un solo turno 7 (el de las 08:34).

| id en BD | Número | Solicitud | Estado |
|---|---|---|---|
| 1-5 | 1-5 | 08:02-08:21 | ATENDIDO |
| 6 | 6 | 08:25 | ESPERANDO |
| 7 | 9 | 08:41 | ESPERANDO |
| 8 | 7 | 08:34 | ESPERANDO |
| 9 | 8 | 08:38 | ESPERANDO |
| 10 | 10 | 08:45 | ESPERANDO |

En espera: **5** · Orden: **6 → 7 → 8 → 9 → 10** · Espera promedio: **12.2 min** · Próximo número: **11**

## Pruebas de API (Postman) - `tests/postman/fila-turnos.json`
Se ejecutan en orden y con el back recién reiniciado.

| ID | Caso | Regla | Esperado |
|---|---|---|---|
| P01 | Fila inicial | R1 | 5 en espera, sin turno actual |
| P02 | Espera promedio | Req. | `esperaPromedioMin` = 12.2 |
| P03 | Turno 7 pendiente (id 8) | R2 | ESPERANDO, 1 persona delante |
| P04 | Turno 9 (id 7) en su lugar | R1 | 3 personas delante |
| P05 | Cliente pide turno | R2 | 201, número 11, 5 delante |
| P06 | Otro cliente pide turno | R2 | Número 12 |
| P07 | Asesor llama al siguiente | R1 | Turno 6, quedan 6 |
| P08 | Asesor llama otra vez | R1 | Turno 7, no el 9 |
| P09 | Fila muestra turno actual | R1 | Turno actual 7, quedan 5 |
| P10 | Marcar actual como atendido | - | Turno 7 ATENDIDO |
| P11 | Turno inexistente | - | 404 |
| P12 | Cancelar turno en espera | - | CANCELADO |
| P13 | Cancelar dos veces | - | 409 |
| P14 | Cancelar un atendido | - | 409 |
| P15 | Llamar con fila vacía | R3 | 409 "No hay personas en espera" |
| P16 | Fila vacía | R3 | 0 en espera |

## Pruebas end-to-end (Selenium) - `tests/e2e/test_e2e.py`
| ID | Caso | Regla | Esperado |
|---|---|---|---|
| E2E-01 | Servicios disponibles | - | Atención general, Pagos y consultas, Información |
| E2E-02 | Cliente obtiene turno | R2 | Aviso con el #11 |
| E2E-03 | Segundo cliente | R2 | Aviso con el #12 |
| E2E-04 | Nombre obligatorio | - | No se registra el #13 |
| E2E-05 | Fila en orden de llegada | R1 | 7 en espera, empieza 6-7-8-9-10 |
| E2E-06 | Espera promedio | Req. | 12.2 min |
| E2E-07 | Asesor llama al siguiente | R1 | Turno #6 |
| E2E-08 | Asesor llama otra vez | R1 | Turno #7 con llegada 08:34 |
| E2E-09 | Fila vacía | R3 | Aviso "No hay turnos pendientes por llamar" |

## Cómo ejecutar y generar reportes
Reiniciar el back antes de cada suite (ambas cambian los datos).

**Postman (HTML con Newman):**

    npm install -g newman newman-reporter-htmlextra
    newman run tests/postman/fila-turnos.json -r htmlextra --reporter-htmlextra-export tests/postman/reporte-postman.html

O desde la app: Import → clic derecho en la colección → Run collection.

**Selenium (HTML)** - con el front corriendo (`ng serve`):

    pip install selenium pytest pytest-html
    pytest tests/e2e/test_e2e.py -v --html=tests/e2e/reporte-e2e.html --self-contained-html

# Casos de prueba - Fila virtual de turnos

## Caso de negocio
Una oficina de atención quiere eliminar las filas físicas. El **cliente** pide turno desde el celular y sabe cuándo le toca. El **asesor** llama al siguiente turno y ve cuántas personas esperan. El sistema continúa desde los turnos registrados en la mañana (`turnos_hoy`).

## Reglas del caso
- **R1.** Los turnos se atienden en **orden de llegada** (hora de solicitud).
- **R2.** Los números de turno **no se repiten**.
- **R3.** No se puede llamar al siguiente si la **fila está vacía**.

## Hallazgos en los datos de entrada
| Hallazgo | Impacto | Decisión |
|---|---|---|
| El turno 9 (08:41) aparece en el archivo antes que el 7 (08:34) y el 8 (08:38) | Si se atiende por orden del archivo, se viola R1 | Ordenar por `hora_solicitud` |
| El turno 7 aparece dos veces (08:30 cancelado y 08:34 pendiente) | Riesgo de ambigüedad y de violar R2 | El cancelado no cuenta; el nuevo número es máximo + 1 |
| Pendientes y cancelados no tienen hora de atención | No se puede calcular su espera | La espera promedio solo usa atendidos |

## Estado esperado de la base de datos al iniciar
| Número | Solicitud | Atención | Estado | Espera (min) |
|---|---|---|---|---|
| 1 | 08:02 | 08:05 | atendido | 3 |
| 2 | 08:06 | 08:15 | atendido | 9 |
| 3 | 08:10 | 08:24 | atendido | 14 |
| 4 | 08:15 | 08:31 | atendido | 16 |
| 5 | 08:21 | 08:40 | atendido | 19 |
| 6 | 08:25 | - | pendiente | |
| 9 | 08:41 | - | pendiente | |
| 7 | 08:30 | - | cancelado | |
| 7 | 08:34 | - | pendiente | |
| 8 | 08:38 | - | pendiente | |
| 10 | 08:45 | - | pendiente | |

- Personas en espera: **5**
- Orden de la fila: **6 → 7 → 8 → 9 → 10**
- Espera promedio: **12.2 min**
- Próximo número a asignar: **11**

## Casos de prueba

### Pruebas de API (Postman) - validan servicio y datos
| ID | Caso | Regla | Resultado esperado |
|---|---|---|---|
| API-01 | Consultar la fila inicial | R1 | 5 en espera, orden 6-7-8-9-10, promedio 12.2 |
| API-02 | Los cancelados no están en la fila | R1 | Ningún turno con estado cancelado |
| API-03 | Consultar el turno 7 | R2 | Devuelve el pendiente de las 08:34 |
| API-04 | Cliente pide turno | R2 | 201, número 11, 5 personas delante |
| API-05 | Otro cliente pide turno | R2 | Número 12 (no se repite) |
| API-06 | Asesor llama al siguiente | R1 | Turno 6 |
| API-07 | Asesor llama otra vez | R1 | Turno 7, no el 9 |
| API-08 | Fila después de llamar | R1 | 5 en espera, el primero es el 8 |
| API-09 | Consultar un turno inexistente | - | 404 |
| API-10 | Vaciar la fila y llamar otra vez | R3 | 409 "La fila esta vacia" |

### Pruebas end-to-end (Selenium) - validan el flujo del usuario en pantalla
| ID | Caso | Regla | Resultado esperado |
|---|---|---|---|
| E2E-01 | El asesor abre la pantalla | R1 | Ve 5 en espera, promedio 12.2 y el turno 6 de primero |
| E2E-02 | El cancelado no se muestra | R1 | No aparece el turno de las 08:30 |
| E2E-03 | El cliente pide turno | R2 | Recibe el 11 con 5 personas delante |
| E2E-04 | El asesor llama al siguiente | R1 | Se llama al turno 6 |
| E2E-05 | El asesor llama otra vez | R1 | Se llama al 7, no al 9 |
| E2E-06 | El asesor llama con la fila vacía | R3 | Se muestra el mensaje "La fila esta vacia" |

## Cómo ejecutar
Las dos suites cambian los datos. **Reiniciar el backend antes de cada suite** para recargar el archivo.

**Postman:** importar `tests/postman/fila-turnos.json`, clic derecho en la colección, **Run collection**, **Run**.

**Selenium:**

    pip install selenium pytest pytest-html
    pytest tests/e2e/test_e2e.py -v --html=tests/e2e/reporte-e2e.html --self-contained-html

El reporte queda en `tests/e2e/reporte-e2e.html`.

## Casos adicionales

### Contrato (se pueden correr contra el mock de Postman antes de que el back esté listo)
| ID | Caso | Resultado esperado |
|---|---|---|
| CON-01 | Estructura de `/fila` | `enEspera` es número, `esperaPromedioMin` es número, `turnos` es lista |
| CON-02 | Estructura de un turno | Tiene `numero`, `horaSolicitud`, `horaAtencion`, `estado` |
| CON-03 | Formato de horas | `horaSolicitud` cumple `HH:MM` |
| CON-04 | Estados válidos | `estado` es `pendiente`, `atendido` o `cancelado` |

### Bordes y errores
| ID | Caso | Regla | Resultado esperado |
|---|---|---|---|
| API-11 | Consultar un turno ya atendido (el 1) | - | 200, estado `atendido`, sin `personasDelante` |
| API-12 | Llamar al siguiente con GET en vez de POST | - | 405 Método no permitido |
| API-13 | Tiempo de respuesta de `/fila` | - | Menos de 500 ms |
| API-14 | Pedir turno con número enviado por el cliente | R2 | El sistema ignora el número y asigna el siguiente |
| API-15 | Hora de atención no anterior a la de solicitud | R1 | `horaAtencion >= horaSolicitud` |

### Calidad de datos del CSV (`tests/datos/test_datos.py`)
No dependen del back ni del front: validan el archivo de entrada.

| ID | Caso | Resultado esperado |
|---|---|---|
| DAT-01 | Columnas del archivo | `numero`, `hora_solicitud`, `hora_atencion`, `estado` |
| DAT-02 | Cantidad de registros | 11 |
| DAT-03 | Estados válidos | Solo `pendiente`, `atendido`, `cancelado` |
| DAT-04 | Hora de solicitud | Todos la tienen |
| DAT-05 | Atendidos | Todos tienen hora de atención |
| DAT-06 | Pendientes | Ninguno tiene hora de atención |
| DAT-07 | Coherencia de horas | Atención no es anterior a solicitud |
| DAT-08 | Hallazgo: duplicado | El 7 aparece dos veces (cancelado y pendiente) |
| DAT-09 | Hallazgo: desorden | El archivo no viene ordenado por hora |
| DAT-10 | Orden de llegada | Pendientes: 6, 7, 8, 9, 10 |
| DAT-11 | Espera promedio | 12.2 min |
| DAT-12 | Próximo número | 11 |

## Formulario del cliente (definido por front)
- **nombre**: nombre completo, texto, **obligatorio**
- **servicio**: `Atención general`, `Pagos y consultas` o `Información`
- Botón **"Obtener mi turno"**: registra el turno y muestra **número, estado y hora de solicitud**

> Nota: los turnos de la mañana (CSV) no traen nombre ni servicio. El sistema debe aceptarlos sin esos campos.

### Pruebas de API del formulario
| ID | Caso | Resultado esperado |
|---|---|---|
| API-16 | Pedir turno con nombre y servicio válidos | 201, devuelve número, estado `pendiente` y hora de solicitud |
| API-17 | Pedir turno sin nombre | 400, no se crea el turno |
| API-18 | Pedir turno con nombre solo de espacios | 400, no se crea el turno |
| API-19 | Pedir turno con servicio no válido | 400, no se crea el turno |
| API-20 | Un turno rechazado no consume número | El siguiente turno válido recibe el número que seguía |

### Pruebas E2E del formulario
| ID | Caso | Resultado esperado |
|---|---|---|
| E2E-07 | Cliente llena nombre y servicio y da clic en "Obtener mi turno" | Ve su número, estado y hora |
| E2E-08 | Cliente da clic sin escribir nombre | No se registra el turno y se muestra un aviso |
| E2E-09 | La lista de servicios | Muestra exactamente las 3 opciones |
| DAT-13 | `tiempo_espera_min` | Igual a atención - solicitud en atendidos; vacío en los demás |
| DAT-14 | `es_pendiente` / `es_cancelado` | Coinciden con la columna `estado` |
| DAT-15 | `turno_id` | Único, aunque `numero` se repita |

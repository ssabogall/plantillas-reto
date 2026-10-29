# Contrato de la API (según el back actual)

Base URL: `http://localhost:8080`

| Método | Ruta | Quién | Respuesta OK | Errores |
|---|---|---|---|---|
| POST | `/turnos` | Cliente | 201 `{id, numero, estado, personasDelante, turnoActual}` | - |
| GET | `/turnos/{id}` | Cliente | 200 `{id, numero, estado, personasDelante, turnoActual}` | 404 "El turno no existe" |
| POST | `/turnos/siguiente` | Asesor | 200 `{numero, enEspera}` | 409 "No hay personas en espera" |
| POST | `/turnos/actual/atendido` | Asesor | 200 turno con estado ATENDIDO | 409 "No hay un turno llamado" |
| GET | `/fila/espera` | Asesor | 200 `{enEspera, turnoActual}` | - |
| POST | `/turnos/{id}/cancelar` | Cliente/Asesor | 200 turno con estado CANCELADO | 404 / 409 si ya está atendido o cancelado |

Estados: `ESPERANDO`, `LLAMADO`, `ATENDIDO`, `CANCELADO`.

> `{id}` es el `turno_id`, no el número del turno (el número 7 se repite).

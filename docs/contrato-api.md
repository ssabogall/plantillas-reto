# Contrato de la API - Fila virtual de turnos

> Acuerdo entre back, front y pruebas. Si algo cambia (ruta, nombre de campo o código de estado), se actualiza aquí primero.

Base URL: `http://localhost:8080/api`

## Objeto Turno
| Campo | Tipo | Ejemplo | Nota |
|---|---|---|---|
| `numero` | entero | `11` | No se repite |
| `horaSolicitud` | texto `HH:MM` | `"08:34"` | Define el orden de llegada |
| `horaAtencion` | texto `HH:MM` o `null` | `null` | Solo los atendidos tienen |
| `estado` | texto | `"pendiente"` | `pendiente`, `atendido` o `cancelado` |
| `personasDelante` | entero | `5` | Solo si está pendiente |

## Endpoints

### POST /turnos - el cliente pide turno
- **201** → turno nuevo:
```json
{ "numero": 11, "horaSolicitud": "16:10", "horaAtencion": null, "estado": "pendiente", "personasDelante": 5 }
```

### GET /turnos/{numero} - el cliente consulta cuándo le toca
- **200** → turno (con `personasDelante` si está pendiente)
- **404** → `{ "message": "Turno no encontrado" }`

### POST /turnos/siguiente - el asesor llama al siguiente
- **200** → turno llamado, ahora `atendido`:
```json
{ "numero": 6, "horaSolicitud": "08:25", "horaAtencion": "16:12", "estado": "atendido" }
```
- **409** → `{ "message": "La fila esta vacia" }`

### GET /fila - el asesor ve la fila
- **200**:
```json
{
  "enEspera": 5,
  "esperaPromedioMin": 12.2,
  "turnos": [
    { "numero": 6, "horaSolicitud": "08:25", "horaAtencion": null, "estado": "pendiente" }
  ]
}
```
- `turnos` viene **ordenado por horaSolicitud** y solo trae pendientes.

## IDs de la pantalla (para Selenium)
| Elemento | id |
|---|---|
| Botón pedir turno | `btn-pedir` |
| Texto del turno del cliente | `mi-turno` |
| Botón llamar siguiente | `btn-siguiente` |
| Texto del turno llamado | `llamado` |
| Número de personas en espera | `en-espera` |
| Espera promedio | `espera-promedio` |
| Lista de turnos en espera | `lista` (con `li` por turno) |
| Mensaje de error | `error` |

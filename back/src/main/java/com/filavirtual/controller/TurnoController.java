package com.filavirtual.controller;

import com.filavirtual.service.TurnoService;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
public class TurnoController {

    private final TurnoService service;

    public TurnoController(TurnoService service) {
        this.service = service;
    }

    // Cliente
    @PostMapping("/turnos")
    @ResponseStatus(HttpStatus.CREATED)
    public Map<String, Object> pedir() {
        return service.pedirTurno();
    }

    @GetMapping("/turnos/{id}")
    public Map<String, Object> consultar(@PathVariable Long id) {
        return service.consultar(id);
    }

    // Asesor
    @PostMapping("/turnos/siguiente")
    public Map<String, Object> siguiente() {
        return service.llamarSiguiente();
    }

    @PostMapping("/turnos/actual/atendido")
    public Map<String, Object> atendido() {
        return service.marcarActualAtendido();
    }

    @GetMapping("/fila/espera")
    public Map<String, Object> fila() {
        return service.estadoFila();
    }

    @PostMapping("/turnos/{id}/cancelar")
    public Map<String, Object> cancelar(@PathVariable Long id) {
        return service.cancelar(id);
    }
}

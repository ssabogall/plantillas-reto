package com.filavirtual.service;

import com.filavirtual.model.Estado;
import com.filavirtual.model.Turno;
import com.filavirtual.repository.TurnoRepository;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.time.LocalDateTime;
import java.util.LinkedHashMap;
import java.util.Map;

@Service
public class TurnoService {

    private final TurnoRepository repo;

    public TurnoService(TurnoRepository repo) {
        this.repo = repo;
    }

    /** El cliente pide un turno: el número continúa desde el máximo existente (incluye el Excel). */
    @Transactional
    public Map<String, Object> pedirTurno() {
        Turno t = new Turno();
        t.setNumero(repo.maxNumero() + 1);
        t = repo.save(t);
        return resumen(t);
    }

    /** El cliente consulta su turno: estado, personas delante y turno actual. */
    @Transactional(readOnly = true)
    public Map<String, Object> consultar(Long id) {
        Turno t = repo.findById(id).orElseThrow(() ->
                new ResponseStatusException(HttpStatus.NOT_FOUND, "El turno no existe"));
        return resumen(t);
    }

    /** El asesor llama al siguiente en orden FIFO. */
    @Transactional
    public Map<String, Object> llamarSiguiente() {
        Turno t = repo.findFirstByEstadoOrderByNumeroAsc(Estado.ESPERANDO)
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.CONFLICT, "No hay personas en espera"));
        t.setEstado(Estado.LLAMADO);
        t.setLlamadoEn(LocalDateTime.now());
        repo.save(t);

        Map<String, Object> r = new LinkedHashMap<>();
        r.put("numero", t.getNumero());
        r.put("enEspera", repo.countByEstado(Estado.ESPERANDO));
        return r;
    }

    /** El asesor marca como atendido el turno que está llamado actualmente. */
    @Transactional
    public Map<String, Object> marcarActualAtendido() {
        Turno t = repo.findFirstByEstadoOrderByLlamadoEnDescNumeroDesc(Estado.LLAMADO)
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.CONFLICT, "No hay un turno llamado"));
        t.setEstado(Estado.ATENDIDO);
        repo.save(t);
        return resumen(t);
    }

    /** Cuántas personas esperan y cuál es el turno actual. */
    @Transactional(readOnly = true)
    public Map<String, Object> estadoFila() {
        Map<String, Object> r = new LinkedHashMap<>();
        r.put("enEspera", repo.countByEstado(Estado.ESPERANDO));
        r.put("turnoActual", turnoActual());
        return r;
    }

    private Integer turnoActual() {
        return repo.findFirstByEstadoOrderByLlamadoEnDescNumeroDesc(Estado.LLAMADO)
                .map(Turno::getNumero).orElse(null);
    }

    private Map<String, Object> resumen(Turno t) {
        long delante = t.getEstado() == Estado.ESPERANDO
                ? repo.countByEstadoAndNumeroLessThan(Estado.ESPERANDO, t.getNumero())
                : 0;
        Map<String, Object> r = new LinkedHashMap<>();
        r.put("id", t.getId());
        r.put("numero", t.getNumero());
        r.put("estado", t.getEstado());
        r.put("personasDelante", delante);
        r.put("turnoActual", turnoActual());
        return r;
    }
}

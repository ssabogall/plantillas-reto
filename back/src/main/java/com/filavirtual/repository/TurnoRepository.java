package com.filavirtual.repository;

import com.filavirtual.model.Estado;
import com.filavirtual.model.Turno;
import jakarta.persistence.LockModeType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Lock;
import org.springframework.data.jpa.repository.Query;

import java.util.Optional;

public interface TurnoRepository extends JpaRepository<Turno, Long> {

    long countByEstado(Estado estado);

    long countByEstadoAndNumeroLessThan(Estado estado, Integer numero);

    @Query("select coalesce(max(t.numero), 0) from Turno t")
    int maxNumero();

    // Bloqueo: dos asesores no pueden llamar el mismo turno a la vez
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    Optional<Turno> findFirstByEstadoOrderByNumeroAsc(Estado estado);

    Optional<Turno> findFirstByEstadoOrderByLlamadoEnDescNumeroDesc(Estado estado);
}

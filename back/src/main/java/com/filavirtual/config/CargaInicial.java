package com.filavirtual.config;

import com.filavirtual.model.Estado;
import com.filavirtual.model.Turno;
import com.filavirtual.repository.TurnoRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Component;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.util.HashSet;
import java.util.Set;

@Component
public class CargaInicial implements CommandLineRunner {

    private final TurnoRepository repo;

    public CargaInicial(TurnoRepository repo) {
        this.repo = repo;
    }

    @Override
    public void run(String... args) throws Exception {
        if (repo.count() > 0) return; // no duplicar datos

        LocalDate hoy = LocalDate.now();
        Set<Integer> vistos = new HashSet<>();
        int cargados = 0;

        try (var br = new BufferedReader(new InputStreamReader(
                new ClassPathResource("turnos_iniciales.csv").getInputStream(),
                StandardCharsets.UTF_8))) {

            br.readLine(); // encabezado
            String linea;
            while ((linea = br.readLine()) != null) {
                if (linea.isBlank()) continue;
                String[] c = linea.split(",", -1); // numero,hora_solicitud,hora_atencion,estado,...

                String estadoCsv = c[3].trim().toUpperCase();
                if (estadoCsv.equals("CANCELADO")) continue;     // se omiten los cancelados

                int numero = Integer.parseInt(c[0].trim());
                if (!vistos.add(numero)) continue;               // número repetido: se omite

                Turno t = new Turno();
                t.setNumero(numero);
                t.setCreadoEn(LocalDateTime.of(hoy, LocalTime.parse(c[1].trim())));
                if (!c[2].isBlank()) {
                    t.setLlamadoEn(LocalDateTime.of(hoy, LocalTime.parse(c[2].trim())));
                }
                t.setEstado(estadoCsv.equals("ATENDIDO") ? Estado.ATENDIDO : Estado.ESPERANDO); // PENDIENTE → ESPERANDO
                repo.save(t);
                cargados++;
            }
        }
        System.out.println("[CargaInicial] Turnos cargados: " + cargados);
    }
}
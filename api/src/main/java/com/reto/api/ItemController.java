package com.reto.api;

import java.util.List;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/items")
@CrossOrigin(origins = "*")
public class ItemController {
    private final ItemRepository repo;

    public ItemController(ItemRepository repo) { this.repo = repo; }

    @GetMapping
    public List<Item> listar() { return repo.findAll(); }

    @GetMapping("/{id}")
    public ResponseEntity<Item> obtener(@PathVariable Long id) {
        return repo.findById(id).map(ResponseEntity::ok).orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public Item crear(@RequestBody Item item) { return repo.save(item); }

    @PutMapping("/{id}")
    public ResponseEntity<Item> actualizar(@PathVariable Long id, @RequestBody Item datos) {
        return repo.findById(id).map(i -> {
            i.setNombre(datos.getNombre());
            i.setDescripcion(datos.getDescripcion());
            return ResponseEntity.ok(repo.save(i));
        }).orElse(ResponseEntity.notFound().build());
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> eliminar(@PathVariable Long id) {
        if (!repo.existsById(id)) return ResponseEntity.notFound().build();
        repo.deleteById(id);
        return ResponseEntity.noContent().build();
    }
}

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="API Reto")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class ItemIn(BaseModel):
    nombre: str
    descripcion: str = ""

class Item(ItemIn):
    id: int

items: dict[int, Item] = {}
contador = 0

@app.get("/api/items")
def listar():
    return list(items.values())

@app.get("/api/items/{item_id}")
def obtener(item_id: int):
    if item_id not in items:
        raise HTTPException(404, "No encontrado")
    return items[item_id]

@app.post("/api/items", status_code=201)
def crear(data: ItemIn):
    global contador
    contador += 1
    items[contador] = Item(id=contador, **data.model_dump())
    return items[contador]

@app.put("/api/items/{item_id}")
def actualizar(item_id: int, data: ItemIn):
    if item_id not in items:
        raise HTTPException(404, "No encontrado")
    items[item_id] = Item(id=item_id, **data.model_dump())
    return items[item_id]

@app.delete("/api/items/{item_id}", status_code=204)
def eliminar(item_id: int):
    if item_id not in items:
        raise HTTPException(404, "No encontrado")
    del items[item_id]

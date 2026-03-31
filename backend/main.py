import sqlite3
import time
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="FoodDelivery API (Anti-Patrón)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar Base de Datos (Directo en el inicio del script - muy acoplado)
conn = sqlite3.connect("comida.db", check_same_thread=False)
cursor = conn.cursor()

# Creación de tablas e inserción de datos iniciales
cursor.executescript("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    saldo REAL
);

CREATE TABLE IF NOT EXISTS restaurantes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    activo INTEGER
);

CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurante_id INTEGER,
    nombre TEXT,
    precio REAL,
    stock INTEGER
);

CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    total REAL,
    estado TEXT
);

-- Insertar datos semilla si la base está vacía
INSERT INTO usuarios (nombre, saldo) 
SELECT 'Juan Perez', 500.0 WHERE NOT EXISTS (SELECT 1 FROM usuarios);

INSERT INTO restaurantes (nombre, activo) 
SELECT 'La Hamburguesería', 1 WHERE NOT EXISTS (SELECT 1 FROM restaurantes);

INSERT INTO productos (restaurante_id, nombre, precio, stock) 
SELECT 1, 'Hamburguesa Doble', 12.50, 10 WHERE NOT EXISTS (SELECT 1 FROM productos);

INSERT INTO productos (restaurante_id, nombre, precio, stock) 
SELECT 1, 'Papas Fritas', 4.00, 5 WHERE (SELECT count(*) from productos) < 2;

INSERT INTO productos (restaurante_id, nombre, precio, stock) 
SELECT 1, 'Refresco', 2.50, 20 WHERE (SELECT count(*) from productos) < 3;
""")
conn.commit()


# Pydantic Schemas
class PedidoRequest(BaseModel):
    usuario_id: int
    productos_ids: List[int]

class ProductoResponse(BaseModel):
    id: int
    restaurante_id: int
    nombre: str
    precio: float
    stock: int


# Entidades
class Usuario:
    def __init__(self, id, nombre, saldo):
        self.id = id
        self.nombre = nombre
        self.saldo = saldo

class Restaurante:
    def __init__(self, id, nombre, activo):
        self.id = id
        self.nombre = nombre
        self.activo = activo

class Producto:
    def __init__(self, id, restaurante_id, nombre, precio, stock):
        self.id = id
        self.restaurante_id = restaurante_id
        self.nombre = nombre
        self.precio = precio
        self.stock = stock

# 🚨 GOD CLASS: La clase Pedido hace todo el trabajo (anti-patrón).
class Pedido:
    def __init__(self):
        self.id = None
        self.usuario_id = None
        self.total = 0.0
        self.estado = 'INICIALIZADO'

    def crear_pedido(self, usuario_id: int, productos_ids: List[int]):
        # 1. Verificar si el usuario existe
        cursor.execute("SELECT id, nombre, saldo FROM usuarios WHERE id = ?", (usuario_id,))
        usr_row = cursor.fetchone()
        if not usr_row:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # 2. Calcular total, verificar stock de cada producto y restar stock 
        # (Esto mezcla validación, cálculo y actualización destructiva directamente)
        total_calculado = 0.0
        for p_id in productos_ids:
            cursor.execute("SELECT id, restaurante_id, nombre, precio, stock FROM productos WHERE id = ?", (p_id,))
            prod_row = cursor.fetchone()
            if not prod_row:
                raise HTTPException(status_code=404, detail=f"Producto {p_id} no existe")
            
            p_stock = prod_row[4]
            p_precio = prod_row[3]

            if p_stock <= 0:
                raise HTTPException(status_code=400, detail=f"No hay stock para producto {prod_row[2]}")
            
            # Cálculo del carrito
            total_calculado += p_precio
            
            # Disminuir stock inmediatamente en DB (!Problema de transacciones en la God Class)
            cursor.execute("UPDATE productos SET stock = stock - 1 WHERE id = ?", (p_id,))

        self.total = total_calculado
        
        # 3. Procesar "pago" (lógica de negocio simulada mezclada aquí)
        # Esto debería estar en un servicio externo de finanzas
        saldo_usuario = usr_row[2]
        if saldo_usuario < self.total:
            # Revertir stock (muy mala práctica hacerlo manualmente así en vez de BD transactions)
            for p_id in productos_ids:
                cursor.execute("UPDATE productos SET stock = stock + 1 WHERE id = ?", (p_id,))
            conn.commit()
            raise HTTPException(status_code=400, detail="Saldo insuficiente para procesar el pago")
        
        # Restar saldo al usuario
        nuevo_saldo = saldo_usuario - self.total
        cursor.execute("UPDATE usuarios SET saldo = ? WHERE id = ?", (nuevo_saldo, usuario_id))
        
        # Simulando tiempo de conexión con Gateway de pagos de terceros
        time.sleep(1) 
        self.estado = 'PAGADO'

        # 4. Guardar Order en DB y actualizar su estado interno
        cursor.execute("INSERT INTO pedidos (usuario_id, total, estado) VALUES (?, ?, ?)", 
                       (usuario_id, self.total, self.estado))
        self.id = cursor.lastrowid
        conn.commit()
        
        return {
            "mensaje": "Pedido creado, pagado y procesado exitosamente",
            "pedido_id": self.id,
            "total": self.total,
            "nuevo_saldo_usuario": nuevo_saldo
        }


# Endpoints (Controladores que instancian la God Class)

@app.get("/productos", response_model=List[ProductoResponse])
def obtener_productos():
    # Consulta directa desde API Controller (alto acoplamiento)
    cursor.execute("SELECT id, restaurante_id, nombre, precio, stock FROM productos WHERE stock > 0")
    filas = cursor.fetchall()
    return [{"id": f[0], "restaurante_id": f[1], "nombre": f[2], "precio": f[3], "stock": f[4]} for f in filas]

@app.post("/pedido")
def procesar_compra(req: PedidoRequest):
    # Todo en un solo comando
    pedido_god = Pedido()
    return pedido_god.crear_pedido(req.usuario_id, req.productos_ids)


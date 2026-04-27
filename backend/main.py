import sqlite3
import time
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="FoodDelivery API (Anti-Pattern)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

conn = sqlite3.connect("food_delivery.db", check_same_thread=False)
cursor = conn.cursor()

cursor.executescript(
    """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    balance REAL
);

CREATE TABLE IF NOT EXISTS restaurants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    is_active INTEGER
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurant_id INTEGER,
    name TEXT,
    price REAL,
    stock INTEGER
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    total REAL,
    status TEXT
);

INSERT INTO users (name, balance)
SELECT 'John Perez', 500.0 WHERE NOT EXISTS (SELECT 1 FROM users);

INSERT INTO restaurants (name, is_active)
SELECT 'The Burger Place', 1 WHERE NOT EXISTS (SELECT 1 FROM restaurants);

INSERT INTO products (restaurant_id, name, price, stock)
SELECT 1, 'Double Burger', 12.50, 10 WHERE NOT EXISTS (SELECT 1 FROM products);

INSERT INTO products (restaurant_id, name, price, stock)
SELECT 1, 'French Fries', 4.00, 5 WHERE (SELECT count(*) FROM products) < 2;

INSERT INTO products (restaurant_id, name, price, stock)
SELECT 1, 'Soda', 2.50, 20 WHERE (SELECT count(*) FROM products) < 3;
"""
)
conn.commit()


class CreateOrderRequest(BaseModel):
    user_id: int
    product_ids: List[int]


class ProductResponse(BaseModel):
    id: int
    restaurant_id: int
    name: str
    price: float
    stock: int


class User:
    def __init__(self, id: int, name: str, balance: float):
        self.id = id
        self.name = name
        self.balance = balance


class Restaurant:
    def __init__(self, id: int, name: str, is_active: int):
        self.id = id
        self.name = name
        self.is_active = is_active


class Product:
    def __init__(self, id: int, restaurant_id: int, name: str, price: float, stock: int):
        self.id = id
        self.restaurant_id = restaurant_id
        self.name = name
        self.price = price
        self.stock = stock


class OrderProcessor:
    def __init__(self):
        self.id = None
        self.user_id = None
        self.total = 0.0
        self.status = "INITIALIZED"

    def create_order(self, user_id: int, product_ids: List[int]):
        cursor.execute("SELECT id, name, balance FROM users WHERE id = ?", (user_id,))
        user_row = cursor.fetchone()
        if not user_row:
            raise HTTPException(status_code=404, detail="User not found")

        calculated_total = 0.0
        for product_id in product_ids:
            cursor.execute(
                "SELECT id, restaurant_id, name, price, stock FROM products WHERE id = ?",
                (product_id,),
            )
            product_row = cursor.fetchone()
            if not product_row:
                raise HTTPException(status_code=404, detail=f"Product {product_id} does not exist")

            product_stock = product_row[4]
            product_price = product_row[3]

            if product_stock <= 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"No stock available for product {product_row[2]}",
                )

            calculated_total += product_price
            cursor.execute("UPDATE products SET stock = stock - 1 WHERE id = ?", (product_id,))

        self.total = calculated_total

        user_balance = user_row[2]
        if user_balance < self.total:
            for product_id in product_ids:
                cursor.execute("UPDATE products SET stock = stock + 1 WHERE id = ?", (product_id,))
            conn.commit()
            raise HTTPException(status_code=400, detail="Insufficient balance to process payment")

        new_user_balance = user_balance - self.total
        cursor.execute("UPDATE users SET balance = ? WHERE id = ?", (new_user_balance, user_id))

        time.sleep(1)
        self.status = "PAID"

        cursor.execute(
            "INSERT INTO orders (user_id, total, status) VALUES (?, ?, ?)",
            (user_id, self.total, self.status),
        )
        self.id = cursor.lastrowid
        conn.commit()

        return {
            "message": "Order created, paid, and processed successfully",
            "order_id": self.id,
            "total": self.total,
            "new_user_balance": new_user_balance,
        }


@app.get("/products", response_model=List[ProductResponse])
def list_products():
    cursor.execute("SELECT id, restaurant_id, name, price, stock FROM products WHERE stock > 0")
    rows = cursor.fetchall()
    return [
        {
            "id": row[0],
            "restaurant_id": row[1],
            "name": row[2],
            "price": row[3],
            "stock": row[4],
        }
        for row in rows
    ]


@app.post("/orders")
def create_order_endpoint(request: CreateOrderRequest):
    order_processor = OrderProcessor()
    return order_processor.create_order(request.user_id, request.product_ids)

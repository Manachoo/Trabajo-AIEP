# FoodDelivery Proyecto para la Universitario

Este proyecto fue generado como caso de estudio de mala arquitectura de software para ser refactorizado. Incluye una **God Class** en el backend llamada `Pedido` que rompe el principio de Single Responsibility (SRP) y genera alto acoplamiento.

## Estructura

- `/backend`: API construida con FastAPI y SQLite.
- `/frontend`: Interfaz de usuario con React, Vite y TailwindCSS.

## Requisitos

- Python 3.9+
- Node.js 18+

## Instrucciones para el Backend

1. Navegar a la carpeta backend:
```bash
cd backend
```

2. Instalar las dependencias (se recomienda usar un entorno virtual):
```bash
pip install -r requirements.txt
```

3. Ejecutar el servidor. La base de datos SQLite se creará automáticamente y se llenará con datos iniciales:
```bash
uvicorn main:app --reload
```
El servidor backend estará disponible en `http://127.0.0.1:8000`.

## Instrucciones para el Frontend

1. Abrir una nueva terminal y navegar a la carpeta frontend:
```bash
cd frontend
```

2. Instalar dependencias (ya deben estar instaladas si se inicializó correctamente, pero por si acaso):
```bash
npm install
```

3. Correr el servidor de desarrollo:
```bash
npm run dev
```
El frontend estará disponible en el puerto por defecto de Vite (usualmente `http://localhost:5173`).


## Explicación de la clase pedido
1. Recibe la petición.
2. Calcula los precios interactuando directamente con la base de datos `sqlite3`.
3. Valida y deduce el stock de forma destructiva (sin manejo de transacciones).
4. Verifica saldo del usuario y simula el pago en su propio flujo.
5. Registra el pedido final.


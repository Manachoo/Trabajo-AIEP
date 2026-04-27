# FoodDelivery Component Architecture

This project implements a food ordering flow using a modular backend with **Facade**, **Command**, **Abstract Factory**, and **Repository** patterns. The backend uses **FastAPI + PostgreSQL** and the frontend uses **React + Vite**.

## Architecture Overview

- `OrderFacade` orchestrates order processing from the API layer.
- `ProcessOrderCommand` encapsulates the transaction flow and exposes `execute`/`undo`.
- `PaymentFactory` creates the correct payment processor by method.
- Repositories isolate data access (`UserRepository`, `ProductRepository`, `OrderRepository`).
- FastAPI routes interact with application services, not with raw SQL.

## Project Structure

- `/backend`
  - `main.py`: FastAPI app bootstrap and startup initialization.
  - `app/api`: routes, request/response schemas, DI dependencies.
  - `app/application`: facade and command use cases.
  - `app/domain`: domain interfaces and contracts.
  - `app/infrastructure`: database setup, ORM models, repositories, payment implementations.
- `/frontend`: React UI.
- `docker-compose.yml`: multi-service setup (`postgres`, `backend`, `frontend`).
- `docs/components.puml`: UML component diagram source.

## Run with Docker (Dev and Prod-like)

```bash
docker compose up --build
```

Services:

- Frontend: `http://localhost:8081`
- Backend: `http://localhost:8000`
- Backend docs: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5432`

Default database settings (already wired in `docker-compose.yml`):

- DB name: `food_delivery`
- User: `food_user`
- Password: `food_password`

## API Endpoints

- `GET /health`
- `GET /products`
- `POST /orders`

Example order payload:

```json
{
  "user_id": 1,
  "product_ids": [1, 2],
  "payment_method": "balance"
}
```

`payment_method` is optional and defaults to `balance`.

## Notes

- Database schema and seed data are initialized automatically on backend startup.
- The order process is transactional: stock reservation, payment, and order persistence are handled atomically.
- `undo()` is implemented as compensating logic for external payment refunds.

## Backend Tests

Run backend integration tests inside Docker:

```bash
docker compose exec backend pip install -r requirements-dev.txt
docker compose exec backend pytest -q
```

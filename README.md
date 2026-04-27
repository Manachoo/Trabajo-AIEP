# FoodDelivery Study Project

This project is intentionally designed as a software architecture refactoring case study. It includes a backend **God Class** (`OrderProcessor`) that violates the Single Responsibility Principle (SRP) and demonstrates high coupling.

## Structure

- `/backend`: FastAPI API with SQLite.
- `/frontend`: React user interface with Vite and TailwindCSS.

## Requirements

- Python 3.9+
- Node.js 18+

## Backend Setup

1. Open the backend directory:

```bash
cd backend
```

2. Install dependencies (a virtual environment is recommended):

```bash
pip install -r requirements.txt
```

3. Start the server. The SQLite database is created automatically and seeded with initial data:

```bash
uvicorn main:app --reload
```

Backend base URL: `http://127.0.0.1:8000`

## Frontend Setup

1. Open a new terminal and go to the frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Run the development server:

```bash
npm run dev
```

Frontend URL (default Vite port): `http://localhost:5173`

## About the OrderProcessor God Class

1. Receives the request.
2. Calculates totals while querying SQLite directly.
3. Validates and decrements stock in a destructive flow (without proper transaction boundaries).
4. Verifies user balance and simulates payment in the same flow.
5. Persists the final order.

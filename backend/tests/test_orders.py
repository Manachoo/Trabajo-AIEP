from app.infrastructure.database import SessionLocal
from app.infrastructure.models import Order, Product, User


def test_get_products_returns_seeded_products(client):
    response = client.get("/products")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 3
    assert payload[0]["name"] == "Double Burger"


def test_create_order_with_balance_debits_user_and_stock(client):
    response = client.post(
        "/orders",
        json={
            "user_id": 1,
            "product_ids": [1, 2],
            "payment_method": "balance",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["order_id"] == 1
    assert payload["total"] == 16.5
    assert payload["new_user_balance"] == 483.5

    with SessionLocal() as session:
        user = session.get(User, 1)
        product_1 = session.get(Product, 1)
        product_2 = session.get(Product, 2)
        orders = session.query(Order).all()

        assert user is not None
        assert user.balance == 483.5

        assert product_1 is not None
        assert product_1.stock == 9

        assert product_2 is not None
        assert product_2.stock == 4

        assert len(orders) == 1
        assert orders[0].payment_method == "balance"


def test_create_order_insufficient_balance_keeps_stock_and_order_unchanged(client):
    with SessionLocal() as session:
        user = session.get(User, 1)
        assert user is not None
        user.balance = 3.0
        session.add(user)
        session.commit()

    response = client.post(
        "/orders",
        json={
            "user_id": 1,
            "product_ids": [1],
            "payment_method": "balance",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient balance to process payment"

    with SessionLocal() as session:
        user = session.get(User, 1)
        product_1 = session.get(Product, 1)
        orders = session.query(Order).all()

        assert user is not None
        assert user.balance == 3.0

        assert product_1 is not None
        assert product_1.stock == 10

        assert len(orders) == 0


def test_create_order_with_unknown_product_returns_404(client):
    response = client.post(
        "/orders",
        json={
            "user_id": 1,
            "product_ids": [999],
            "payment_method": "balance",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product 999 does not exist"


def test_create_order_with_unsupported_payment_method_returns_400(client):
    response = client.post(
        "/orders",
        json={
            "user_id": 1,
            "product_ids": [1],
            "payment_method": "crypto",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported payment method 'crypto'. Use: balance, points"


def test_create_order_with_points_uses_points_processor(client):
    response = client.post(
        "/orders",
        json={
            "user_id": 1,
            "product_ids": [3],
            "payment_method": "points",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 2.5

    with SessionLocal() as session:
        orders = session.query(Order).all()
        assert len(orders) == 1
        assert orders[0].payment_method == "points"

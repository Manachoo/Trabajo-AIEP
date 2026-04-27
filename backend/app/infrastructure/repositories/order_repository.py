from app.infrastructure.models import Order


class OrderRepository:
    def __init__(self, session):
        self.session = session

    def create_order(self, user_id: int, total: float, status: str, payment_method: str) -> Order:
        order = Order(
            user_id=user_id,
            total=total,
            status=status,
            payment_method=payment_method,
        )
        self.session.add(order)
        self.session.flush()
        return order

from app.infrastructure.models import User


class UserRepository:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)

    def ensure_sufficient_balance(self, user: User, amount: float) -> None:
        if user.balance < amount:
            raise ValueError("Insufficient balance to process payment")

    def debit_balance(self, user: User, amount: float) -> None:
        user.balance = round(user.balance - amount, 2)
        self.session.add(user)

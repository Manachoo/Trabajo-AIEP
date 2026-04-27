from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.application.commands.order_command import OrderCommand
from app.domain.payment import PaymentProcessor, PaymentReceipt
from app.infrastructure.repositories.order_repository import OrderRepository
from app.infrastructure.repositories.product_repository import ProductRepository
from app.infrastructure.repositories.user_repository import UserRepository


@dataclass
class ProcessOrderResult:
    message: str
    order_id: int
    total: float
    new_user_balance: float


class ProcessOrderCommand(OrderCommand):
    def __init__(
        self,
        session: Session,
        user_repository: UserRepository,
        product_repository: ProductRepository,
        order_repository: OrderRepository,
        payment_processor: PaymentProcessor,
    ):
        self.session = session
        self.user_repository = user_repository
        self.product_repository = product_repository
        self.order_repository = order_repository
        self.payment_processor = payment_processor
        self._payment_receipt: PaymentReceipt | None = None

    def execute(self, user_id: int, product_ids: list[int]) -> ProcessOrderResult:
        if not product_ids:
            raise ValueError("At least one product is required")

        total = 0.0
        new_user_balance = 0.0
        order_id = 0

        try:
            with self.session.begin():
                user = self.user_repository.get_by_id(user_id)
                if user is None:
                    raise LookupError("User not found")

                products_by_id = self.product_repository.get_products_by_ids(product_ids)
                self.product_repository.reserve_stock(products_by_id, product_ids)

                total = self.product_repository.calculate_total(products_by_id, product_ids)
                self.user_repository.ensure_sufficient_balance(user, total)

                self._payment_receipt = self.payment_processor.charge(user_id=user.id, amount=total)
                self.user_repository.debit_balance(user=user, amount=total)
                new_user_balance = user.balance

                order = self.order_repository.create_order(
                    user_id=user.id,
                    total=total,
                    status="PAID",
                    payment_method=self._payment_receipt.method,
                )
                order_id = order.id
        except Exception:
            self.undo()
            raise

        return ProcessOrderResult(
            message="Order created, paid, and processed successfully",
            order_id=order_id,
            total=total,
            new_user_balance=new_user_balance,
        )

    def undo(self) -> None:
        if self._payment_receipt is None:
            return
        self.payment_processor.refund(self._payment_receipt)
        self._payment_receipt = None

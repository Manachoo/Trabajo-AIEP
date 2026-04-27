from sqlalchemy.orm import Session

from app.application.commands.process_order_command import ProcessOrderCommand, ProcessOrderResult
from app.infrastructure.payments.payment_factory import PaymentFactory
from app.infrastructure.repositories.order_repository import OrderRepository
from app.infrastructure.repositories.product_repository import ProductRepository
from app.infrastructure.repositories.user_repository import UserRepository


class OrderFacade:
    def __init__(self, session: Session, payment_factory: PaymentFactory | None = None):
        self.session = session
        self.payment_factory = payment_factory or PaymentFactory()

    def process_order(
        self,
        user_id: int,
        product_ids: list[int],
        payment_method: str = "balance",
    ) -> ProcessOrderResult:
        command = ProcessOrderCommand(
            session=self.session,
            user_repository=UserRepository(self.session),
            product_repository=ProductRepository(self.session),
            order_repository=OrderRepository(self.session),
            payment_processor=self.payment_factory.create(payment_method),
        )
        return command.execute(user_id=user_id, product_ids=product_ids)

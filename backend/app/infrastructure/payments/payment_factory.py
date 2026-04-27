from app.infrastructure.payments.balance_payment_processor import BalancePaymentProcessor
from app.infrastructure.payments.points_payment_processor import PointsPaymentProcessor


class PaymentFactory:
    _processors = {
        "balance": BalancePaymentProcessor,
        "points": PointsPaymentProcessor,
    }

    def create(self, payment_method: str):
        selected_method = payment_method.lower().strip() if payment_method else "balance"
        processor_class = self._processors.get(selected_method)
        if processor_class is None:
            supported_methods = ", ".join(sorted(self._processors.keys()))
            raise ValueError(f"Unsupported payment method '{selected_method}'. Use: {supported_methods}")
        return processor_class()

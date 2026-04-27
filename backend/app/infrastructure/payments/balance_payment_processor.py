from uuid import uuid4

from app.domain.payment import PaymentProcessor, PaymentReceipt


class BalancePaymentProcessor(PaymentProcessor):
    method = "balance"

    def charge(self, user_id: int, amount: float) -> PaymentReceipt:
        return PaymentReceipt(transaction_id=f"BAL-{uuid4().hex[:10]}", method=self.method)

    def refund(self, receipt: PaymentReceipt) -> None:
        return None

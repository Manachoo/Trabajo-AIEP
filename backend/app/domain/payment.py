from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class PaymentReceipt:
    transaction_id: str
    method: str


class PaymentProcessor(ABC):
    method: str

    @abstractmethod
    def charge(self, user_id: int, amount: float) -> PaymentReceipt:
        raise NotImplementedError

    @abstractmethod
    def refund(self, receipt: PaymentReceipt) -> None:
        raise NotImplementedError

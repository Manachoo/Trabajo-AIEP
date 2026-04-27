from abc import ABC, abstractmethod


class OrderCommand(ABC):
    @abstractmethod
    def execute(self, user_id: int, product_ids: list[int]):
        raise NotImplementedError

    @abstractmethod
    def undo(self) -> None:
        raise NotImplementedError

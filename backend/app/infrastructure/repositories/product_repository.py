from collections import Counter

from sqlalchemy import select

from app.infrastructure.models import Product


class ProductRepository:
    def __init__(self, session):
        self.session = session

    def list_available_products(self) -> list[Product]:
        statement = select(Product).where(Product.stock > 0).order_by(Product.id)
        return list(self.session.scalars(statement).all())

    def get_products_by_ids(self, product_ids: list[int]) -> dict[int, Product]:
        unique_ids = set(product_ids)
        if not unique_ids:
            return {}
        statement = select(Product).where(Product.id.in_(unique_ids))
        products = self.session.scalars(statement).all()
        return {product.id: product for product in products}

    def reserve_stock(self, products_by_id: dict[int, Product], product_ids: list[int]) -> None:
        requested_quantities = Counter(product_ids)

        for product_id, quantity in requested_quantities.items():
            product = products_by_id.get(product_id)
            if product is None:
                raise LookupError(f"Product {product_id} does not exist")
            if product.stock < quantity:
                raise ValueError(f"No stock available for product {product.name}")

            product.stock -= quantity
            self.session.add(product)

    def calculate_total(self, products_by_id: dict[int, Product], product_ids: list[int]) -> float:
        requested_quantities = Counter(product_ids)
        total = 0.0

        for product_id, quantity in requested_quantities.items():
            product = products_by_id[product_id]
            total += product.price * quantity

        return round(total, 2)

from pydantic import BaseModel, ConfigDict, Field, field_validator


class OrderRequest(BaseModel):
    user_id: int = Field(gt=0)
    product_ids: list[int] = Field(min_length=1)
    payment_method: str = Field(default="balance", min_length=1)

    @field_validator("product_ids")
    @classmethod
    def validate_product_ids(cls, product_ids: list[int]) -> list[int]:
        if any(product_id <= 0 for product_id in product_ids):
            raise ValueError("Product IDs must be greater than 0")
        return product_ids


class ProductResponse(BaseModel):
    id: int
    restaurant_id: int
    name: str
    price: float
    stock: int

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    message: str
    order_id: int
    total: float
    new_user_balance: float

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_order_facade
from app.api.schemas import OrderRequest, OrderResponse, ProductResponse
from app.application.facade.order_facade import OrderFacade
from app.infrastructure.database import get_session
from app.infrastructure.repositories.product_repository import ProductRepository

router = APIRouter()


@router.get("/products", response_model=list[ProductResponse])
def list_products(session: Session = Depends(get_session)):
    product_repository = ProductRepository(session)
    products = product_repository.list_available_products()
    return [ProductResponse.model_validate(product, from_attributes=True) for product in products]


@router.post("/orders", response_model=OrderResponse)
def create_order_endpoint(
    request: OrderRequest,
    order_facade: OrderFacade = Depends(get_order_facade),
):
    try:
        result = order_facade.process_order(
            user_id=request.user_id,
            product_ids=request.product_ids,
            payment_method=request.payment_method,
        )
        return OrderResponse(
            message=result.message,
            order_id=result.order_id,
            total=result.total,
            new_user_balance=result.new_user_balance,
        )
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

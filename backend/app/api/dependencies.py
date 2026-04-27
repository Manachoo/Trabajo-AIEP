from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.facade.order_facade import OrderFacade
from app.infrastructure.database import get_session


def get_order_facade(session: Session = Depends(get_session)) -> Generator[OrderFacade, None, None]:
    yield OrderFacade(session=session)

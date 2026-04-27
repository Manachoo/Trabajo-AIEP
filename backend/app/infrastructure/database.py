import os
from collections.abc import Generator

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://food_user:food_password@postgres:5432/food_delivery",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def init_database() -> None:
    from app.infrastructure.models import Product, Restaurant, User

    Base.metadata.create_all(bind=engine)

    with SessionLocal() as session:
        with session.begin():
            users_count = session.scalar(select(func.count(User.id))) or 0
            if users_count == 0:
                session.add(User(name="John Perez", balance=500.0))

            restaurants_count = session.scalar(select(func.count(Restaurant.id))) or 0
            if restaurants_count == 0:
                restaurant = Restaurant(name="The Burger Place", is_active=True)
                session.add(restaurant)
                session.flush()
                _ensure_default_products(session, restaurant.id)
            else:
                restaurant = session.scalar(select(Restaurant).order_by(Restaurant.id).limit(1))
                if restaurant is not None:
                    _ensure_default_products(session, restaurant.id)


def _ensure_default_products(session: Session, restaurant_id: int) -> None:
    from app.infrastructure.models import Product

    existing_names = set(
        session.scalars(select(Product.name).where(Product.restaurant_id == restaurant_id)).all()
    )

    default_products = [
        ("Double Burger", 12.50, 10),
        ("French Fries", 4.00, 5),
        ("Soda", 2.50, 20),
    ]

    for name, price, stock in default_products:
        if name in existing_names:
            continue
        session.add(Product(restaurant_id=restaurant_id, name=name, price=price, stock=stock))

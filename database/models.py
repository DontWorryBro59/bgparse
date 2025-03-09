from sqlalchemy import String, Float
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ProductModels(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(String(150), index=True)
    category_name: Mapped[str] = mapped_column(String(150), index=True)
    item_name: Mapped[str] = mapped_column(String(150), index=True)
    price: Mapped[float] = mapped_column(Float)
    density: Mapped[float] = mapped_column(Float)
    size: Mapped[str] = mapped_column(String(15))
    quantity: Mapped[str] = mapped_column(String(15))

    def __repr__(self) -> str:
        return f'{self.product_name} | {self.category_name} | {self.item_name} | {self.price} | {self.density} | {self.size} | {self.quantity}'

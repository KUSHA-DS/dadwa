from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SaleBase(BaseModel):
    """Base sale schema."""
    product_id: int
    quantity: int
    total_price: float


class SaleCreate(BaseModel):
    """Schema for creating a sale."""
    product_id: int
    quantity: int


class Sale(SaleBase):
    """Sale schema with ID and timestamp."""
    id: int
    sale_date: datetime

    class Config:
        from_attributes = True

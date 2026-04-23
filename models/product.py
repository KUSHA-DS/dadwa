from pydantic import BaseModel
from typing import Optional


class ProductBase(BaseModel):
    """Base product schema."""
    name: str
    category: str
    price: float
    stock: int
    description: Optional[str] = None


class ProductCreate(ProductBase):
    """Schema for creating a product."""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product."""
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    description: Optional[str] = None


class Product(ProductBase):
    """Product schema with ID."""
    id: int

    class Config:
        from_attributes = True

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from models.product import Product, ProductCreate, ProductUpdate
from auth.security import get_api_key
from database import get_db_connection

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=List[Product])
async def get_all_products(
    category: Optional[str] = None,
    search: Optional[str] = None
):
    """Get all products with optional filtering."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM products WHERE 1=1"
    params = []
    
    if category:
        query += " AND category = ?"
        params.append(category)
    
    if search:
        query += " AND (name LIKE ? OR description LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    
    cursor.execute(query, params)
    products = cursor.fetchall()
    conn.close()
    
    return [dict(p) for p in products]


@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: int):
    """Get a specific product by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    conn.close()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return dict(product)


@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    api_key: str = Depends(get_api_key)
):
    """Create a new product (requires API key)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """INSERT INTO products (name, category, price, stock, description)
           VALUES (?, ?, ?, ?, ?)""",
        (product.name, product.category, product.price, product.stock, product.description)
    )
    
    product_id = cursor.lastrowid
    conn.commit()
    
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    new_product = cursor.fetchone()
    conn.close()
    
    return dict(new_product)


@router.put("/{product_id}", response_model=Product)
async def update_product(
    product_id: int,
    product: ProductUpdate,
    api_key: str = Depends(get_api_key)
):
    """Update a product (requires API key)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if product exists
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    existing = cursor.fetchone()
    
    if not existing:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Build update query dynamically
    updates = []
    params = []
    
    if product.name is not None:
        updates.append("name = ?")
        params.append(product.name)
    if product.category is not None:
        updates.append("category = ?")
        params.append(product.category)
    if product.price is not None:
        updates.append("price = ?")
        params.append(product.price)
    if product.stock is not None:
        updates.append("stock = ?")
        params.append(product.stock)
    if product.description is not None:
        updates.append("description = ?")
        params.append(product.description)
    
    if updates:
        params.append(product_id)
        cursor.execute(
            f"UPDATE products SET {', '.join(updates)} WHERE id = ?",
            params
        )
        conn.commit()
    
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    updated_product = cursor.fetchone()
    conn.close()
    
    return dict(updated_product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    api_key: str = Depends(get_api_key)
):
    """Delete a product (requires API key)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()

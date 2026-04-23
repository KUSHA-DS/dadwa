from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime
from models.sale import Sale, SaleCreate
from auth.security import get_api_key
from database import get_db_connection

router = APIRouter(prefix="/sales", tags=["Sales"])


@router.get("/", response_model=List[Sale])
async def get_all_sales():
    """Get all sales records."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sales ORDER BY sale_date DESC")
    sales = cursor.fetchall()
    conn.close()
    
    return [dict(s) for s in sales]


@router.post("/", response_model=Sale, status_code=status.HTTP_201_CREATED)
async def create_sale(
    sale: SaleCreate,
    api_key: str = Depends(get_api_key)
):
    """Create a new sale and update product stock (requires API key)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if product exists and has enough stock
    cursor.execute("SELECT * FROM products WHERE id = ?", (sale.product_id,))
    product = cursor.fetchone()
    
    if not product:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    if product["stock"] < sale.quantity:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Not enough stock. Available: {product['stock']}"
        )
    
    # Calculate total price
    total_price = product["price"] * sale.quantity
    
    # Create sale record
    cursor.execute(
        """INSERT INTO sales (product_id, quantity, total_price, sale_date)
           VALUES (?, ?, ?, ?)""",
        (sale.product_id, sale.quantity, total_price, datetime.now().isoformat())
    )
    
    # Update product stock
    new_stock = product["stock"] - sale.quantity
    cursor.execute(
        "UPDATE products SET stock = ? WHERE id = ?",
        (new_stock, sale.product_id)
    )
    
    sale_id = cursor.lastrowid
    conn.commit()
    
    cursor.execute("SELECT * FROM sales WHERE id = ?", (sale_id,))
    new_sale = cursor.fetchone()
    conn.close()
    
    return dict(new_sale)


@router.get("/stats")
async def get_sales_stats():
    """Get sales statistics."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total sales
    cursor.execute("SELECT COUNT(*) as count, SUM(total_price) as total FROM sales")
    stats = cursor.fetchone()
    
    # Top selling products
    cursor.execute("""
        SELECT p.name, SUM(s.quantity) as total_sold, SUM(s.total_price) as revenue
        FROM sales s
        JOIN products p ON s.product_id = p.id
        GROUP BY p.id
        ORDER BY total_sold DESC
        LIMIT 5
    """)
    top_products = cursor.fetchall()
    
    conn.close()
    
    return {
        "total_sales": stats["count"] or 0,
        "total_revenue": stats["total"] or 0,
        "top_products": [dict(p) for p in top_products]
    }

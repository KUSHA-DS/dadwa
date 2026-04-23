import fastapi
import fastapi.middleware.cors
from pydantic import BaseModel
from typing import Optional
import sqlite3
import os
from contextlib import contextmanager
from datetime import datetime

app = fastapi.FastAPI()

app.add_middleware(
    fastapi.middleware.cors.CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), "boxing_shop.db")


@contextmanager
def get_db():
    """Get database connection with context manager."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Initialize database with tables."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                stock INTEGER NOT NULL DEFAULT 0,
                size TEXT,
                color TEXT,
                image_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Stock history table for tracking changes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                change_amount INTEGER NOT NULL,
                change_type TEXT NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        """)
        
        # Categories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT
            )
        """)
        
        # Insert default categories
        default_categories = [
            ("Doreza", "Doreza boksi - profesionale dhe amatore"),
            ("Tesha", "Tesha boksi - shorte dhe bluza"),
            ("Atlete", "Atlete boksi - speciale per ring"),
            ("Koka", "Mbrojtese koke dhe helmet"),
            ("Thes", "Thes boksi dhe pajisje stervitje"),
            ("Aksesor", "Aksesorë të ndryshëm boksi")
        ]
        
        for cat_name, cat_desc in default_categories:
            try:
                cursor.execute(
                    "INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)",
                    (cat_name, cat_desc)
                )
            except sqlite3.IntegrityError:
                pass
        
        conn.commit()


# Initialize database on startup
init_db()


# Pydantic models
class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    price: float
    stock: int = 0
    size: Optional[str] = None
    color: Optional[str] = None
    image_url: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    size: Optional[str] = None
    color: Optional[str] = None
    image_url: Optional[str] = None


class StockChange(BaseModel):
    amount: int
    change_type: str  # "add" or "remove"
    notes: Optional[str] = None


class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None


# API Routes
@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/products")
async def get_products(category: Optional[str] = None, search: Optional[str] = None):
    """Get all products with optional filtering."""
    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM products WHERE 1=1"
        params = []
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if search:
            query += " AND (name LIKE ? OR description LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])
        
        query += " ORDER BY created_at DESC"
        cursor.execute(query, params)
        products = [dict(row) for row in cursor.fetchall()]
        return products


@app.get("/products/{product_id}")
async def get_product(product_id: int):
    """Get a single product by ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()
        if not product:
            raise fastapi.HTTPException(status_code=404, detail="Produkti nuk u gjet")
        return dict(product)


@app.post("/products")
async def create_product(product: ProductCreate):
    """Create a new product."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO products (name, description, category, price, stock, size, color, image_url)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (product.name, product.description, product.category, product.price,
             product.stock, product.size, product.color, product.image_url)
        )
        conn.commit()
        product_id = cursor.lastrowid
        
        # Add initial stock history if stock > 0
        if product.stock > 0:
            cursor.execute(
                """INSERT INTO stock_history (product_id, change_amount, change_type, notes)
                   VALUES (?, ?, ?, ?)""",
                (product_id, product.stock, "add", "Stok fillestar")
            )
            conn.commit()
        
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        return dict(cursor.fetchone())


@app.put("/products/{product_id}")
async def update_product(product_id: int, product: ProductUpdate):
    """Update a product."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Get current product
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        existing = cursor.fetchone()
        if not existing:
            raise fastapi.HTTPException(status_code=404, detail="Produkti nuk u gjet")
        
        # Build update query
        updates = []
        params = []
        for field, value in product.model_dump(exclude_unset=True).items():
            if value is not None:
                updates.append(f"{field} = ?")
                params.append(value)
        
        if updates:
            updates.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            params.append(product_id)
            
            query = f"UPDATE products SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
        
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        return dict(cursor.fetchone())


@app.delete("/products/{product_id}")
async def delete_product(product_id: int):
    """Delete a product."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        if not cursor.fetchone():
            raise fastapi.HTTPException(status_code=404, detail="Produkti nuk u gjet")
        
        cursor.execute("DELETE FROM stock_history WHERE product_id = ?", (product_id,))
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        return {"message": "Produkti u fshi me sukses"}


@app.post("/products/{product_id}/stock")
async def update_stock(product_id: int, stock_change: StockChange):
    """Update product stock (add or remove)."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()
        if not product:
            raise fastapi.HTTPException(status_code=404, detail="Produkti nuk u gjet")
        
        current_stock = product["stock"]
        
        if stock_change.change_type == "add":
            new_stock = current_stock + stock_change.amount
        elif stock_change.change_type == "remove":
            new_stock = current_stock - stock_change.amount
            if new_stock < 0:
                raise fastapi.HTTPException(
                    status_code=400,
                    detail=f"Nuk keni stok të mjaftueshëm. Stoku aktual: {current_stock}"
                )
        else:
            raise fastapi.HTTPException(status_code=400, detail="Lloji i ndryshimit duhet të jetë 'add' ose 'remove'")
        
        # Update stock
        cursor.execute(
            "UPDATE products SET stock = ?, updated_at = ? WHERE id = ?",
            (new_stock, datetime.now().isoformat(), product_id)
        )
        
        # Record history
        cursor.execute(
            """INSERT INTO stock_history (product_id, change_amount, change_type, notes)
               VALUES (?, ?, ?, ?)""",
            (product_id, stock_change.amount, stock_change.change_type, stock_change.notes)
        )
        conn.commit()
        
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        return dict(cursor.fetchone())


@app.get("/products/{product_id}/history")
async def get_stock_history(product_id: int):
    """Get stock history for a product."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM stock_history WHERE product_id = ? ORDER BY created_at DESC""",
            (product_id,)
        )
        history = [dict(row) for row in cursor.fetchall()]
        return history


@app.get("/categories")
async def get_categories():
    """Get all categories."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM categories ORDER BY name")
        categories = [dict(row) for row in cursor.fetchall()]
        return categories


@app.post("/categories")
async def create_category(category: CategoryCreate):
    """Create a new category."""
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO categories (name, description) VALUES (?, ?)",
                (category.name, category.description)
            )
            conn.commit()
            category_id = cursor.lastrowid
            cursor.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
            return dict(cursor.fetchone())
        except sqlite3.IntegrityError:
            raise fastapi.HTTPException(status_code=400, detail="Kategoria ekziston tashmë")


@app.get("/stats")
async def get_stats():
    """Get dashboard statistics."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Total products
        cursor.execute("SELECT COUNT(*) as count FROM products")
        total_products = cursor.fetchone()["count"]
        
        # Total stock value
        cursor.execute("SELECT SUM(price * stock) as value FROM products")
        total_value = cursor.fetchone()["value"] or 0
        
        # Low stock products (less than 5)
        cursor.execute("SELECT COUNT(*) as count FROM products WHERE stock < 5")
        low_stock = cursor.fetchone()["count"]
        
        # Out of stock
        cursor.execute("SELECT COUNT(*) as count FROM products WHERE stock = 0")
        out_of_stock = cursor.fetchone()["count"]
        
        # Products by category
        cursor.execute("""
            SELECT category, COUNT(*) as count, SUM(stock) as total_stock
            FROM products GROUP BY category
        """)
        by_category = [dict(row) for row in cursor.fetchall()]
        
        return {
            "total_products": total_products,
            "total_value": round(total_value, 2),
            "low_stock": low_stock,
            "out_of_stock": out_of_stock,
            "by_category": by_category
        }

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import os
from contextlib import contextmanager
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'boxing-shop-secret-key-2024'

# Database path - use /tmp for Vercel serverless
DB_PATH = "/tmp/boxing_shop.db"

# Categories
CATEGORIES = [
    {"value": "doreza", "label": "Doreza Boksi"},
    {"value": "tesha", "label": "Tesha Boksi"},
    {"value": "atlete", "label": "Atlete"},
    {"value": "pantallona", "label": "Pantallona"},
    {"value": "koka", "label": "Mbrojtese Koke"},
    {"value": "dhembe", "label": "Mbrojtese Dhembesh"},
    {"value": "traste", "label": "Traste Boksi"},
    {"value": "thes", "label": "Thes Boksi"},
    {"value": "tjeter", "label": "Tjeter"},
]


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
                min_stock INTEGER NOT NULL DEFAULT 5,
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
        
        conn.commit()


# Initialize database on startup
init_db()


def get_stats():
    """Get dashboard statistics."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as count FROM products")
        total_products = cursor.fetchone()["count"]
        
        cursor.execute("SELECT COALESCE(SUM(stock), 0) as total FROM products")
        total_stock = cursor.fetchone()["total"]
        
        cursor.execute("SELECT COUNT(*) as count FROM products WHERE stock <= min_stock")
        low_stock_count = cursor.fetchone()["count"]
        
        cursor.execute("SELECT COALESCE(SUM(price * stock), 0) as value FROM products")
        total_value = cursor.fetchone()["value"]
        
        return {
            "total_products": total_products,
            "total_stock": total_stock,
            "low_stock_count": low_stock_count,
            "total_value": round(total_value, 2)
        }


def get_category_label(value):
    """Get category label from value."""
    for cat in CATEGORIES:
        if cat["value"] == value:
            return cat["label"]
    return value


@app.route("/")
def index():
    """Main page - show all products."""
    search = request.args.get("search", "")
    category = request.args.get("category", "")
    
    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM products WHERE 1=1"
        params = []
        
        if search:
            query += " AND (name LIKE ? OR description LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        query += " ORDER BY created_at DESC"
        cursor.execute(query, params)
        products = [dict(row) for row in cursor.fetchall()]
    
    stats = get_stats()
    
    return render_template("index.html", 
                         products=products, 
                         stats=stats, 
                         categories=CATEGORIES,
                         search=search,
                         category_filter=category,
                         get_category_label=get_category_label)


@app.route("/product/add", methods=["GET", "POST"])
def add_product():
    """Add a new product."""
    if request.method == "POST":
        name = request.form.get("name")
        category = request.form.get("category")
        size = request.form.get("size") or None
        color = request.form.get("color") or None
        price = float(request.form.get("price", 0))
        stock = int(request.form.get("stock", 0))
        min_stock = int(request.form.get("min_stock", 5))
        image_url = request.form.get("image_url") or None
        description = request.form.get("description") or None
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO products (name, description, category, price, stock, min_stock, size, color, image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, description, category, price, stock, min_stock, size, color, image_url))
            
            product_id = cursor.lastrowid
            
            if stock > 0:
                cursor.execute("""
                    INSERT INTO stock_history (product_id, change_amount, change_type, notes)
                    VALUES (?, ?, ?, ?)
                """, (product_id, stock, "add", "Stok fillestar"))
            
            conn.commit()
        
        flash("Produkti u shtua me sukses!", "success")
        return redirect(url_for("index"))
    
    return render_template("product_form.html", 
                         product=None, 
                         categories=CATEGORIES,
                         title="Shto Produkt te Ri")


@app.route("/product/edit/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    """Edit an existing product."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()
        
        if not product:
            flash("Produkti nuk u gjet!", "error")
            return redirect(url_for("index"))
        
        product = dict(product)
    
    if request.method == "POST":
        name = request.form.get("name")
        category = request.form.get("category")
        size = request.form.get("size") or None
        color = request.form.get("color") or None
        price = float(request.form.get("price", 0))
        stock = int(request.form.get("stock", 0))
        min_stock = int(request.form.get("min_stock", 5))
        image_url = request.form.get("image_url") or None
        description = request.form.get("description") or None
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE products 
                SET name=?, description=?, category=?, price=?, stock=?, min_stock=?, size=?, color=?, image_url=?, updated_at=?
                WHERE id=?
            """, (name, description, category, price, stock, min_stock, size, color, image_url, datetime.now().isoformat(), product_id))
            conn.commit()
        
        flash("Produkti u ndryshua me sukses!", "success")
        return redirect(url_for("index"))
    
    return render_template("product_form.html", 
                         product=product, 
                         categories=CATEGORIES,
                         title="Ndrysho Produktin")


@app.route("/product/delete/<int:product_id>", methods=["POST"])
def delete_product(product_id):
    """Delete a product."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM stock_history WHERE product_id = ?", (product_id,))
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
    
    flash("Produkti u fshi me sukses!", "success")
    return redirect(url_for("index"))


@app.route("/product/stock/<int:product_id>/<action>", methods=["POST"])
def update_stock(product_id, action):
    """Update product stock (add or remove 1)."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT stock FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()
        
        if not product:
            flash("Produkti nuk u gjet!", "error")
            return redirect(url_for("index"))
        
        current_stock = product["stock"]
        
        if action == "add":
            new_stock = current_stock + 1
            change_type = "add"
        elif action == "remove":
            if current_stock <= 0:
                flash("Nuk keni stok te mjaftueshem!", "error")
                return redirect(url_for("index"))
            new_stock = current_stock - 1
            change_type = "remove"
        else:
            flash("Veprim i panjohur!", "error")
            return redirect(url_for("index"))
        
        cursor.execute("""
            UPDATE products SET stock = ?, updated_at = ? WHERE id = ?
        """, (new_stock, datetime.now().isoformat(), product_id))
        
        cursor.execute("""
            INSERT INTO stock_history (product_id, change_amount, change_type, notes)
            VALUES (?, ?, ?, ?)
        """, (product_id, 1, change_type, "Ndryshim manual"))
        
        conn.commit()
    
    return redirect(url_for("index"))


# Export for Vercel
application = app

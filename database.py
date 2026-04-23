import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "shop.db")


def get_db_connection():
    """Create a database connection."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database with tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0,
            description TEXT
        )
    """)
    
    # Create sales table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            total_price REAL NOT NULL,
            sale_date TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    """)
    
    # Add sample data if empty
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        sample_products = [
            ("Doreza Boksi Everlast", "Doreza", 49.99, 25, "Doreza profesionale per boks"),
            ("Doreza Boksi Venum", "Doreza", 59.99, 20, "Doreza premium per stervitje"),
            ("Thes Boksi 100kg", "Thes", 149.99, 10, "Thes i madh per stervitje intensive"),
            ("Thes Boksi 50kg", "Thes", 89.99, 15, "Thes mesatar per fillestare"),
            ("Kaska Mbrojtese", "Mbrojtje", 39.99, 30, "Kaska per sparring"),
            ("Mbrojtese Dhembesh", "Mbrojtje", 9.99, 50, "Mbrojtese per dhembet"),
            ("Fasheta Dore", "Aksesore", 12.99, 40, "Fasheta per mbrojte te duarve"),
            ("Kepuce Boksi", "Kepuce", 79.99, 18, "Kepuce te lehta per ring"),
            ("Shорц Boksi", "Veshje", 29.99, 35, "Shortsa per ndeshje"),
            ("Litare Kercimi", "Aksesore", 14.99, 45, "Litar per ngrohje")
        ]
        
        cursor.executemany(
            "INSERT INTO products (name, category, price, stock, description) VALUES (?, ?, ?, ?, ?)",
            sample_products
        )
    
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")

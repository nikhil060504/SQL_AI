import sqlite3
import random
from datetime import datetime, timedelta

# Create or connect to the SQLite database
# Node.js Equivalent: This is similar to const db = new sqlite3.Database('ecommerce.db');
def setup_database():
    """
    Sets up the database, creates tables (Users, Products, Orders) if they don't exist,
    and populates them with dummy data.
    """
    # Connect to the SQLite database. It will create 'ecommerce.db' if it doesn't exist.
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()

    # --- 1. Create Tables ---
    
    # Create Users table
    # Node.js Equivalent: Running a standard CREATE TABLE query using db.run()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        signup_date TEXT NOT NULL
    )
    ''')

    # Create Products table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL,
        stock_quantity INTEGER NOT NULL
    )
    ''')

    # Create Orders table (links Users and Products)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        order_date TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        total_price REAL NOT NULL,
        FOREIGN KEY(user_id) REFERENCES Users(id),
        FOREIGN KEY(product_id) REFERENCES Products(id)
    )
    ''')

    # --- 2. Check if data exists ---
    # We only want to insert dummy data if the tables are empty
    cursor.execute('SELECT COUNT(*) FROM Users')
    if cursor.fetchone()[0] == 0:
        print("Populating database with realistic dummy data...")
        populate_dummy_data(cursor)
        conn.commit()
    else:
        print("Database already populated.")

    # Close the connection
    # Node.js Equivalent: db.close()
    conn.close()

def populate_dummy_data(cursor):
    """
    Generates 50 rows of dummy data for each table.
    """
    # Dummy data arrays for realistic generation
    first_names = ['John', 'Jane', 'Alex', 'Emily', 'Chris', 'Sarah', 'Mike', 'Jessica', 'David', 'Ashley']
    last_names = ['Smith', 'Doe', 'Johnson', 'Brown', 'Taylor', 'Anderson', 'Thomas', 'Jackson', 'White', 'Harris']
    categories = ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Toys']
    product_adjectives = ['Premium', 'Wireless', 'Smart', 'Eco-friendly', 'Portable']
    product_nouns = ['Headphones', 'Speaker', 'Monitor', 'Jacket', 'Watch']

    # Insert 50 Users
    # Node.js Equivalent: This is like a for loop running INSERT queries or bulk insert.
    for _ in range(50):
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        email = f"{name.lower().replace(' ', '.')}@example.com"
        # Generate a random date within the last year
        days_ago = random.randint(0, 365)
        signup_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        
        # INSERT OR IGNORE handles potential duplicate emails smoothly
        cursor.execute('INSERT OR IGNORE INTO Users (name, email, signup_date) VALUES (?, ?, ?)', 
                       (name, email, signup_date))

    # Insert 50 Products
    for _ in range(50):
        name = f"{random.choice(product_adjectives)} {random.choice(product_nouns)}"
        category = random.choice(categories)
        price = round(random.uniform(10.0, 500.0), 2)
        stock_quantity = random.randint(0, 100)
        
        cursor.execute('INSERT INTO Products (name, category, price, stock_quantity) VALUES (?, ?, ?, ?)', 
                       (name, category, price, stock_quantity))

    # Insert 50 Orders
    for _ in range(50):
        user_id = random.randint(1, 50)
        product_id = random.randint(1, 50)
        
        # Fetch the product's price to calculate the order total
        cursor.execute('SELECT price FROM Products WHERE id = ?', (product_id,))
        result = cursor.fetchone()
        
        if result:
            price_per_unit = result[0]
            quantity = random.randint(1, 5)
            total_price = round(price_per_unit * quantity, 2)
            
            # Order date within the last 30 days
            days_ago = random.randint(0, 30)
            order_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            
            cursor.execute('''
            INSERT INTO Orders (user_id, product_id, order_date, quantity, total_price) 
            VALUES (?, ?, ?, ?, ?)
            ''', (user_id, product_id, order_date, quantity, total_price))

if __name__ == '__main__':
    # Run setup when the script is executed directly
    # Node.js Equivalent: if (require.main === module) { setupDatabase(); }
    setup_database()

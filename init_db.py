import sqlite3
import os

def build_database():
    print("Initializing SQLite database using Python...")
    
    # Connect to (or create) database.db
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Read and execute schema.sql
    if os.path.exists("schema.sql"):
        with open("schema.sql", "r", encoding="utf-8") as f:
            schema_script = f.read()
            cursor.executescript(schema_script)
        print("✓ Tables created successfully from schema.sql.")
    else:
        print("✕ Error: schema.sql file not found!")

    # 2. Read and execute seed.sql if present
    if os.path.exists("seed.sql"):
        with open("seed.sql", "r", encoding="utf-8") as f:
            seed_script = f.read()
            cursor.executescript(seed_script)
        print("✓ Sample data inserted successfully from seed.sql.")

    # Commit changes and close
    conn.commit()
    conn.close()
    print("\nDatabase initialization complete! 'database.db' is ready.")

if __name__ == "__main__":
    build_database()
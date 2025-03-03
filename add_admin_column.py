import sqlite3
import os

# Path to the database file
db_path = os.path.join('instance', 'database.db')

def add_is_admin_column():
    """Add the is_admin column to the user table"""
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_admin' not in columns:
            print("Adding is_admin column to user table...")
            # Add the is_admin column with a default value of 0 (False)
            cursor.execute("ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT 0")
            conn.commit()
            print("Column added successfully!")
        else:
            print("The is_admin column already exists.")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Current user table columns: {columns}")
        
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return False

if __name__ == "__main__":
    if os.path.exists(db_path):
        print(f"Database found at {db_path}")
        add_is_admin_column()
    else:
        print(f"Database not found at {db_path}") 
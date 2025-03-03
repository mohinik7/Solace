import sqlite3
import os

# Path to the database file
db_path = os.path.join('instance', 'database.db')

def check_user_table():
    """Check the structure of the user table"""
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute("PRAGMA table_info(user)")
        columns = cursor.fetchall()
        
        print("User table structure:")
        for column in columns:
            print(f"Column: {column[1]}, Type: {column[2]}, NotNull: {column[3]}, DefaultValue: {column[4]}, PK: {column[5]}")
        
        # Check if there are any users in the table
        cursor.execute("SELECT * FROM user LIMIT 5")
        users = cursor.fetchall()
        
        print(f"\nFound {len(users)} users in the database")
        if users:
            print("\nUser data (first 5 users):")
            for user in users:
                # Don't print the password
                safe_user = list(user)
                if len(safe_user) > 2:  # Make sure there's a password field
                    safe_user[2] = "********"  # Mask the password
                print(safe_user)
        
        conn.close()
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")

if __name__ == "__main__":
    if os.path.exists(db_path):
        print(f"Database found at {db_path}")
        check_user_table()
    else:
        print(f"Database not found at {db_path}") 
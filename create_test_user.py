import os
import sqlite3
from werkzeug.security import generate_password_hash

# Database path
db_path = os.path.join('instance', 'database.db')

def create_test_user(email, password, first_name, is_admin=False):
    """Create a test user in the database"""
    try:
        # Make sure the database exists
        if not os.path.exists(db_path):
            print(f"Database not found at {db_path}")
            return False
        
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT id FROM user WHERE email = ?", (email,))
        user = cursor.fetchone()
        
        if user:
            print(f"User with email {email} already exists (ID: {user[0]})")
            choice = input("Update this user? (y/n): ").lower()
            if choice != 'y':
                conn.close()
                return False
            
            # Update existing user
            hashed_password = generate_password_hash(password)
            cursor.execute(
                "UPDATE user SET password = ?, first_name = ?, is_admin = ? WHERE email = ?",
                (hashed_password, first_name, 1 if is_admin else 0, email)
            )
            conn.commit()
            print(f"User {email} updated successfully")
        else:
            # Create new user
            hashed_password = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO user (email, password, first_name, is_admin) VALUES (?, ?, ?, ?)",
                (email, hashed_password, first_name, 1 if is_admin else 0)
            )
            conn.commit()
            print(f"User {email} created successfully")
        
        # Verify the user was created/updated
        cursor.execute("SELECT id, email, first_name, is_admin FROM user WHERE email = ?", (email,))
        user = cursor.fetchone()
        print(f"User details: ID={user[0]}, Email={user[1]}, Name={user[2]}, Admin={user[3]}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating/updating user: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("CREATE TEST USER")
    print("=" * 50)
    
    # Get user details
    email = input("Enter email (default: test@example.com): ") or "test@example.com"
    password = input("Enter password (default: password123): ") or "password123"
    first_name = input("Enter first name (default: Test User): ") or "Test User"
    is_admin_input = input("Make user an admin? (y/n) (default: y): ").lower() or "y"
    is_admin = is_admin_input == "y"
    
    # Create the user
    if create_test_user(email, password, first_name, is_admin):
        print("\nTest user created/updated successfully!")
        print(f"You can now log in with:")
        print(f"Email: {email}")
        print(f"Password: {password}")
    else:
        print("\nFailed to create/update test user") 
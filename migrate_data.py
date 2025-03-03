import sqlite3
import os
import shutil
from datetime import datetime

# Database paths
root_db_path = 'database.db'
instance_db_path = os.path.join('instance', 'database.db')

def backup_database(db_path):
    """Create a backup of the database"""
    if os.path.exists(db_path) and os.path.getsize(db_path) > 0:
        backup_path = f"{db_path}.backup.{datetime.now().strftime('%Y%m%d%H%M%S')}"
        shutil.copy2(db_path, backup_path)
        print(f"Created backup at {backup_path}")
        return backup_path
    return None

def copy_user_data():
    """Copy user data from root database to instance database"""
    # Check if root database exists and has data
    if not os.path.exists(root_db_path) or os.path.getsize(root_db_path) == 0:
        print("Root database doesn't exist or is empty. No data to migrate.")
        return False
    
    # Backup both databases before migration
    backup_database(root_db_path)
    backup_database(instance_db_path)
    
    try:
        # Connect to both databases
        root_conn = sqlite3.connect(root_db_path)
        root_cursor = root_conn.cursor()
        
        instance_conn = sqlite3.connect(instance_db_path)
        instance_cursor = instance_conn.cursor()
        
        # Check if the user table exists in root database
        root_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
        if not root_cursor.fetchone():
            print("No user table found in root database.")
            return False
        
        # Get user data from root database
        root_cursor.execute("SELECT * FROM user")
        users = root_cursor.fetchall()
        
        if not users:
            print("No user data found in root database.")
            return False
        
        print(f"Found {len(users)} users in root database.")
        
        # Get column names from root database
        root_cursor.execute("PRAGMA table_info(user)")
        root_columns = [column[1] for column in root_cursor.fetchall()]
        
        # Get column names from instance database
        instance_cursor.execute("PRAGMA table_info(user)")
        instance_columns = [column[1] for column in instance_cursor.fetchall()]
        
        print(f"Root database columns: {root_columns}")
        print(f"Instance database columns: {instance_columns}")
        
        # Check for existing users in instance database to avoid duplicates
        for user in users:
            # Extract email from the user tuple (assuming it's in the same position)
            email_index = root_columns.index('email') if 'email' in root_columns else 1
            email = user[email_index]
            
            # Check if user already exists in instance database
            instance_cursor.execute("SELECT id FROM user WHERE email = ?", (email,))
            existing_user = instance_cursor.fetchone()
            
            if existing_user:
                print(f"User with email {email} already exists in instance database. Skipping.")
                continue
            
            # Prepare insert query based on available columns
            available_columns = [col for col in root_columns if col in instance_columns]
            
            # Add is_admin with default value if it exists in instance but not in root
            if 'is_admin' in instance_columns and 'is_admin' not in root_columns:
                available_columns.append('is_admin')
                # Create a new user tuple with is_admin=0 appended
                user_values = list(user)
                user_values.append(0)  # Default is_admin to False
                user = tuple(user_values)
            
            placeholders = ', '.join(['?' for _ in available_columns])
            columns_str = ', '.join(available_columns)
            
            # Extract values for available columns
            values = []
            for col in available_columns:
                if col in root_columns:
                    idx = root_columns.index(col)
                    values.append(user[idx])
                elif col == 'is_admin':
                    values.append(0)  # Default value for is_admin
            
            # Insert user into instance database
            query = f"INSERT INTO user ({columns_str}) VALUES ({placeholders})"
            instance_cursor.execute(query, values)
            
            print(f"Migrated user with email {email} to instance database.")
        
        # Commit changes
        instance_conn.commit()
        
        # Close connections
        root_conn.close()
        instance_conn.close()
        
        print("Migration completed successfully.")
        return True
    
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return False

if __name__ == "__main__":
    print("Starting data migration...")
    copy_user_data()
    print("Migration process completed.") 
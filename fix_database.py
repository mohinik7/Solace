import os
import shutil
import sqlite3
from datetime import datetime

try:
    from werkzeug.security import generate_password_hash
    has_werkzeug = True
except ImportError:
    has_werkzeug = False
    print("Warning: werkzeug not installed. Will use basic hash for password.")

# Database paths and configuration
instance_dir = 'instance'
db_name = 'database.db'
db_path = os.path.join(instance_dir, db_name)
backup_suffix = f".backup.{datetime.now().strftime('%Y%m%d%H%M%S')}"
backup_path = db_path + backup_suffix

def create_backup():
    """Create a backup of the current database file"""
    if os.path.exists(db_path):
        print(f"Creating backup of existing database to {backup_path}...")
        shutil.copy2(db_path, backup_path)
        return True
    return False

def create_new_database():
    """Create a new database with the required schema"""
    print("Creating new database with required schema...")
    
    # Ensure the instance directory exists
    if not os.path.exists(instance_dir):
        os.makedirs(instance_dir)
        print(f"Created instance directory: {instance_dir}")
    
    # Create the database file
    try:
        # Remove existing file if it exists
        if os.path.exists(db_path):
            os.remove(db_path)
            print("Removed existing database file")
        
        # Create a new database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create user table with required schema
        cursor.execute('''
        CREATE TABLE user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email VARCHAR(150) UNIQUE,
            password VARCHAR(150),
            first_name VARCHAR(150),
            is_admin BOOLEAN DEFAULT 0
        )
        ''')
        
        # Create chat_session table
        cursor.execute('''
        CREATE TABLE chat_session (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            session_name VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user (id)
        )
        ''')
        
        # Create chat_message table
        cursor.execute('''
        CREATE TABLE chat_message (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_session_id INTEGER NOT NULL,
            role VARCHAR(10),
            message TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (chat_session_id) REFERENCES chat_session (id)
        )
        ''')
        
        # Create mood_entry table
        cursor.execute('''
        CREATE TABLE mood_entry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_session_id INTEGER NOT NULL,
            sentiment_score FLOAT NOT NULL,
            key_phrases TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (chat_session_id) REFERENCES chat_session (id) ON DELETE CASCADE
        )
        ''')
        
        conn.commit()
        conn.close()
        
        print(f"New database created successfully at {db_path}")
        return True
    except Exception as e:
        print(f"Error creating new database: {e}")
        return False

def migrate_user_data():
    """Try to migrate user data from the backup if it exists"""
    if not os.path.exists(backup_path):
        print("No backup found to migrate data from")
        return False
    
    try:
        print("Attempting to migrate user data from backup...")
        
        # Connect to both databases
        backup_conn = sqlite3.connect(backup_path)
        backup_cursor = backup_conn.cursor()
        
        new_conn = sqlite3.connect(db_path)
        new_cursor = new_conn.cursor()
        
        # Check if user table exists in backup
        backup_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
        if not backup_cursor.fetchone():
            print("No user table found in backup")
            backup_conn.close()
            new_conn.close()
            return False
        
        # Get user data from backup
        backup_cursor.execute("SELECT * FROM user")
        users = backup_cursor.fetchall()
        
        if not users:
            print("No user data found in backup")
            backup_conn.close()
            new_conn.close()
            return False
        
        print(f"Found {len(users)} users in backup")
        
        # Get column names from backup database
        backup_cursor.execute("PRAGMA table_info(user)")
        backup_columns = [column[1] for column in backup_cursor.fetchall()]
        
        # Check if columns match
        new_cursor.execute("PRAGMA table_info(user)")
        new_columns = [column[1] for column in new_cursor.fetchall()]
        
        # Find common columns
        common_columns = [col for col in backup_columns if col in new_columns]
        
        # Skip if no common columns
        if not common_columns:
            print("No matching columns found between backup and new database")
            backup_conn.close()
            new_conn.close()
            return False
        
        print(f"Migrating data for columns: {common_columns}")
        
        # Prepare insert query
        placeholders = ', '.join(['?' for _ in common_columns])
        columns_str = ', '.join(common_columns)
        
        # Insert each user
        for user in users:
            # Extract values for common columns
            values = []
            for col in common_columns:
                idx = backup_columns.index(col)
                values.append(user[idx])
            
            query = f"INSERT INTO user ({columns_str}) VALUES ({placeholders})"
            try:
                new_cursor.execute(query, values)
                print(f"Migrated user with ID {user[0]}")
            except sqlite3.IntegrityError:
                print(f"Skipped user with ID {user[0]} (already exists)")
        
        # Commit changes
        new_conn.commit()
        
        # Close connections
        backup_conn.close()
        new_conn.close()
        
        print("User data migration completed successfully")
        return True
    except Exception as e:
        print(f"Error migrating user data: {e}")
        return False

def create_default_user():
    """Create a default admin user if no users exist"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if any users exist
        cursor.execute("SELECT COUNT(*) FROM user")
        user_count = cursor.fetchone()[0]
        
        if user_count > 0:
            print(f"Database already has {user_count} users, skipping default user creation")
            conn.close()
            return False
        
        # Create a default admin user
        email = "admin@example.com"
        password = "admin123"
        first_name = "Admin"
        
        # Hash the password
        if has_werkzeug:
            # Use werkzeug's password hashing
            hashed_password = generate_password_hash(password)
        else:
            # Simple hash as fallback (not secure for production)
            import hashlib
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Insert the admin user
        cursor.execute(
            "INSERT INTO user (email, password, first_name, is_admin) VALUES (?, ?, ?, ?)",
            (email, hashed_password, first_name, 1)
        )
        conn.commit()
        
        print(f"Created default admin user:")
        print(f"Email: {email}")
        print(f"Password: {password}")
        print(f"First Name: {first_name}")
        print(f"Is Admin: Yes")
        
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating default user: {e}")
        return False

def main():
    """Main function to fix the database"""
    print("=" * 50)
    print("DATABASE FIX UTILITY")
    print("=" * 50)
    print(f"Current directory: {os.getcwd()}")
    print(f"Database path: {os.path.abspath(db_path)}")
    
    # Step 1: Create backup
    has_backup = create_backup()
    if has_backup:
        print("✓ Backup created successfully")
    else:
        print("! No existing database to backup")
    
    # Step 2: Create new database
    if create_new_database():
        print("✓ New database created successfully")
    else:
        print("✗ Failed to create new database")
        return
    
    # Step 3: Migrate user data if backup exists
    users_migrated = False
    if has_backup:
        users_migrated = migrate_user_data()
        if users_migrated:
            print("✓ User data migrated successfully")
        else:
            print("! Failed to migrate user data")
    
    # Step 4: Create default user if no users were migrated
    if not users_migrated:
        if create_default_user():
            print("✓ Default admin user created successfully")
        else:
            print("! No default user created")
    
    print("\nDatabase fix completed.")
    print("\nIf you still encounter issues, try the following:")
    print("1. Run your application with administrator privileges")
    print("2. Make sure no other applications are using the database")
    print("3. Check your application's config to ensure it's looking for the database in the correct location")
    print("4. If needed, you can restore the backup from:", backup_path if has_backup else "No backup available")

if __name__ == "__main__":
    main() 
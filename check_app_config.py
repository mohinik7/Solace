import os
import sys
import sqlite3

# Get the absolute path of the project root directory
basedir = os.path.abspath(os.path.dirname(__file__))
print(f"Base directory: {basedir}")

# Check instance directory
instance_dir = os.path.join(basedir, 'instance')
print(f"Expected instance directory: {instance_dir}")

if not os.path.exists(instance_dir):
    print(f"ERROR: Instance directory does not exist! Creating it now...")
    try:
        os.makedirs(instance_dir)
        print(f"✓ Created instance directory at {instance_dir}")
    except Exception as e:
        print(f"Failed to create instance directory: {e}")
        sys.exit(1)
else:
    print(f"✓ Instance directory exists at {instance_dir}")

# Check database file
db_path = os.path.join(instance_dir, 'database.db')
print(f"Expected database path: {db_path}")

if not os.path.exists(db_path):
    print(f"ERROR: Database file does not exist!")
else:
    print(f"✓ Database file exists at {db_path}")
    print(f"  - File size: {os.path.getsize(db_path)} bytes")
    print(f"  - Read access: {os.access(db_path, os.R_OK)}")
    print(f"  - Write access: {os.access(db_path, os.W_OK)}")

# Check parent directory permissions
parent_dir = os.path.dirname(instance_dir)
print(f"Parent directory: {parent_dir}")
print(f"  - Read access: {os.access(parent_dir, os.R_OK)}")
print(f"  - Write access: {os.access(parent_dir, os.W_OK)}")
print(f"  - Execute access: {os.access(parent_dir, os.X_OK)}")

# Import the config
try:
    sys.path.insert(0, basedir)
    from config.config import Config
    print(f"\nDatabase URI from config: {Config.SQLALCHEMY_DATABASE_URI}")
    
    # Parse the URI to get the actual path
    uri = Config.SQLALCHEMY_DATABASE_URI
    if uri.startswith('sqlite:///'):
        path = uri[10:]  # Remove 'sqlite:///'
        print(f"Actual database path from URI: {os.path.abspath(path)}")
        
        # Check if this path exists
        if os.path.exists(path):
            print(f"✓ Database path from URI exists")
        else:
            print(f"ERROR: Database path from URI does not exist!")
except Exception as e:
    print(f"Error importing config: {e}")

# Try to connect to the database
print("\nAttempting to connect to the database...")
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    conn.close()
    print(f"✓ Successfully connected to database")
    print(f"  - Tables: {[t[0] for t in tables]}")
except Exception as e:
    print(f"ERROR connecting to database: {e}")

print("\nChecking Flask's default instance folder location...")
app_path = os.path.join(basedir, "website")
default_instance = os.path.join(app_path, "instance")
print(f"Default Flask instance path for app.py: {default_instance}")
if os.path.exists(default_instance):
    print(f"✓ Default Flask instance path exists")
else:
    print(f"Default Flask instance path does not exist")

print("\nFix Recommendations:")
print("1. Run your application as administrator")
print("2. Ensure the instance directory exists at:", instance_dir)
print("3. Check if your __init__.py explicitly sets the instance_path")
print("4. If the instance directory was created in a different location, copy the database.db file to:", db_path)
print("5. Verify the database path in config.py matches where the file actually is") 
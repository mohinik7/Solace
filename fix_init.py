import os
import re
import shutil
from datetime import datetime

# Paths
init_file = os.path.join('website', '__init__.py')
backup_suffix = f".backup.{datetime.now().strftime('%Y%m%d%H%M%S')}"
backup_file = init_file + backup_suffix

def backup_init_file():
    """Create a backup of the __init__.py file"""
    if os.path.exists(init_file):
        print(f"Creating backup of {init_file} to {backup_file}...")
        shutil.copy2(init_file, backup_file)
        return True
    return False

def update_init_file():
    """Update the __init__.py file to use the correct database path"""
    if not os.path.exists(init_file):
        print(f"ERROR: {init_file} does not exist!")
        return False
    
    try:
        # Read the file content
        with open(init_file, 'r') as f:
            content = f.read()
        
        # Update DB_NAME to include instance folder
        updated_content = re.sub(
            r'DB_NAME\s*=\s*"database.db"',
            'DB_NAME = os.path.join("instance", "database.db")',
            content
        )
        
        # Update check_sqlite3_database_exists function to support instance path
        updated_content = re.sub(
            r'def check_sqlite3_database_exists\(db_name\):.*?try:.*?conn = sqlite3.connect\(db_name\)',
            'def check_sqlite3_database_exists(db_name):\n    """Check if the SQLite3 database file exists and has the expected tables"""\n    try:\n        # Ensure the directory exists\n        db_dir = os.path.dirname(db_name)\n        if db_dir and not os.path.exists(db_dir):\n            os.makedirs(db_dir)\n            print(f"Created directory: {db_dir}")\n        conn = sqlite3.connect(db_name)',
            updated_content,
            flags=re.DOTALL
        )
        
        # Update create_app function to explicitly set instance_path
        updated_content = re.sub(
            r'def create_app\(config_name=\'development\'\):',
            'def create_app(config_name=\'development\', instance_path=None):\n    # Set up instance path\n    instance_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), \'..\', \'instance\'))\n    app = Flask(__name__, instance_path=instance_folder)',
            updated_content
        )
        
        # Remove the original Flask app creation line
        updated_content = re.sub(
            r'app = Flask\(__name__\)',
            '# App already created with instance_path above',
            updated_content
        )
        
        # Write the updated content
        with open(init_file, 'w') as f:
            f.write(updated_content)
        
        print(f"Updated {init_file} to use the correct database path")
        return True
    except Exception as e:
        print(f"ERROR updating {init_file}: {e}")
        return False

def main():
    """Main function to fix the __init__.py file"""
    print("=" * 50)
    print("INIT.PY FIX UTILITY")
    print("=" * 50)
    
    # Step 1: Create backup
    if backup_init_file():
        print("✓ Backup created successfully")
    else:
        print("✗ Failed to create backup")
        return
    
    # Step 2: Update __init__.py
    if update_init_file():
        print("✓ __init__.py updated successfully")
    else:
        print("✗ Failed to update __init__.py")
        return
    
    print("\nFix completed. Try running your app again.")
    print(f"If you encounter issues, you can restore the backup from: {backup_file}")

if __name__ == "__main__":
    main() 
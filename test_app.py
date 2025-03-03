import os
import sys
import sqlite3
from website import create_app, db

def test_database_connection():
    """Test if the app can connect to the database"""
    print("Testing database connection...")
    
    # Create Flask app with explicit instance path
    app = create_app()
    
    # Print configuration
    print(f"SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    instance_path = app.instance_path
    print(f"Flask instance path: {instance_path}")
    
    # Extract the database path from URI
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    if db_uri.startswith('sqlite:///'):
        db_path = db_uri[10:]  # Remove 'sqlite:///'
        print(f"Database path: {db_path}")
    else:
        print(f"Non-SQLite database URI: {db_uri}")
        db_path = os.path.join(instance_path, 'database.db')
        print(f"Falling back to default path: {db_path}")
    
    # Check if instance directory exists
    if not os.path.exists(instance_path):
        print(f"ERROR: Instance directory does not exist: {instance_path}")
        os.makedirs(instance_path)
        print(f"Created instance directory: {instance_path}")
    else:
        print(f"Instance directory exists: {instance_path}")
    
    # First try connecting directly with SQLite
    print("\nTrying direct SQLite connection...")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        print(f"Direct SQLite connection successful!")
        print(f"Tables in database: {tables}")
    except Exception as e:
        print(f"ERROR with direct SQLite connection: {str(e)}")
    
    # Now try with Flask-SQLAlchemy
    print("\nTrying Flask-SQLAlchemy connection...")
    try:
        with app.app_context():
            # Use a try/except to safely attempt different methods depending on SQLAlchemy version
            try:
                # Method for newer SQLAlchemy versions
                from sqlalchemy import text
                result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                tables = [row[0] for row in result]
            except Exception:
                try:
                    # Method for older SQLAlchemy versions
                    result = db.session.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = [row[0] for row in result]
                except Exception:
                    # Fallback
                    connection = db.engine.connect()
                    result = connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = [row[0] for row in result]
                    connection.close()
            
            print(f"Flask-SQLAlchemy connection successful!")
            print(f"Tables in database: {tables}")
            return True
    except Exception as e:
        print(f"ERROR with Flask-SQLAlchemy connection: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("APP DATABASE TEST")
    print("=" * 50)
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    
    success = test_database_connection()
    
    print("\nTest result:", "SUCCESS" if success else "FAILED")
    
    if not success:
        print("\nTroubleshooting tips:")
        print("1. Make sure the instance directory exists")
        print("2. Ensure the database file exists in the instance directory")
        print("3. Check file permissions")
        print("4. Run the application as administrator")
        print("5. Restart your computer to clear any file locks") 
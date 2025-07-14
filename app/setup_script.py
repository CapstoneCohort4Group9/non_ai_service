#!/usr/bin/env python3
"""
HopJetAir Database Setup Script
This script sets up the PostgreSQL database and populates it with sample data
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    required_packages = [
        'psycopg2-binary',
        'psycopg-pool', 
        'sqlalchemy',
        'fastapi',
        'uvicorn',
        'faker',
        'pydantic'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nInstall them with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def setup_database():
    """Setup PostgreSQL database"""
    print("Setting up PostgreSQL database...")
    
    # Database configuration
    db_config = {
        'host': 'localhost',
        'port': '5432',
        'database': 'hopjetair',
        'username': 'hopjetair',
        'password': 'SecurePass123!'
    }
    
    # SQL commands to create database and user
    sql_commands = f"""
    -- Create user
    CREATE USER {db_config['username']} WITH PASSWORD '{db_config['password']}';
    
    -- Create database
    CREATE DATABASE {db_config['database']} OWNER {db_config['username']};
    
    -- Grant privileges
    GRANT ALL PRIVILEGES ON DATABASE {db_config['database']} TO {db_config['username']};
    
    -- Connect to the database and grant schema privileges
    \\c {db_config['database']}
    GRANT ALL ON SCHEMA public TO {db_config['username']};
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {db_config['username']};
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {db_config['username']};
    """
    
    # Write SQL to temporary file
    sql_file = Path("setup_db.sql")
    sql_file.write_text(sql_commands)
    
    try:
        # Try to create database (requires postgresql to be running)
        print("Creating database and user...")
        result = subprocess.run([
            'psql', '-h', db_config['host'], '-p', db_config['port'], 
            '-U', 'postgres', '-f', str(sql_file)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Database setup completed successfully!")
        else:
            print("❌ Database setup failed:")
            print(result.stderr)
            print("\nManual setup instructions:")
            print(f"1. Start PostgreSQL service")
            print(f"2. Connect as postgres user: psql -U postgres")
            print(f"3. Run these commands:")
            print(sql_commands)
            
    except FileNotFoundError:
        print("❌ PostgreSQL 'psql' command not found.")
        print("Please install PostgreSQL and ensure it's in your PATH.")
        print("\nManual setup instructions:")
        print(sql_commands)
    
    finally:
        # Clean up
        if sql_file.exists():
            sql_file.unlink()
    
    return db_config

def create_env_file(db_config):
    """Create environment file with database configuration"""
    env_content = f"""# HopJetAir Database Configuration
DATABASE_URL=postgresql+asyncpg://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}
SYNC_DATABASE_URL=postgresql://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}

# Connection Pool Settings
DB_MIN_CONNECTIONS=5
DB_MAX_CONNECTIONS=20

# Application Settings
DEBUG=True
LOG_LEVEL=INFO
"""
    
    env_file = Path(".env")
    env_file.write_text(env_content)
    print(f"✅ Environment file created: {env_file}")

async def populate_database():
    """Populate database with sample data"""
    print("Populating database with sample data...")
    
    try:
        from data_generator import HopJetAirDataGenerator
        
        # Use the database URL from environment or default
        database_url = os.getenv("SYNC_DATABASE_URL", "postgresql://hopjetair:SecurePass123!@localhost:5432/hopjetair")
        
        generator = HopJetAirDataGenerator(database_url)
        await generator.populate_database()
        
        print("✅ Database populated successfully!")
        print("📊 Data summary:")
        print("  - 5 Airlines (including HopJetAir)")
        print("  - 16 Major airports worldwide")
        print("  - 5 Aircraft types")
        print("  - 50 Aircraft in fleet")
        print("  - 300 Passengers")
        print("  - 500 Bookings")
        print("  - 400 Flights")
        print("  - Trip packages and excursions")
        print("  - Insurance policies and refund records")
        
    except Exception as e:
        print(f"❌ Database population failed: {e}")
        print("Please check your database connection and try again.")

def create_project_structure():
    """Create recommended project structure"""
    directories = [
        "models",
        "services", 
        "api",
        "tests",
        "docs",
        "scripts"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    # Create __init__.py files
    for directory in ["models", "services", "api"]:
        (Path(directory) / "__init__.py").touch()
    
    print("✅ Project structure created")

def create_requirements_file():
    """Create requirements.txt file"""
    requirements = """fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
psycopg-pool==3.2.0
pydantic==2.5.0
faker==20.1.0
python-dotenv==1.0.0
alembic==1.13.0
pytest==7.4.3
httpx==0.25.2
"""
    
    Path("requirements.txt").write_text(requirements)
    print("✅ Requirements file created")

def main():
    """Main setup function"""
    print("🚀 HopJetAir Database Setup")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Please install required packages first")
        return
    
    # Create project structure
    create_project_structure()
    
    # Create requirements file
    create_requirements_file()
    
    # Setup database
    db_config = setup_database()
    
    # Create environment file
    create_env_file(db_config)
    
    # Ask user if they want to populate database
    populate = input("\n🔄 Do you want to populate the database with sample data? (y/n): ").lower().strip()
    
    if populate == 'y':
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Populate database
        asyncio.run(populate_database())
    
    print("\n🎉 Setup completed!")
    print("\nNext steps:")
    print("1. Start the API server:")
    print("   python updated_api_endpoints.py")
    print("\n2. Test the API:")
    print("   curl http://localhost:8000/health")
    print("\n3. View API documentation:")
    print("   http://localhost:8000/docs")
    print("\n4. Example API call:")
    print('   curl -X POST "http://localhost:8000/search_flight" \\')
    print('        -H "Content-Type: application/json" \\')
    print('        -d \'{"origin": "JFK", "destination": "LAX", "departure_date": "2025-08-15"}\'')

if __name__ == "__main__":
    main()

"""
Test MongoDB connection
"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_mongodb_connection():
    """Test MongoDB connection"""
    try:
        # Get MongoDB configuration
        mongo_url = os.getenv('MONGODB_URL')
        mongo_user = os.getenv('MONGODB_USER')
        mongo_password = os.getenv('MONGODB_PASSWORD')
        mongo_database = os.getenv('MONGODB_DATABASE')
        
        print("Testing MongoDB connection...")
        print(f"Host: {os.getenv('MONGODB_HOST')}")
        print(f"Database: {mongo_database}")
        
        # Create connection
        connection_string = f"mongodb://{mongo_user}:{mongo_password}@{mongo_url.replace('mongodb://', '')}"
        client = MongoClient(connection_string)
        
        # Test connection
        client.admin.command('ping')
        print("✓ Successfully connected to MongoDB!")
        
        # List databases
        print("\nAvailable databases:")
        for db_name in client.list_database_names():
            print(f"  - {db_name}")
        
        # Select database
        db = client[mongo_database]
        
        # List collections
        print(f"\nCollections in '{mongo_database}':")
        for collection_name in db.list_collection_names():
            print(f"  - {collection_name}")
        
        client.close()
        
    except Exception as e:
        print(f"✗ Failed to connect to MongoDB: {e}")


if __name__ == "__main__":
    test_mongodb_connection()

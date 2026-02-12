from dotenv import load_dotenv
import os
from pymongo import MongoClient

load_dotenv()

uri = os.getenv('MONGODB_URI')
db_name = os.getenv('MONGODB_DB', 'ELIXIDB')

print(f'Connecting to Atlas...')
try:
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print('✓ MongoDB Atlas connection successful!')
    
    db = client[db_name]
    collections = db.list_collection_names()
    print(f'✓ Database: {db_name}')
    print(f'✓ Collections: {collections if collections else "(empty)"}')
    
    client.close()
except Exception as e:
    print(f'✗ Connection failed: {str(e)}')

import atexit
from pymongo import MongoClient

# Replace these values with your MongoDB connection string
mongo_url = "mongodb://admin:password@localhost:27017"

DATABASE_NAME = "my-db"
COLLECTION_NAME = "my-collection"

# Connect to MongoDB
client = MongoClient(mongo_url)

# Access a specific database (replace 'your_database' with the actual database name)
db = client[DATABASE_NAME]

# Now you can interact with the collection
collection = db[COLLECTION_NAME]

# Example: Insert a document into the collection
document_data = {"key": "value"}
collection.insert_one(document_data)

# Register a function to close the MongoDB client on exit
# atexit.register(client.close)

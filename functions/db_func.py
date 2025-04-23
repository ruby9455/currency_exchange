from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from functions.auth_func import _read_toml
    
def _get_mongo_connection_string() -> str:
    """
    Get the MongoDB connection string from the TOML file.
    """
    # Read the TOML file
    config = _read_toml(".streamlit/secrets.toml")
    
    # Extract the connection string
    username = config.get("mongo", {}).get("username", "")
    password = config.get("mongo", {}).get("password", "")
    connection_string = f"mongodb+srv://{username}:{password}@cluster0.bgcvdvh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    
    return connection_string

def get_mongo_client() -> MongoClient | None:
    """
    Create a MongoDB client using the connection string from environment variables.
    """
    connection_str = _get_mongo_connection_string()
    
    # Create a MongoDB client
    client = MongoClient(connection_str, server_api=ServerApi('1'))
    
    try:
        client.admin.command('ping')
        print("MongoDB connection successful")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        client = None
    # Return the client
    return client

def create_db(client: MongoClient, db_name: str) -> None: # TODO: test the function
    """
    Create a new database in MongoDB.
    """
    # Create a new database
    db = client[db_name]
    print(f"Database '{db_name}' created successfully.")
    return db

def create_collection(db, collection_name: str) -> None: # TODO: test the function
    """
    Create a new collection in the specified database.
    """
    # Create a new collection
    collection = db[collection_name]
    print(f"Collection '{collection_name}' created successfully.")
    return collection

def insert_data(collection, data: dict) -> None:
    """
    Insert data into the specified collection.
    """
    # Insert data into the collection
    result = collection.insert_one(data)
    print(f"Data inserted with ID: {result.inserted_id}")
    return result

def fetch_data(collection, query: dict) -> list:
    """
    Fetch data from the specified collection based on the query.
    """
    # Fetch data from the collection
    data = collection.find(query)
    return list(data)

def update_data(collection, query: dict, new_values: dict) -> None:
    """
    Update data in the specified collection based on the query.
    """
    # Update data in the collection
    result = collection.update_one(query, {"$set": new_values})
    if result.modified_count > 0:
        print(f"Data updated successfully. Modified count: {result.modified_count}")
    else:
        print("No documents matched the query. No data updated.")
    return result

def delete_data(collection, query: dict) -> None: # TODO: test the function
    """
    Delete data from the specified collection based on the query.
    """
    # Delete data from the collection
    result = collection.delete_one(query)
    if result.deleted_count > 0:
        print(f"Data deleted successfully. Deleted count: {result.deleted_count}")
    else:
        print("No documents matched the query. No data deleted.")
    return result

def get_all_databases(client: MongoClient) -> list:
    """
    Get a list of all databases in the MongoDB server.
    """
    # Get a list of all databases
    databases = client.list_database_names()
    return databases

def get_all_collections(client: MongoClient, db_name: str) -> list:
    """
    Get a list of all collections in the specified database.
    """
    # Get a list of all collections
    db = client[db_name]
    collections = db.list_collection_names()
    return collections

def get_collection(client: MongoClient, db_name: str, collection_name: str) -> Collection:
    """
    Get a specific collection from the specified database.
    """
    # Get the specified collection
    db = client[db_name]
    collection = db[collection_name]
    return collection

def get_collection_data(client: MongoClient, db_name: str, collection_name: str) -> list:
    """
    Get all data from the specified collection.
    """
    collection = get_collection(client, db_name, collection_name)
    # Get all data from the collection
    data = collection.find()
    return list(data)

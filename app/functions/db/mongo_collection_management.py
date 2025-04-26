from pymongo.collection import Collection
from pymongo.mongo_client import MongoClient

def create_collection(client: MongoClient, db_name: str, collection_name: str) -> Collection:
    """
    Create a new collection in the specified database.
    """
    # Create a new collection
    db = client[db_name]
    collection = db[collection_name]
    print(f"Collection '{collection_name}' created successfully.")
    return collection

def get_all_databases(client: MongoClient) -> list:
    """
    Get a list of all databases in the MongoDB server.
    """
    # Get a list of all databases
    databases = client.list_database_names()
    databases = [db for db in databases if db not in ["admin", "local", "config"]]
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

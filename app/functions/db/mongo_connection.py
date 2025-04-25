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

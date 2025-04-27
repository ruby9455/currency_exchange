from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from typing import Literal
    
def _get_mongo_connection_string_file() -> str:
    """
    Get the MongoDB connection string from the TOML file.
    """
    from functions.utils import _read_toml
    # Read the TOML file
    config = _read_toml(".streamlit/secrets.toml")
    
    # Extract the connection components
    username = config.get("mongo", {}).get("username", "")
    password = config.get("mongo", {}).get("password", "")
    host = config.get("mongo", {}).get("host", "")
    protocol = config.get("mongo", {}).get("protocol", "")
    options = config.get("mongo", {}).get("options", "")
    
    # Build the connection string
    if protocol.endswith("://"):
        connection_string = f"{protocol}{username}:{password}@{host}/{options}"
    else:
        connection_string = f"{protocol}://{username}:{password}@{host}/{options}"
    
    return connection_string

def _get_mongo_connection_string_st() -> str:
    import streamlit as st
    username = st.secrets["mongo"]["username"]
    password = st.secrets["mongo"]["password"]
    host = st.secrets["mongo"]["host"]
    protocol = st.secrets["mongo"]["protocol"]
    options = st.secrets["mongo"]["options"]
    if protocol.endswith("://"):
        connection_string = f"{protocol}{username}:{password}@{host}/{options}"
    else:
        connection_string = f"{protocol}://{username}:{password}@{host}/{options}"
    return connection_string

def get_mongo_client(approach: Literal['file', 'st']='st') -> MongoClient | None:
    """
    Create a MongoDB client using the connection string from environment variables.
    """
    connection_str = _get_mongo_connection_string_file() if approach == 'file' else _get_mongo_connection_string_st()
    
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
    
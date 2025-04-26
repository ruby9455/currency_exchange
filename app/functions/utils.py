def _read_toml(file_path: str) -> dict:
    """
    Read a TOML file and return its contents as a dictionary.
    """
    import toml
    try:
        with open(file_path, 'r') as file:
            data = toml.load(file)
        return data
    except Exception as e:
        print(f"Error reading TOML file: {e}")
        return {}

def _get_default_db():
    """
    Get the database name from the TOML file.
    """
    from functions.utils import _read_toml
    config = _read_toml(".streamlit/secrets.toml")
    db_name = config.get("mongo", {}).get("db_name", "")
    return db_name

def _get_default_collection():
    """
    Get the collection name from the TOML file.
    """
    from functions.utils import _read_toml
    config = _read_toml(".streamlit/secrets.toml")
    collection_name = config.get("mongo", {}).get("collection_name", "")
    return collection_name
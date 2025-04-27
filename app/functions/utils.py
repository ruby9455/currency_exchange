from typing import Optional, Literal
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

def _get_default_db(approach: Literal['file', 'st']='st') -> str:
    if approach == 'file':
        return _get_default_db_file()
    elif approach == 'st':
        return _get_default_db_st()
    else:
        raise ValueError("Invalid approach. Use 'file' or 'st'.")
    
def _get_default_collection(approach: Literal['file', 'st']='st'):
    if approach == 'file':
        return _get_default_collection_file()
    elif approach == 'st':
        return _get_default_collection_st()
    else:
        raise ValueError("Invalid approach. Use 'file' or 'st'.")

def _get_default_db_file():
    """
    Get the database name from the TOML file.
    """
    from functions.utils import _read_toml
    config = _read_toml(".streamlit/secrets.toml")
    db_name = config.get("mongo", {}).get("db_name", "")
    return db_name

def _get_default_collection_file():
    """
    Get the collection name from the TOML file.
    """
    from functions.utils import _read_toml
    config = _read_toml(".streamlit/secrets.toml")
    collection_name = config.get("mongo", {}).get("collection_name", "")
    return collection_name

def _get_default_db_st():
    import streamlit as st
    db_name = st.secrets["mongo"]["db_name"]
    return db_name

def _get_default_collection_st():
    import streamlit as st
    collection_name = st.secrets["mongo"]["collection_name"]
    return collection_name

def _load_css(file_path: Optional[str] = None) -> None:
    """
    Load CSS styles from a file.
    """
    import streamlit as st
    with open('app/css/style.css') as f:
        style = f.read()
        
    if file_path:
        with open(file_path) as f:
            style += f.read()
    st.markdown(f'<style>{style}</style>', unsafe_allow_html=True)

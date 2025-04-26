import pandas as pd
import streamlit as st
from functions.db.mongo_connection import get_mongo_client
from functions.db.mongo_collection_management import get_all_databases, get_all_collections
from typing import Literal

@st.cache_resource
def get_cached_mongo_client():
    """
    Cache the MongoDB client connection using Streamlit's cache_resource decorator.
    This ensures the connection persists across Streamlit reruns.
    """
    return get_mongo_client()

def create_db_and_collection_input():
    all_database, all_collections = [], []
    client = get_cached_mongo_client()
    
    if client:
        all_database = get_all_databases(client)
        db_name = st.selectbox("Select a database", all_database)
        
        if db_name:
            all_collections = get_all_collections(client, db_name)
        collection_name = st.selectbox("Select a collection", all_collections)
        
        if db_name and collection_name:
            return db_name, collection_name
    return None, None

def get_collection_data_wrapper(db_name, collection_name):
    """
    Get data from the specified collection in the selected database.
    
    Args:
        db_name: The name of the database
        collection_name: The name of the collection
        
    Returns:
        DataFrame: A pandas DataFrame containing the data from the collection
    """
    from functions.db.mongo_collection_management import get_collection_data
    client = get_cached_mongo_client()
    if client:
        data = get_collection_data(client=client, db_name=db_name, collection_name=collection_name)
        if data:
            df = pd.DataFrame(data)
            for col in df.columns:
                if isinstance(df[col].iloc[0], pd.Timestamp):
                    df[col] = pd.to_datetime(df[col])
                    if not df[col].empty and df[col].dt.strftime('%H:%M:%S').eq('00:00:00').all():
                        df[col] = df[col].dt.date
            
            return df
    return None

def get_target_db_and_collection(db_action: Literal["insert", "update", "delete"]):
    """
    Get the target database and collection for the specified action (insert, update, delete).
    This function retrieves the database and collection names from the session state.
    """
    target_db = st.session_state.get(f"{db_action}_db", None)
    target_collection = st.session_state.get(f"{db_action}_collection", None)
    
    if target_db is None or target_collection is None:
        st.warning(f"Please select a database and collection to {db_action} data.")
        return None, None
    
    return target_db, target_collection

def execute_db_operation(operation: Literal["insert", "update", "delete"], data=None, query=None):
    """
    Execute a database operation (insert, update, delete) with the provided data.
    
    Args:
        operation: The type of operation to perform ("insert", "update", or "delete")
        data: The data to insert or update (required for insert and update)
        query: The query to identify documents for update or delete (required for update and delete)
        
    Returns:
        bool: True if the operation was successful, False otherwise
    """
    client = get_cached_mongo_client()
    if not client:
        st.error("Failed to connect to MongoDB.")
        return False
        
    db_name, collection_name = get_target_db_and_collection(operation)
    if not db_name or not collection_name:
        return False
    
    try:
        if operation == "insert":
            if not data:
                st.warning("No data provided for insertion.")
                return False
            client[db_name][collection_name].insert_one(data)
            st.success(f"Data inserted into '{collection_name}' in database '{db_name}'.")
        
        elif operation == "update":
            if not data or not query:
                st.warning("Both query and update data are required for update operations.")
                return False
            result = client[db_name][collection_name].update_one(query, {"$set": data})
            if result.modified_count > 0:
                st.success(f"Data updated in '{collection_name}' in database '{db_name}'.")
            else:
                st.warning("No documents matched the query criteria. No updates were made.")
                
        elif operation == "delete":
            if not query:
                st.warning("Query is required for delete operations.")
                return False
            result = client[db_name][collection_name].delete_one(query)
            if result.deleted_count > 0:
                st.success(f"Data deleted from '{collection_name}' in database '{db_name}'.")
            else:
                st.warning("No documents matched the query criteria. No deletions were made.")
                
        return True
    except Exception as e:
        st.error(f"Error performing {operation} operation: {e}")
        return False

def execute_batch_operations(operation_type: Literal["insert", "update", "delete"], operations_data):
    """
    Execute batch operations (insert, update, delete) on MongoDB documents.
    
    Args:
        operation_type: The type of operation to perform ("insert", "update", or "delete")
        operations_data: The data for the operations:
                         - For insert: List of documents to insert
                         - For update: Dict mapping document _ids to changed fields 
                                      {doc_id1: {field1: value1, field2: value2}, doc_id2: {...}}
                         - For delete: List of document _ids to delete
        
    Returns:
        dict: Statistics about the operation (success count, error count)
    """
    from pymongo.operations import InsertOne, UpdateOne, DeleteOne
    
    client = get_cached_mongo_client()
    if not client:
        st.error("Failed to connect to MongoDB.")
        return {"success": 0, "errors": 0}
        
    db_name, collection_name = get_target_db_and_collection(operation_type)
    if not db_name or not collection_name:
        return {"success": 0, "errors": 0}
    
    collection = client[db_name][collection_name]
    success_count = 0
    error_count = 0
    
    try:
        # Create a list of bulk operation objects
        bulk_operations = []
        
        # Add operations based on operation type
        if operation_type == "insert":
            # For insert, operations_data should be a list of documents to insert
            for document in operations_data:
                bulk_operations.append(InsertOne(document))
                
        elif operation_type == "update":
            # For update, operations_data should be a dict mapping _ids to changes
            for doc_id, changes in operations_data.items():
                bulk_operations.append(UpdateOne({"_id": doc_id}, {"$set": changes}))
                
        elif operation_type == "delete":
            # For delete, operations_data should be a list of _ids to delete
            for doc_id in operations_data:
                bulk_operations.append(DeleteOne({"_id": doc_id}))
        
        # Execute the bulk operation if there are operations to perform
        if bulk_operations:
            result = collection.bulk_write(bulk_operations)
            if operation_type == "insert":
                success_count = result.inserted_count
            elif operation_type == "update":
                success_count = result.modified_count
            elif operation_type == "delete":
                success_count = result.deleted_count
            
            st.success(f"Batch {operation_type} completed: {success_count} documents processed successfully")
            
        return {"success": success_count, "errors": error_count}
    except Exception as e:
        st.error(f"Error performing batch {operation_type} operation: {e}")
        # For inserts and deletes, operations_data is a list, for updates it's a dict
        total = len(operations_data)
        return {"success": success_count, "errors": total - success_count}

def determine_field_type(value):
    import datetime
    
    if isinstance(value, str):
        return "String"
    elif isinstance(value, int):
        return "Integer"
    elif isinstance(value, float):
        return "Float"
    elif isinstance(value, bool):
        return "Boolean"
    elif isinstance(value, pd.Timestamp) or isinstance(value, datetime.date):
        return "Date"
    else:
        return "Unknown"

def get_schema_form(disabled: bool = False):
    num_fields = st.number_input("Number of fields:", min_value=1, max_value=10, value=1, disabled=disabled)
    name_col, type_col = st.columns([1, 1])
    name_col.write("Field Name")
    type_col.write("Field Type")
    for i in range(num_fields):
        with name_col:
            st.text_input("", placeholder=f"Field Name {i+1}", key=f"field_name_{i}", disabled=disabled)
        with type_col:
            st.selectbox("", ["String", "Integer", "Float", "Boolean", "Date"], key=f"field_type_{i}", disabled=disabled)

def get_blank_form(disabled: bool = False):
    num_fields = st.number_input("Number of fields:", min_value=1, max_value=10, value=1, disabled=disabled)
    
    name_col, type_col, value_col = st.columns([1, 1, 3])
    name_col.write("Field Name")
    type_col.write("Field Type")
    value_col.write("Field Value")
    for i in range(num_fields):
        with name_col:
            st.text_input("", placeholder=f"Field Name {i+1}", key=f"field_name_{i}", disabled=disabled)
        with type_col:
            st.selectbox("", ["String", "Integer", "Float", "Boolean", "Date"], key=f"field_type_{i}", disabled=disabled)
        with value_col:
            st.text_input("", placeholder=f"Field Value {i+1}", key=f"field_value_{i}", disabled=disabled)

def get_form_from_data(data: 'pd.DataFrame', pre_filled: bool = False):
    for col in data.columns:
        if col.startswith("_"):
            continue
        
        field_name = col
        field_type = determine_field_type(data[col].iloc[0])
        
        if field_type == "String":
            st.text_input(label=field_name.replace('_', ' ').title(), value=None if not pre_filled else data[col].iloc[0], key=f"field_value_{field_name}")
        elif field_type == "Integer":
            st.number_input(label=field_name.replace('_', ' ').title(), value=None if not pre_filled else data[col].iloc[0], step=1, key=f"field_value_{field_name}")
        elif field_type == "Float":
            st.number_input(label=field_name.replace('_', ' ').title(), value=None if not pre_filled else data[col].iloc[0], key=f"field_value_{field_name}")
        elif field_type == "Boolean":
            st.radio(label=field_name.replace('_', ' ').title(), options=[True, False], index=0 if not pre_filled else int(data[col].iloc[0]), key=f"field_value_{field_name}", horizontal=True)
        elif field_type == "Date":
            st.date_input(label=field_name.replace('_', ' ').title(), value=None if not pre_filled else data[col].iloc[0], key=f"field_value_{field_name}")

def prepare_data_for_blank_form():
    data = {}
    field_names = [key for key in st.session_state.keys() if key.startswith("field_name_")]
    field_types = [key for key in st.session_state.keys() if key.startswith("field_type_")]
    field_values = [key for key in st.session_state.keys() if key.startswith("field_value_")]
    
    for i in range(len(field_names)):
        field_name = st.session_state[field_names[i]]
        field_type = st.session_state[field_types[i]]
        field_value = st.session_state[field_values[i]]
        
        if field_value == "":
            continue
        
        try:
            if field_type == "String":
                data[field_name] = str(field_value)
            elif field_type == "Integer":
                data[field_name] = int(field_value)
            elif field_type == "Float":
                data[field_name] = float(field_value)
            elif field_type == "Boolean":
                data[field_name] = bool(field_value)
            elif field_type == "Date":
                data[field_name] = pd.to_datetime(field_value)
            else:
                st.warning(f"Unsupported field type: {field_type}")
        except ValueError as e:
            st.warning(f"Invalid value for field '{field_name}': {field_value}. Error: {e}")
            # Keep as string if conversion fails
            data[field_name] = str(field_value)
            
    # clear the session state for field names, types, and values
    for key in field_names + field_types + field_values:
        if key in st.session_state:
            del st.session_state[key]
    # clear the form
    st.session_state["num_fields"] = 1
    
    return data

def prepare_data_for_existing_form():
    data = {}
    field_names = [key.replace("field_value_", "") for key in st.session_state.keys() if key.startswith("field_value_")]
    field_values = [value for key, value in st.session_state.items() if key.startswith("field_value_")]

    for name, value in zip(field_names, field_values):
        if value == "" or value is None or pd.isna(value):
            continue
        data[name] = value
        
    # clear the session state for field names and values
    for key in field_names:
        if "field_value_" + key in st.session_state:
            del st.session_state["field_value_" + key]
    
    return data

def get_data_ui():
    client = get_cached_mongo_client()
    if client:
        all_databases, all_collections = [], []
        
        all_databases = get_all_databases(client)
        db_name = st.selectbox("Select a database", all_databases)
        
        if db_name:
            all_collections = get_all_collections(client, db_name)
        collection_name = st.selectbox("Select a collection", all_collections)
        
        if collection_name:
            data = get_collection_data_wrapper(db_name=db_name, collection_name=collection_name)
            return data
    return None

def _handle_hidden_fields(operation_type: Literal["insert", "update", "delete"], data):
    """
    Handle hidden fields in the form based on the operation type.
    
    Args:
        operation_type: The type of operation to perform ("insert", "update", or "delete")
        data: The data associated with the operation
    """
    import uuid
    if operation_type == "insert":
        data["_id"] = str(uuid.uuid4())
        data["_created_at"] = pd.Timestamp.now()
        data["_updated_at"] = pd.Timestamp.now()
    elif operation_type == "update":
        data["_updated_at"] = pd.Timestamp.now()
    elif operation_type == "delete":
        pass
    else:
        st.warning("Unsupported operation type.")
        return data
    
    return data

def _handle_data_types(data):
    """
    Handle data types for the fields in the form.
    
    Args:
        data: The data to be processed
        
    Returns:
        dict: The processed data with appropriate types
    """
    for key, value in data.items():
        if isinstance(value, str):
            # Date or datetime conversion
            try:
                # Try to convert to datetime
                data[key] = pd.to_datetime(value)
                continue  # Skip further processing if this succeeds
            except ValueError:
                pass  # Keep as string if conversion fails
            
            # Integer or float conversion
            value = value.strip() 
            
            # Check for integer
            if value.lstrip('-').isdigit():
                data[key] = int(value)
                continue
                
            # Check for float
            try:
                float_value = float(value)
                if float_value.is_integer():
                    data[key] = int(float_value)
                else:
                    data[key] = float_value
            except ValueError:
                pass
                
        elif isinstance(value, bool):
            data[key] = bool(value)
        elif isinstance(value, (int, float)):
            data[key] = float(value)
    
    return data

def convert_value_to_capitalized(data):
    for key, value in data.items():
        if key in ["from_curr", "to_curr"]:
            if not pd.isna(value):
                data[key] = value.upper()
    return data

def clean_up_data(operation_type: Literal["insert", "update", "delete"], data, hidden_fields: bool = False):
    """
    Clean up the data by removing empty fields and converting values to appropriate types.
    
    Args:
        data: The data to be cleaned
    """
    cleaned_data = {k: v for k, v in data.items() if v not in [None, "", pd.NA]}
    
    if hidden_fields:
        cleaned_data = _handle_hidden_fields(operation_type=operation_type, data=cleaned_data)
    cleaned_data = _handle_data_types(cleaned_data)
    cleaned_data = convert_value_to_capitalized(cleaned_data)
    
    return cleaned_data

@st.dialog("Confirmation Dialog")
def confirmation_dialog(message: str, on_confirm: 'Callable', on_cancel: 'Callable', args=None, kwargs=None):
    """
    Show a confirmation dialog with the specified message.
    
    Args:
        message: The message to display in the dialog
        on_confirm: Function to call when the user confirms
        on_cancel: Function to call when the user cancels
        args: Tuple of positional arguments to pass to on_confirm
        kwargs: Dictionary of keyword arguments to pass to on_confirm
    """
    from functions.ui.auth_ui import check_secondary_password_ui
    st.write(message)
    secondary_pw = st.text_input("Enter secondary password", type="password", key="secondary_password")
    left_btn, right_btn = st.columns([1, 1], vertical_alignment="center")
    if left_btn.button("Confirm"):
        logged_in_user = st.session_state.get("logged_in_user", "")
        if not logged_in_user:
            st.warning("Login ID is not set.")
            return
        if check_secondary_password_ui(username=logged_in_user, secondary_password=secondary_pw):
            # Call on_confirm with args and kwargs if provided
            if args is not None and kwargs is not None:
                on_confirm(*args, **kwargs)
            elif args is not None:
                on_confirm(*args)
            elif kwargs is not None:
                on_confirm(**kwargs)
            else:
                on_confirm()
            st.rerun()
        else:
            st.warning("Invalid secondary password.")
    if right_btn.button("Cancel"):
        on_cancel()

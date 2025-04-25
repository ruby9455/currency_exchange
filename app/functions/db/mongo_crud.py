from pymongo.collection import Collection

def insert_data(collection: Collection, data: dict) -> None:
    """
    Insert data into the specified collection.
    """
    # Insert data into the collection
    result = collection.insert_one(data)
    print(f"Data inserted with ID: {result.inserted_id}")
    return result

def fetch_data(collection: Collection, query: dict) -> list:
    """
    Fetch data from the specified collection based on the query.
    """
    # Fetch data from the collection
    data = collection.find(query)
    return list(data)

def update_data(collection: Collection, query: dict, new_values: dict) -> None:
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

def delete_data(collection: Collection, query: dict) -> None: # TODO: test the function
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

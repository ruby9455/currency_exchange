import uuid
import pandas as pd
import streamlit as st
from functions.db_func import get_mongo_client, get_all_databases, get_all_collections, get_collection, get_collection_data
from functions.auth_func import authenticate_user

def init_page():
    if "logged_in" not in st.session_state: 
        st.session_state.logged_in = False
    if "login_id" not in st.session_state: 
        st.session_state.login_id = ""

def login_page():
    st.title("Login Page")
    st.text_input("Enter Login ID", key="login_id")
    st.text_input("Enter Password", type="password", key="password")
    
    if st.button("Login"):
        if authenticate_user(st.session_state.login_id, st.session_state.password):
            st.session_state.logged_in = True
            del st.session_state.password
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid login credentials. Please try again.")

def logout_page():
    st.session_state.logged_in = False
    if "login_id" in st.session_state: 
        del st.session_state.login_id
    if "password" in st.session_state: 
        del st.session_state.password
    st.success("Logged out successfully.")

def refresh_page():
    st.rerun()

def db_actions():
    client = get_mongo_client()
    content = st.container()
    if client:
        st.success("Connected to MongoDB successfully!")
        
        st.selectbox(label="Select an action", options=["", "Create Database", "Create Collection", "Insert Data", "Fetch Data", "Update Data"], index=0, key="db_action")
        
        if st.session_state.db_action == "Create Database":
            db_name = st.text_input("Enter database name")
            if st.button("Create Database"):
                db = client[db_name]
                st.success(f"Database '{db_name}' created successfully.")
                refresh_page()
                
        elif st.session_state.db_action == "Create Collection":
            db_name = st.text_input("Enter database name")
            collection_name = st.text_input("Enter collection name")
            if st.button("Create Collection"):
                db = client[db_name]
                collection = db[collection_name]
                st.success(f"Collection '{collection_name}' created successfully in database '{db_name}'.")
                refresh_page()
                
        elif st.session_state.db_action == "Insert Data":
            all_databases = get_all_databases(client)
            db_name = st.selectbox(label="Select database", options=all_databases)
            if db_name:
                all_collections = get_all_collections(client=client, db_name=db_name)
                collection_name = st.selectbox("Select collection", options=all_collections)
                collection = get_collection(client=client, db_name=db_name, collection_name=collection_name)
                db_data = get_collection_data(client=client, db_name=db_name, collection_name=collection_name)
                db_data = pd.DataFrame(db_data)
                columns = db_data.columns.tolist()
                hide_cols = [col for col in columns if col.startswith("_")]
                show_cols = [col for col in columns if not col.startswith("_")]
                all_cols = hide_cols + show_cols
                empty_data = pd.DataFrame(columns=show_cols)
                if "data_editor_key" not in st.session_state:
                    st.session_state.data_editor_key = str(uuid.uuid4())
                st.data_editor(data=empty_data, use_container_width=True, key=st.session_state.data_editor_key, hide_index=True, num_rows="dynamic")
                if st.button("Insert Data"):
                    if st.session_state.data_editor_key in st.session_state:
                        print("Data editor key found in session state.")
                        with st.spinner("Inserting data..."):
                            changes_dict = st.session_state[st.session_state.data_editor_key]
                            if "added_rows" in changes_dict:
                                print("Added rows found in changes dictionary.")
                                added_rows = changes_dict["added_rows"]
                                new_data_df = pd.DataFrame(added_rows)
                                
                                new_data_df["_id"] = [str(uuid.uuid4()) for _ in range(len(new_data_df))]
                                now = pd.Timestamp.now()
                                new_data_df["_created_at"] = now
                                new_data_df["_updated_at"] = now
                                
                                if "date" in new_data_df.columns:
                                    new_data_df["date"] = pd.to_datetime(new_data_df["date"])
                                if "from_curr" in new_data_df.columns:
                                    new_data_df["from_curr"] = new_data_df["from_curr"].fillna("")
                                    new_data_df["from_curr"] = new_data_df["from_curr"].astype(str).str.upper()
                                if "to_curr" in new_data_df.columns:
                                    new_data_df["to_curr"] = new_data_df["to_curr"].fillna("")
                                    new_data_df["to_curr"] = new_data_df["to_curr"].astype(str).str.upper()
                                if "from_amt" in new_data_df.columns and "to_amt" in new_data_df.columns:
                                    new_data_df["from_amt"] = new_data_df["from_amt"].fillna(0).astype(float)
                                    new_data_df["to_amt"] = new_data_df["to_amt"].fillna(0).astype(float)
                                    new_data_df["_rate"] = new_data_df["to_amt"] / new_data_df["from_amt"]
                                    new_data_df["_rate_reciprocal"] = new_data_df["from_amt"] / new_data_df["to_amt"]
                                if "bonus_amt" in new_data_df.columns:
                                    new_data_df["bonus_amt"] = new_data_df["bonus_amt"].fillna(0)
                                    new_data_df["bonus_amt"] = new_data_df["bonus_amt"].astype(float)
                                for index, row in new_data_df.iterrows():
                                    data = {col: row[col] for col in all_cols if col in row}
                                    print(f"Inserting data: {data}")
                                    collection.insert_one(data)
                                # st.success("Data inserted successfully.")
                                # st.session_state.data_editor_key = str(uuid.uuid4())
                                # refresh_page()
                    else:
                        st.warning("No data to insert.")
                        refresh_page()
                        
        elif st.session_state.db_action == "Fetch Data":
            all_databases = get_all_databases(client)
            db_name = st.selectbox(label="Select database", options=all_databases)
            if db_name:
                all_collections = get_all_collections(client=client, db_name=db_name)
                collection_name = st.selectbox("Select collection", options=all_collections)
                collection = get_collection(client=client, db_name=db_name, collection_name=collection_name)
                db_data = get_collection_data(client=client, db_name=db_name, collection_name=collection_name)
                db_data = pd.DataFrame(db_data)
                correct_order = ["date", "from_curr", "from_amt", "to_curr", "to_amt", "_rate", "bonus_amt", "_created_at", "_updated_at"]
                db_data = db_data[correct_order]
                db_data = db_data.rename(columns={"date": "Date", "from_curr": "From Currency", "from_amt": "From Amount", "to_curr": "To Currency", "to_amt": "To Amount", "_rate": "Rate", "bonus_amt": "Bonus Amount", "_created_at": "Created At", "_updated_at": "Updated At"})
                db_data["Date"] = pd.to_datetime(db_data["Date"]).dt.strftime("%Y-%m-%d")
                db_data["Created At"] = pd.to_datetime(db_data["Created At"]).dt.strftime("%Y-%m-%d %H:%M:%S")
                db_data["Updated At"] = pd.to_datetime(db_data["Updated At"]).dt.strftime("%Y-%m-%d %H:%M:%S")
                st.dataframe(db_data, use_container_width=True, hide_index=True)
                
        elif st.session_state.db_action == "Update Data":
            # TODO: Implement update data functionality with st.data_editor
            all_databases = get_all_databases(client)
            db_name = st.selectbox(label="Select database", options=all_databases)
            if db_name:
                all_collections = get_all_collections(client=client, db_name=db_name)
                collection_name = st.selectbox("Select collection", options=all_collections)
                if collection_name:
                    collection = get_collection(client=client, db_name=db_name, collection_name=collection_name)
                    db_data = get_collection_data(client=client, db_name=db_name, collection_name=collection_name)
                    db_data = pd.DataFrame(db_data)
                    correct_order = ["_id", "date", "from_curr", "from_amt", "to_curr", "to_amt", "_rate", "_rate_reciprocal", "bonus_amt"]
                    db_data = db_data[correct_order]
                    db_data = db_data.set_index("_id")
                    columns_dict = {"date": "Date", "from_curr": "From Currency", "from_amt": "From Amount", "to_curr": "To Currency", "to_amt": "To Amount", "_rate": "Rate", "_rate_reciprocal": "Rate Reciprocal", "bonus_amt": "Bonus Amount", "_created_at": "Created At", "_updated_at": "Updated At"}
                    db_data = db_data.rename(columns=columns_dict)
                    db_data["Date"] = pd.to_datetime(db_data["Date"]).dt.strftime("%Y-%m-%d")
                    if "update_data_editor_key" not in st.session_state:
                        st.session_state.update_data_editor_key = str(uuid.uuid4())
                    st.data_editor(data=db_data, use_container_width=True, key=st.session_state.update_data_editor_key, hide_index=True, num_rows="fixed", disabled=("_id"))
                    if st.button("Update Data"):
                        if st.session_state.update_data_editor_key in st.session_state:
                            with st.spinner("Updating data..."):
                                changes_dict = st.session_state[st.session_state.update_data_editor_key]
                                if "edited_rows" in changes_dict and changes_dict["edited_rows"]:
                                    reversed_columns_dict = {v: k for k, v in columns_dict.items()}
                                    edited_rows = changes_dict["edited_rows"]
                                    for index, changes in edited_rows.items():
                                        rate_changed = False
                                        changed_cols = list(changes.keys())
                                        if "From Amount" in changed_cols or "To Amount" in changed_cols:
                                            rate_changed = True
                                        new_data = {"_id": db_data.index[index], "_updated_at": pd.Timestamp.now()}
                                        for column, new_value in changes.items():
                                            if column in list(reversed_columns_dict.keys()):
                                                if reversed_columns_dict[column] in ["from_amt", "to_amt", "bonus_amt"]:
                                                    if new_value is None:
                                                        new_value = 0
                                                        edited_rows[index][column] = 0 # update the dict for calculating rates
                                                    new_data[reversed_columns_dict[column]] = float(new_value)
                                                else:
                                                    new_data[reversed_columns_dict[column]] = new_value
                                        if rate_changed:
                                            if "From Amount" in changed_cols and "To Amount" in changed_cols:
                                                new_from = changes["From Amount"]
                                                new_to = changes["To Amount"]
                                            elif "From Amount" in changed_cols:
                                                new_from = changes["From Amount"]
                                                new_to = db_data.loc[index, "To Amount"]
                                            else:
                                                new_from = db_data.loc[index, "From Amount"]
                                                new_to = changes["To Amount"]
                                            new_data["_rate"] = float(new_to) / float(new_from)
                                            new_data["_rate_reciprocal"] = float(new_from) / float(new_to)
                                        
                                        print(f"Updating {new_data["_id"]} with {new_data}")
                                        collection.update_one({"_id": new_data["_id"]}, {"$set": new_data})
                                    st.success("Data updated successfully.")
                                    st.session_state.update_data_editor_key = str(uuid.uuid4())
                                    refresh_page()
                                else:
                                    st.warning("No data to update.")
                        else:
                            st.warning("No data to update.")
                            refresh_page()
        
        else:
            st.warning("Please select an action from the dropdown.")

def main():
    init_page()
    header = st.columns([1, 5, 1])
    
    header[1].title("Dataabase Management")
    content = st.container()
    if not st.session_state.logged_in:
        with content:
            login_page()
    else:
        header[0].write(f"Welcome {st.session_state.login_id}!")
        header[2].button("Logout", key="logout", on_click=logout_page)
        content.empty()
        with content:
            db_actions()
        
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.success("Logged out successfully.")

if __name__ == "__main__":
    main()


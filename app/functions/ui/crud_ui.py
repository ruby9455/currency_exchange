import pandas as pd
import streamlit as st
from functions.ui.db_func_ui import create_db_and_collection_input, prepare_data_for_existing_form, execute_db_operation, get_form_from_data, get_collection_data_wrapper, execute_batch_operations, clean_up_data

def get_create_table_page():
    from functions.db.mongo_collection_management import create_collection
    from functions.ui.db_func_ui import get_cached_mongo_client
    
    db_name = st.text_input(label="", placeholder="Name of database", label_visibility="collapsed", value=None)
    collection_name = st.text_input(label="", placeholder="Name of collection", label_visibility="collapsed", value=None)
    if db_name is None and collection_name is None:
        st.button("Create Collection", disabled=True)
        st.stop()
    if st.button("Create Collection"):
        client = get_cached_mongo_client()
        if client:
            if db_name and collection_name:
                try:
                    create_collection(client, db_name, collection_name)
                    st.success(f"Collection '{collection_name}' created in database '{db_name}'.")
                except Exception as e:
                    st.error(f"Error creating collection: {e}")
            else:
                st.warning("Please enter both database and collection names.")
        else:
            st.error("Failed to connect to MongoDB.")
            
def get_insert_data_page():
    from functions.ui.db_func_ui import get_schema_form, get_blank_form, prepare_data_for_blank_form
    db_name, collection_name = create_db_and_collection_input()
    st.divider()
    
    st.session_state["insert_db"] = db_name
    st.session_state["insert_collection"] = collection_name
    
    if db_name is None and collection_name is None:
        get_blank_form(disabled=True)
        st.stop()
    
    collection_data = get_collection_data_wrapper(db_name, collection_name)
    if collection_data is None:
        batch_mode = st.toggle("Use batch update mode", value=True, help="Update all documents in a single database operation")
        if batch_mode: 
            get_schema_form(disabled=False)
            st.divider()

            field_names = [st.session_state[key] for key in st.session_state if key.startswith("field_name_")]
            field_types = [st.session_state[key] for key in st.session_state if key.startswith("field_type_")]
            display_field_names = [field_name for field_name in sorted(field_names) if not field_name.startswith("_") and not pd.isna(field_name) and field_name != ""] if field_names else []
            column_config = {}
            for field_name, field_type in zip(field_names, field_types):
                if field_type == "String":
                    column_config[field_name] = st.column_config.TextColumn(label=field_name)
                elif field_type == "Number":
                    column_config[field_name] = st.column_config.NumberColumn(label=field_name)
                elif field_type == "Boolean":
                    column_config[field_name] = st.column_config.CheckboxColumn(label=field_name)
                elif field_type == "Date":
                    column_config[field_name] = st.column_config.DateColumn(label=field_name)
                else:
                    column_config[field_name] = st.column_config.Column(label=field_name)
            
            if display_field_names:
                st.data_editor(
                    data=pd.DataFrame(columns=display_field_names),
                    use_container_width=True,
                    hide_index=True,
                    column_order=display_field_names,
                    column_config=column_config,
                    key="insert_data_editor",
                    num_rows="dynamic",
                )
                
                documents_to_insert = []
                if "insert_data_editor" in st.session_state and "added_rows" in st.session_state.insert_data_editor:
                    added_rows = st.session_state.insert_data_editor["added_rows"]
                    if added_rows:
                        for added_row in added_rows:
                            new_doc = {}
                            for col, new_value in added_row.items():
                                if not pd.isna(new_value):
                                    new_doc[col] = new_value
                            
                            if new_doc:
                                new_doc = clean_up_data(operation_type="insert", data=new_doc, hidden_fields=True)
                                documents_to_insert.append(new_doc)
                                
                        if st.button("Insert Data", disabled=not documents_to_insert):
                            if db_name and collection_name:
                                result = execute_batch_operations(operation_type="insert", operations_data=documents_to_insert)
                                if result["success"] > 0:
                                    st.success(f"Successfully inserted {result['success']} document(s) in batch mode.")
                                    st.session_state.insert_data_editor["added_rows"] = {}
                                if result["errors"] > 0:
                                    st.error(f"Failed to insert {result['errors']} document(s).")
                            else:
                                st.warning("Please enter both database and collection names.")
        else:
            get_blank_form(disabled=False)
            data = prepare_data_for_blank_form()
            data = clean_up_data(operation_type="insert", data=data, hidden_fields=True)
            if st.button("Insert Data", disabled=not data):
                if db_name and collection_name:
                    execute_db_operation("insert", data=data)
                else:
                    st.warning("Please enter both database and collection names.")
    else:
        batch_mode = st.toggle("Use batch update mode", value=True, help="Update all documents in a single database operation")
        if batch_mode: 
            display_cols = [col for col in collection_data.columns.tolist() if not col.startswith("_")]
            st.data_editor(
                data=pd.DataFrame(columns=display_cols),
                use_container_width=True,
                hide_index=True,
                column_order=display_cols,
                key="insert_data_editor",
                num_rows="dynamic",
            )
            
            documents_to_insert = []
            if "insert_data_editor" in st.session_state and "added_rows" in st.session_state.insert_data_editor:
                added_rows = st.session_state.insert_data_editor["added_rows"]
                if added_rows:
                    for added_row in added_rows:
                        new_doc = {}
                        for col, new_value in added_row.items():
                            if not pd.isna(new_value):
                                new_doc[col] = new_value
                        
                        if new_doc:
                            new_doc = clean_up_data(operation_type="insert", data=new_doc, hidden_fields=True)
                            documents_to_insert.append(new_doc)
                    
                    if st.button("Insert Data", disabled=not documents_to_insert):
                        if db_name and collection_name:
                            result = execute_batch_operations(operation_type="insert", operations_data=documents_to_insert)
                            if result["success"] > 0:
                                st.success(f"Successfully inserted {result['success']} document(s) in batch mode.")
                                st.session_state.insert_data_editor["added_rows"] = {}
                            if result["errors"] > 0:
                                st.error(f"Failed to insert {result['errors']} document(s).")
                        else:
                            st.warning("Please enter both database and collection names.")
        else:
            get_form_from_data(data=collection_data)
            data = prepare_data_for_existing_form()
            data = clean_up_data(operation_type="insert", data=data, hidden_fields=True)
            if st.button(label="Insert Data", disabled=not data):
                if db_name and collection_name:
                    execute_db_operation("insert", data=data)
                else:
                    st.warning("Please enter both database and collection names.")
    
def get_fetch_data_page():
    from functions.ui.db_func_ui import get_collection_data_wrapper
    db_name, collection_name = create_db_and_collection_input()
    st.divider()
    
    if db_name is None and collection_name is None:
        st.stop()
    
    collection_data = get_collection_data_wrapper(db_name, collection_name)
    if collection_data is not None:
        st.dataframe(data=collection_data, hide_index=True)
    else:
        st.warning("No data found in the specified collection.")

def get_update_data_page():
    db_name, collection_name = create_db_and_collection_input()
    st.divider()
    
    st.session_state["update_db"] = db_name
    st.session_state["update_collection"] = collection_name
    
    if db_name is None and collection_name is None:
        st.stop()
        
    collection_data = get_collection_data_wrapper(db_name, collection_name)
    if collection_data is None:
        st.warning("No data found in the specified collection.")
        st.stop()
    else:
        display_cols = [col for col in collection_data.columns.tolist() if not col.startswith("_")]
        batch_mode = st.toggle("Use batch update mode", value=False, help="Update all documents in a single database operation")
        
        if batch_mode:
            st.data_editor(
                data=collection_data,
                use_container_width=True,
                hide_index=True,
                column_order=display_cols,
                key="update_data_editor",
                num_rows="fixed",
            )
        
            updated_data = {}        
            if "update_data_editor" in st.session_state and "edited_rows" in st.session_state.update_data_editor:
                edited_rows = st.session_state.update_data_editor["edited_rows"]
                if edited_rows: # {row_index: {col_name: new_value}}
                    for row, values in edited_rows.items():
                        _id = collection_data.iloc[row]["_id"]
                        updated_data[_id] = {}
                        for col, new_value in values.items():
                            updated_data[_id][col] = new_value
                        updated_data[_id] = clean_up_data(operation_type="update", data=updated_data[_id], hidden_fields=True)
                    if st.button("Update Data", disabled=not updated_data):
                        if db_name and collection_name:
                            # Use batch update for efficiency
                            result = execute_batch_operations("update", updated_data)
                            if result["success"] > 0:
                                st.success(f"Successfully updated {result['success']} document(s) in batch mode.")
                            if result["errors"] > 0:
                                st.error(f"Failed to update {result['errors']} document(s).")
                                
                            st.session_state.update_data_editor["edited_rows"] = {}
        else:
            st.write("Select a row to update:")
            st.dataframe(
                data=collection_data,
                use_container_width=True,
                hide_index=True,
                column_order=display_cols,
                on_select="rerun",
                selection_mode="single-row",
                key="update_data_frame",
            )
            
            if "update_data_frame" in st.session_state and "selection" in st.session_state.update_data_frame:
                selected_row = st.session_state.update_data_frame["selection"]["rows"]
                if selected_row:
                    selected_row_index = selected_row[0]
                    selected_row_data = collection_data.iloc[[selected_row_index]]
                    get_form_from_data(data=selected_row_data, pre_filled=True)
                    
                    updated_data = {}
                    for col in selected_row_data.columns:
                        if not col.startswith("_") and "field_value_" + col in st.session_state:
                            if st.session_state["field_value_" + col] != selected_row_data[col].values[0]:
                                updated_data[col] = st.session_state["field_value_" + col]
                    updated_data = clean_up_data(operation_type="update", data=updated_data, hidden_fields=False)
                    if st.button("Update Data", disabled=not updated_data):
                        if db_name and collection_name:
                            execute_db_operation("update", data=updated_data, query={"_id": selected_row_data["_id"].values[0]})
                        else:
                            st.warning("Please enter both database and collection names.")
                    
def get_delete_data_page():
    from functions.ui.db_func_ui import confirmation_dialog
    db_name, collection_name = create_db_and_collection_input()
    st.divider()
    
    st.session_state["delete_db"] = db_name
    st.session_state["delete_collection"] = collection_name
    
    if db_name is None and collection_name is None:
        st.stop()
        
    collection_data = get_collection_data_wrapper(db_name, collection_name)
    if collection_data is None:
        st.warning("No data found in the specified collection.")
        st.stop()
    else:
        display_cols = [col for col in collection_data.columns.tolist() if not col.startswith("_")]
        st.dataframe(
            data=collection_data,
            use_container_width=True,
            hide_index=True,
            column_order=display_cols,
            on_select="rerun",
            selection_mode="multi-row",
            key="delete_data_frame",
        )
        
        if "delete_data_frame" in st.session_state and "selection" in st.session_state.delete_data_frame:
            selected_rows = st.session_state.delete_data_frame["selection"]["rows"]
            if selected_rows:
                selected_row_data = collection_data.iloc[selected_rows]
                
                if st.button("Delete Data"):
                    if db_name and collection_name:
                        ids_to_delete = selected_row_data["_id"].values.tolist()
                        confirmation_dialog(
                            message=f"Are you sure you want to delete {len(selected_rows)} document(s)?",
                            on_confirm=execute_batch_operations,
                            on_cancel=st.rerun,
                            args=("delete", ids_to_delete),
                        )
                    else:
                        st.warning("Please enter both database and collection names.")

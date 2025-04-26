import streamlit as st
from components.navigation import nav_bar
from functions.utils import _get_default_db, _get_default_collection
from functions.ui.auth_page import init_auth_state, login_page, auth_header
from functions.ui.crud_ui import _tidy_up_collection_data

def transaction_history_page():
    from functions.ui.db_func_ui import get_collection_data_wrapper
    default_db = _get_default_db()
    default_collection = _get_default_collection()
    data = get_collection_data_wrapper(db_name=default_db, collection_name=default_collection)
    if data is not None and not data.empty:
        data = _tidy_up_collection_data(data, hide_id=True, show_hidden=False)
        st.dataframe(
            data=data,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.warning(body="沒有交易紀錄", icon="⚠️")

def main():
    init_auth_state()
    nav_bar()
    header_placeholder = st.empty()
    content_placeholder = st.empty()
    if not st.session_state.is_logged_in:
        with content_placeholder:
            login_page()
    else:
        content_placeholder.empty()
        with header_placeholder:
            auth_header(page_title="交易紀錄")
        with content_placeholder:
            transaction_history_page()
    
if __name__ == "__main__":
    st.set_page_config(
        page_title="交易紀錄",
        page_icon="📜",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    main()
APP_NAME = "Currency Exchange"
MARGIN = 0.005
PAGE_FILE_NAME_DICT = {
    "Exchange Approach Comparison": "main.py",
    "Transaction History": "pages/transaction_history.py",
    "Database Management": "pages/db_management.py",
    "User Management": "pages/user_management.py",
    "Login": "pages/login.py",
    "Logout": "pages/logout.py",
}

def get_tabs(is_logged_in: bool, is_admin: bool):
    general_tabs = set(["Exchange Approach Comparison"])
    
    if is_logged_in:
        general_tabs.add("Transaction History")
        general_tabs.add("Logout")
    else:
        general_tabs.add("Login")
        
    if is_admin:
        general_tabs.add("Database Management")
        general_tabs.add("User Management")

    return general_tabs

def get_cols_ratio(is_logged_in: bool, is_admin: bool):
    tabs = get_tabs(is_logged_in, is_admin)
    cols_ratio = [1] * len(tabs)
    return [MARGIN] + cols_ratio + [MARGIN]


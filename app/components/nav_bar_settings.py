APP_NAME = "Currency Exchange"
MARGIN = 1  # Increased margin for better visibility and consistency
PAGE_FILE_NAME_DICT = {
    "比較兌換方法": "main.py",
    "兌換紀錄": "pages/transaction_history.py",
    "管理資料庫": "pages/db_management.py",
    "管理用戶": "pages/user_management.py",
    "登入": "pages/login.py",
    "登出": "pages/logout.py",
}

def get_tabs(is_logged_in: bool, is_admin: bool):
    general_tabs = ["比較兌換方法"]
    auth_tab = ""
    
    if is_logged_in:
        general_tabs.append("兌換紀錄")
        auth_tab = "登出"
    else:
        auth_tab = "登入"
        
    if is_admin:
        general_tabs.append("管理資料庫")
        general_tabs.append("管理用戶")

    return general_tabs, auth_tab

def get_cols_ratio(is_logged_in: bool, is_admin: bool):
    tabs, auth_tab = get_tabs(is_logged_in, is_admin)
    
    # Create columns for all general tabs
    general_tab_cols = [1] * len(tabs)
    
    # Create a spacer that will push the auth tab to the right
    # Using a large value ensures it takes up all available space
    spacer_ratio = 6
    
    # Create consistent margins on both sides
    left_margin = right_margin = MARGIN
    
    # Combine all column ratios
    return [left_margin] + general_tab_cols + [spacer_ratio] + [1] + [right_margin]

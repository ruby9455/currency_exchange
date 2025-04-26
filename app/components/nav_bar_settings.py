APP_NAME = "Currency Exchange"
MARGIN = 0.005
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
        general_tabs.append("用戶管理")

    return general_tabs, auth_tab

def get_cols_ratio(is_logged_in: bool, is_admin: bool):
    tabs, auth_tab = get_tabs(is_logged_in, is_admin)

    cols_ratio = [1] * (len(tabs) + len(auth_tab))
    spacer_ratio = 1/(len(tabs)+len(auth_tab))
    return [MARGIN] + cols_ratio[:-1] + [spacer_ratio] + [cols_ratio[-1]] + [MARGIN]

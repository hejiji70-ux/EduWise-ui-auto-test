"""
admin_pages.py — Admin 后台页面对象（Page Object Model）
"""

from playwright.sync_api import Page


class AdminLoginPage:
    """Admin 登录页页面对象"""

    def __init__(self, page: Page):
        self.page = page
        self.username_input = page.locator("input[name='username']")
        self.password_input = page.locator("input[name='password']")
        self.login_button = page.locator("button:has-text('登录')")
        self.error_message = page.locator(".el-form-item__error, .el-message--error")

    def goto(self, base_url: str):
        """导航到登录页"""
        self.page.goto(base_url + "/login", timeout=30_000)
        self.page.wait_for_load_state("networkidle")

    def login(self, username: str, password: str):
        """执行登录：填用户名+密码+点登录"""
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()

    def get_error_text(self) -> str:
        """获取错误提示文本"""
        return self.error_message.first.text_content(timeout=5_000) or ""


class AdminDashboardPage:
    """Admin 首页仪表盘（登录成功后的目标页面）"""

    def __init__(self, page: Page):
        self.page = page
        self.sidebar_menu = page.locator(".sidebar-container, .el-menu")

    def is_loaded(self) -> bool:
        """侧边栏可见即表示已成功进入后台"""
        return self.sidebar_menu.first.is_visible(timeout=10_000)


class AdminMemberPage:
    """Admin 学员管理页面"""

    def __init__(self, page: Page):
        self.page = page
        self.search_input = page.locator(
            ".el-table-wrapper input[type='text'], "
            ".el-table input.el-input__inner, "
            ".el-form input.el-input__inner"
        ).first
        self.search_button = page.locator("button:has-text('搜索'), button:has-text('查询')").first
        self.table = page.locator(".el-table")
        self.table_rows = page.locator(".el-table__row")

    def search(self, keyword: str):
        """输入搜索关键词并点击搜索按钮"""
        self.search_input.fill(keyword)
        self.search_button.click()
        self.page.wait_for_load_state("networkidle")

    def get_row_count(self) -> int:
        """获取表格当前页的数据行数"""
        return self.table_rows.count()


class AdminCoursePage:
    """Admin 课程管理页面"""

    def __init__(self, page: Page):
        self.page = page
        self.table = page.locator(".el-table")
        self.table_rows = page.locator(".el-table__row")
        self.pagination = page.locator(".el-pagination")

    def get_row_count(self) -> int:
        return self.table_rows.count()

    def get_total_text(self) -> str:
        """获取分页总条数文本（如 "共 100 条"）"""
        total_el = self.page.locator(".el-pagination__total")
        if total_el.is_visible(timeout=5_000):
            return total_el.text_content() or ""
        return ""

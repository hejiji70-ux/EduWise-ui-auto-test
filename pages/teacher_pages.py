"""
teacher_pages.py — Teacher 讲师端页面对象（Page Object Model）
登录表单 DOM 与 Admin 完全相同，账号字段为 username（值填手机号）
"""

from playwright.sync_api import Page


class TeacherLoginPage:
    """Teacher 讲师登录页"""

    def __init__(self, page: Page):
        self.page = page
        # 与 Admin 登录页完全相同的表单结构
        self.username_input = page.locator("input[name='username']")
        self.password_input = page.locator("input[name='password']")
        self.login_button = page.locator("button:has-text('登录')")
        self.error_tip = page.locator(".el-form-item__error, .el-message--error")

    def goto(self, base_url: str):
        """导航到讲师端登录页"""
        self.page.goto(base_url + "/login", timeout=30_000)
        self.page.wait_for_load_state("networkidle")

    def login(self, mobile_or_username: str, password: str):
        """执行登录（参数名叫 mobile 但实际填入 username 字段）"""
        self.username_input.fill(mobile_or_username)
        self.password_input.fill(password)
        self.login_button.click()


class TeacherDashboardPage:
    """Teacher 首页（登录后跳转至此）"""

    def __init__(self, page: Page):
        self.page = page
        # 讲师后台的侧边栏/导航菜单
        self.nav_menu = page.locator(".el-menu, .sidebar-container, nav")

    def is_loaded(self) -> bool:
        """导航菜单可见即表示已成功进入讲师后台"""
        return self.nav_menu.first.is_visible(timeout=10_000)


class TeacherCoursePage:
    """Teacher 课程管理页面"""

    def __init__(self, page: Page):
        self.page = page
        self.create_btn = page.locator("button:has-text('创建课程'), button:has-text('新建')").first
        self.table = page.locator(".el-table")
        self.table_rows = page.locator(".el-table__row")
        self.title_input = page.locator("input[placeholder*='课程名'], input[placeholder*='标题']").first
        self.submit_btn = page.locator("button[type='submit'], .el-button--primary:has-text('保存')").first

    def get_row_count(self) -> int:
        """获取表格数据行数"""
        return self.table_rows.count()

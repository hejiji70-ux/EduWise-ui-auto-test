"""
app_pages.py — App 学员端页面对象（Page Object Model）
App 登录为对话框模式（非独立 /login 页面），入口是导航栏"登录/注册"链接
"""

from playwright.sync_api import Page


class AppHomePage:
    """App 首页"""

    def __init__(self, page: Page):
        self.page = page
        self.banner = page.locator(".banner, .swiper, .el-carousel").first
        self.course_cards = page.locator(".course-card, .course-item, .el-card")
        self.search_input = page.locator("input[placeholder*='搜索']").first
        self.login_link = page.locator("text=登录/注册")

    def goto(self, base_url: str):
        """访问 App 首页"""
        self.page.goto(base_url, timeout=30_000)
        self.page.wait_for_load_state("networkidle")

    def click_login_link(self):
        """点击导航栏的'登录/注册'链接→弹出登录对话框"""
        self.login_link.click()
        self.page.locator(".el-dialog.login").wait_for(state="visible", timeout=10_000)

    def get_course_card_count(self) -> int:
        """获取首页课程卡片数量"""
        return self.course_cards.count()


class AppLoginDialog:
    """App 登录对话框（el-dialog 组件，非独立页面）"""

    def __init__(self, page: Page):
        self.page = page
        dialog = ".el-dialog.login"
        self.mobile_input = page.locator(f"{dialog} input[placeholder*='手机号']").first
        self.password_input = page.locator(f"{dialog} input[type='password']").first
        self.login_button = page.locator(f"{dialog} button:has-text('登 录')")
        self.register_button = page.locator(f"{dialog} button:has-text('注 册')")
        self.error_tip = page.locator(f"{dialog} .el-form-item__error, {dialog} .el-message--error")
        self.dialog = page.locator(dialog)

    def is_visible(self) -> bool:
        """检查登录对话框是否正在显示"""
        try:
            return self.dialog.is_visible(timeout=3_000)
        except Exception:
            return False

    def fill_login_form(self, mobile: str, password: str):
        """填写手机号和密码（参数化以支持正确/错误账密场景）"""
        self.mobile_input.fill(mobile)
        self.password_input.fill(password)

    def submit(self):
        """点击登录按钮提交表单"""
        self.login_button.click()

    def wait_until_closed(self, timeout: int = 20_000):
        """等待对话框关闭（同时检查 hidden/detached/visibility 三种状态）"""
        import time as _time
        deadline = _time.time() + (timeout / 1000)
        while _time.time() < deadline:
            try:
                if not self.dialog.is_visible(timeout=500):
                    return
                if self.dialog.count() == 0:
                    return
            except Exception:
                return
            _time.sleep(0.5)


# 兼容旧引用的别名（test_app_ui.py 可能用到）
AppLoginPage = AppLoginDialog


class AppCourseListPage:
    """App 课程列表页"""

    def __init__(self, page: Page):
        self.page = page
        self.course_cards = page.locator(".course-card, .course-item, .course-list .item")
        self.no_data_tip = page.locator(".no-data, .empty-tip")

    def get_course_card_count(self) -> int:
        return self.course_cards.count()


class AppCourseDetailPage:
    """App 课程详情页"""

    def __init__(self, page: Page):
        self.page = page
        self.course_title = page.locator(".course-title, .detail-title, h1, h2").first
        self.enroll_btn = page.locator("button:has-text('立即学习'), button:has-text('免费学习')").first
        self.chapter_list = page.locator(".chapter-list, .section-list")

    def get_title(self) -> str:
        return self.course_title.text_content(timeout=5_000) or ""

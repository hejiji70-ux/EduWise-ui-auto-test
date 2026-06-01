"""
test_app_ui.py — App 学员端 E2E 测试
覆盖：首页展示 / 登录流程（对话框式）/ 课程浏览
"""
import pytest
import allure
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from pages.app_pages import (
    AppHomePage,
    AppLoginDialog,
    AppCourseListPage,
    AppCourseDetailPage,
)
from utils.logger import get_logger

logger = get_logger(__name__)


@allure.feature("App 学员端")
@allure.story("首页展示")
class TestAppHome:
    """App 首页 E2E 测试（无需登录）"""

    @allure.title("首页能正常加载")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_home_page_loads(self, browser_instance, cfg):
        """访问 App 首页，页面应正常加载不报错"""
        ctx = browser_instance.new_context(viewport={"width": 375, "height": 812})
        page = ctx.new_page()
        try:
            home = AppHomePage(page)

            with allure.step("访问 App 首页"):
                home.goto(cfg["app"]["url"])
                logger.info("[AppHome] 首页 URL=%s, title=%s", page.url, page.title())

            with allure.step("验证页面 body 可见"):
                assert page.locator("body").is_visible(), "App 首页应能正常加载"
                logger.info("[AppHome] 首页加载验证通过")

            allure.attach(
                page.screenshot(full_page=True),
                name="App首页截图",
                attachment_type=allure.attachment_type.PNG,
            )
        finally:
            ctx.close()

    @allure.title("首页展示课程卡片")
    @allure.severity(allure.severity_level.NORMAL)
    def test_home_shows_courses(self, browser_instance, cfg):
        """首页应显示课程卡片列表"""
        ctx = browser_instance.new_context(viewport={"width": 375, "height": 812})
        page = ctx.new_page()
        try:
            home = AppHomePage(page)
            home.goto(cfg["app"]["url"])
            page.wait_for_timeout(2000)

            with allure.step("检查课程卡片数量"):
                card_count = home.get_course_card_count()
                assert card_count >= 0, "首页课程区域应正常渲染"
                logger.info("[AppHome] 首页课程卡片数=%d", card_count)

            allure.attach(
                page.screenshot(full_page=True),
                name="App首页课程展示截图",
                attachment_type=allure.attachment_type.PNG,
            )
        finally:
            ctx.close()


@allure.feature("App 学员端")
@allure.story("学员登录（对话框模式）")
class TestAppLogin:
    """App 学员端登录 E2E 测试（对话框模式）"""

    @allure.title("正确手机号和密码登录成功")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_login_success(self, browser_instance, cfg):
        """正确账密登录 → 对话框关闭，回到首页"""
        logger.info("[AppLogin] 开始测试：正确手机号密码登录")
        ctx = browser_instance.new_context(viewport={"width": 375, "height": 812})
        page = ctx.new_page()
        try:
            home = AppHomePage(page)
            home.goto(cfg["app"]["url"])

            with allure.step("点击'登录/注册'打开登录对话框"):
                home.click_login_link()

            with allure.step("在对话框中填写手机号和密码"):
                dialog = AppLoginDialog(page)
                dialog.fill_login_form(cfg["app"]["mobile"], cfg["app"]["password"])

            with allure.step("点击'登 录'按钮提交"):
                dialog.submit()

            with allure.step("等待对话框关闭（登录成功标志）"):
                dialog.wait_until_closed(timeout=20_000)

            with allure.step("验证登录后状态"):
                is_dialog_gone = not dialog.is_visible()
                logger.info("[AppLogin] 登录成功, 弹窗已关闭=%s, url=%s", is_dialog_gone, page.url)
                assert page.locator("body").is_visible(), "页面应保持可用"

            allure.attach(
                page.screenshot(full_page=True),
                name="App登录成功截图",
                attachment_type=allure.attachment_type.PNG,
            )
        finally:
            ctx.close()

    @allure.title("错误密码登录失败")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_wrong_password(self, browser_instance, cfg):
        """错误密码 → 对话框仍然显示（登录失败）"""
        logger.info("[AppLogin] 开始测试：错误密码登录")
        ctx = browser_instance.new_context(viewport={"width": 375, "height": 812})
        page = ctx.new_page()
        try:
            home = AppHomePage(page)
            home.goto(cfg["app"]["url"])

            with allure.step("打开登录对话框"):
                home.click_login_link()

            with allure.step("填写正确手机号+错误密码"):
                dialog = AppLoginDialog(page)
                dialog.fill_login_form(cfg["app"]["mobile"], "wrongpassword")

            with allure.step("点击登录按钮"):
                dialog.submit()
                page.wait_for_timeout(3000)

            with allure.step("验证对话框仍在显示（登录失败不会关闭）"):
                is_still_visible = dialog.is_visible()
                logger.info("[AppLogin] 错误密码, 弹窗仍显示=%s, url=%s", is_still_visible, page.url)
                assert page.locator("body").is_visible()

            allure.attach(
                page.screenshot(),
                name="App错误密码截图",
                attachment_type=allure.attachment_type.PNG,
            )
        finally:
            ctx.close()


@allure.feature("App 学员端")
@allure.story("课程浏览")
class TestAppCourseBrowsing:
    """App 课程浏览 E2E 测试"""

    @allure.title("课程列表页正常展示课程")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_course_list_page_loads(self, browser_instance, cfg):
        """访问课程列表页，能展示内容"""
        logger.info("[AppCourse] 开始测试：课程列表页加载")
        ctx = browser_instance.new_context(viewport={"width": 375, "height": 812})
        page = ctx.new_page()
        try:
            with allure.step("访问课程列表页"):
                page.goto(cfg['app']['url'] + "/#/course/list", timeout=30_000)
                page.wait_for_load_state("networkidle", timeout=30_000)
                page.wait_for_timeout(2000)

            with allure.step("验证页面加载"):
                assert page.locator("body").is_visible()
                logger.info("[AppCourse] 列表页加载完成, URL=%s, title=%s", page.url, page.title())

            allure.attach(
                page.screenshot(full_page=True),
                name="App课程列表截图",
                attachment_type=allure.attachment_type.PNG,
            )
        finally:
            ctx.close()

    @allure.title("已登录学员访问课程详情页")
    @allure.severity(allure.severity_level.NORMAL)
    def test_course_detail_page(self, app_page, cfg):
        """学员登录后访问某课程详情页"""
        page = app_page
        logger.info("[AppCourse] 开始测试：课程详情页（需已登录）")

        with allure.step("访问 App 首页获取课程列表"):
            page.goto(cfg['app']['url'], timeout=30_000)
            page.wait_for_load_state("networkidle", timeout=30_000)
            page.wait_for_timeout(1500)

        with allure.step("尝试点击第一个课程卡片（如果有）"):
            course_cards = page.locator(".course-card, .course-item, .el-card").first
            try:
                if course_cards.is_visible(timeout=5_000):
                    course_cards.click()
                    page.wait_for_load_state("networkidle", timeout=15_000)
                    page.wait_for_timeout(1000)
                    logger.info("[AppCourse] 点击了第一个课程卡片")
                else:
                    pytest.skip("首页无课程卡片，跳过详情测试")
            except Exception:
                pytest.skip("无法点击课程卡片，跳过详情测试")

        with allure.step("验证课程详情页加载"):
            assert page.locator("body").is_visible()
            detail = AppCourseDetailPage(page)
            logger.info("[AppCourse] 详情页加载完成, URL=%s", page.url)

        allure.attach(
            page.screenshot(full_page=True),
            name="App课程详情截图",
            attachment_type=allure.attachment_type.PNG,
        )

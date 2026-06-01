"""
tests/test_teacher_ui.py — Teacher 讲师端 E2E 测试
覆盖：登录流程 / 课程列表
"""
import pytest
import allure
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from pages.teacher_pages import TeacherLoginPage, TeacherDashboardPage, TeacherCoursePage
from utils.logger import get_logger

logger = get_logger(__name__)


@allure.feature("Teacher 讲师端")
@allure.story("讲师登录")
class TestTeacherLogin:
    """Teacher 登录流程 E2E 测试"""

    @allure.title("正确手机号和密码登录成功")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_login_success(self, teacher_page, cfg):
        """正确手机号登录 → 已进入讲师后台首页（导航菜单可见）"""
        page = teacher_page

        with allure.step("验证首页导航菜单可见"):
            dashboard = TeacherDashboardPage(page)
            assert dashboard.is_loaded(), "讲师后台首页导航应可见"

        logger.info("[TeacherLogin] 正确手机号登录验证通过")

        allure.attach(
            page.screenshot(full_page=True),
            name="Teacher登录后首页截图",
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.title("错误密码登录失败，页面停留在登录页")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_wrong_password(self, browser_instance, cfg):
        """错误密码 → 登录失败，停留在 /login"""
        logger.info("[TeacherLogin] 开始测试：错误密码登录")
        ctx = browser_instance.new_context(viewport={"width": 1280, "height": 720})
        page = ctx.new_page()
        try:
            login_page = TeacherLoginPage(page)
            login_page.goto(cfg["teacher"]["url"])

            with allure.step("输入错误密码并提交"):
                login_page.login(cfg["teacher"]["mobile"], "wrongpassword")
                page.wait_for_timeout(2000)

            with allure.step("验证仍在登录页"):
                assert "/login" in page.url, f"错误密码不应跳转，当前URL: {page.url}"

            logger.info("[TeacherLogin] 错误密码验证通过（仍在登录页）")

            allure.attach(
                page.screenshot(),
                name="Teacher错误密码截图",
                attachment_type=allure.attachment_type.PNG,
            )
        finally:
            ctx.close()

    @allure.title("未注册手机号登录失败")
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_unregistered_mobile(self, browser_instance, cfg):
        """未注册手机号 → 登录失败"""
        logger.info("[TeacherLogin] 开始测试：未注册手机号登录")
        ctx = browser_instance.new_context(viewport={"width": 1280, "height": 720})
        page = ctx.new_page()
        try:
            login_page = TeacherLoginPage(page)
            login_page.goto(cfg["teacher"]["url"])

            with allure.step("输入未注册手机号"):
                login_page.login("19999999999", "123456")
                page.wait_for_timeout(2000)

            with allure.step("验证仍在登录页"):
                assert "/login" in page.url, "未注册手机号不应登录成功"

            logger.info("[TeacherLogin] 未注册手机号验证通过")

            allure.attach(
                page.screenshot(),
                name="Teacher未注册手机截图",
                attachment_type=allure.attachment_type.PNG,
            )
        finally:
            ctx.close()


@allure.feature("Teacher 讲师端")
@allure.story("课程管理")
class TestTeacherCourseUI:
    """Teacher 课程管理 E2E 测试"""

    @allure.title("进入课程列表页面，能正常加载")
    @allure.severity(allure.severity_level.NORMAL)
    def test_course_list_page_loads(self, teacher_page, cfg):
        """课程列表页正常加载"""
        page = teacher_page

        with allure.step("导航到讲师课程管理页"):
            page.goto(cfg['teacher']['url'] + "/#/course/list", timeout=20_000)
            page.wait_for_load_state("networkidle", timeout=20_000)
            page.wait_for_timeout(1500)

        with allure.step("验证页面主体可见"):
            assert page.locator("body").is_visible(), "页面主体应可见"
            logger.info("[TeacherCourse] 列表页加载完成, URL=%s", page.url)

        allure.attach(
            page.screenshot(full_page=True),
            name="Teacher课程列表截图",
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.title("课程列表有数据或正常展示")
    @allure.severity(allure.severity_level.NORMAL)
    def test_course_list_has_data(self, teacher_page, cfg):
        """课程列表应有数据（如果有的话）"""
        page = teacher_page

        with allure.step("导航到讲师课程列表"):
            page.goto(cfg['teacher']['url'] + "/#/course/list", timeout=20_000)
            page.wait_for_load_state("networkidle", timeout=20_000)
            page.wait_for_timeout(2000)

        with allure.step("检查表格行数"):
            course_page = TeacherCoursePage(page)
            row_count = course_page.get_row_count()
            if row_count == 0:
                logger.info("[TeacherCourse] 讲师暂无课程数据，跳过")
                pytest.skip("讲师暂无课程数据，跳过该测试")
            assert row_count > 0, "课程列表应有数据"
            logger.info("[TeacherCourse] 行数=%d", row_count)

        allure.attach(
            page.screenshot(full_page=True),
            name="Teacher课程数据截图",
            attachment_type=allure.attachment_type.PNG,
        )

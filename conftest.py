"""
conftest.py — Playwright UI 自动化测试配置与 Fixture
三端登录方案：
- Admin/Teacher: API Login + Token 注入 localStorage（绕过 CORS）
- App: UI 点击"登录/注册"链接 → el-dialog 对话框内填写表单
"""

import sys
import time
import pytest
import yaml
import allure
from pathlib import Path
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page

from utils.logger import get_logger, get_allure_log_text, clear_allure_logs

logger = get_logger("ui-test.conftest")


# ── 配置加载 ──────────────────────────────────────────

def load_config() -> dict:
    """加载 UI 测试专用的 config.yaml（含 URL、viewport、headless 等设置）"""
    cfg_path = Path(__file__).parent / "config" / "config.yaml"
    with open(cfg_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="session")
def cfg() -> dict:
    """全局配置 fixture（session 级别，只加载一次）"""
    return load_config()


# ── 浏览器 Fixture（session 级别）──────────────────────

@pytest.fixture(scope="session")
def browser_instance(cfg):
    """
    启动浏览器实例（session 级别，整批测试只启动一次）
    优先使用系统 Chrome，不可用时 fallback 到 Chromium
    """
    pw_cfg = cfg.get("playwright", {})
    headless = pw_cfg.get("headless", True)
    slow_mo = pw_cfg.get("slow_mo", 0)

    logger.info("启动浏览器: headless=%s, slow_mo=%s", headless, slow_mo)

    with sync_playwright() as pw:
        try:
            browser = pw.chromium.launch(
                channel="chrome",
                headless=headless,
                slow_mo=slow_mo,
            )
        except Exception:
            browser = pw.chromium.launch(
                headless=headless,
                slow_mo=slow_mo,
            )
        yield browser
        browser.close()
    logger.info("浏览器已关闭")


def _new_context(browser: "Browser", cfg: dict) -> "BrowserContext":
    """创建隔离的浏览器上下文（独立 Cookie/Storage，确保三端互不干扰）"""
    vp = cfg.get("playwright", {}).get("viewport", {"width": 1280, "height": 720})
    ctx = browser.new_context(
        viewport={"width": vp["width"], "height": vp["height"]},
        ignore_https_errors=True,
    )
    logger.info("创建浏览器上下文: viewport=%sx%s", vp["width"], vp["height"])
    return ctx


# ── Admin 后台 Fixture ─────────────────────────────────

@pytest.fixture(scope="class")
def admin_page(browser_instance, cfg) -> Page:
    """Admin 已登录页面对象（class 级别，同测试类共享登录态）"""
    logger.info(">>> [Admin] 准备创建已登录页面")
    ctx = _new_context(browser_instance, cfg)
    page = ctx.new_page()
    _admin_login(page, cfg)
    yield page
    ctx.close()
    logger.info("<<< [Admin] 上下文已关闭")


def _admin_login(page: Page, cfg: dict):
    """
    Admin 登录：API Login + Token 注入 localStorage（绕过前端 CORS 跨域限制）
    流程：requests 登录 → 取 token → page.evaluate 注入 → 导航到 dashboard
    """
    logger.info("[Admin] 开始 API 登录...")
    import requests as _requests

    api_base = cfg["admin"].get("api_base", "http://localhost:9096")
    login_url = f"{api_base}/api/admin/user/login"
    username = cfg["admin"]["username"]
    password = cfg["admin"]["password"]

    resp = _requests.post(login_url, json={"username": username, "password": password}, timeout=10)
    data = resp.json()

    if data.get("status") != 200 or "data" not in data or not data["data"].get("token"):
        logger.error("[Admin] API 登录失败: %s", data.get("message", "未知错误"))
        import pytest as _pytest
        _pytest.skip(
            f"Admin API 登录失败: {data.get('message', '未知错误')}\n"
            f"URL={login_url}, username={username}\n"
            f"请检查后端服务是否正常启动"
        )

    token = data["data"]["token"]
    logger.info("[Admin] API 登录成功, token=%s...", token[:20])

    admin_url = cfg["admin"]["url"]
    logger.info("[Admin] 导航到登录页: %s/login", admin_url)
    page.goto(admin_url + "/login", timeout=30_000)
    page.wait_for_load_state("networkidle", timeout=30_000)

    page.evaluate("(token) => { localStorage.setItem('token', token); }", token)
    logger.info("[Admin] Token 已注入 localStorage")

    page.goto(admin_url + "/#/dashboard", timeout=30_000)
    page.wait_for_load_state("networkidle", timeout=15_000)

    assert "#/dashboard" in page.url or "#/login" not in page.url, \
        f"Admin token 注入后未进入 dashboard。当前 URL: {page.url}"
    logger.info("[Admin] 已进入 dashboard, url=%s", page.url)


# ── Teacher 讲师端 Fixture ──────────────────────────────

@pytest.fixture(scope="class")
def teacher_page(browser_instance, cfg) -> Page:
    """Teacher 已登录页面对象"""
    logger.info(">>> [Teacher] 准备创建已登录页面")
    ctx = _new_context(browser_instance, cfg)
    page = ctx.new_page()
    _teacher_login(page, cfg)
    yield page
    ctx.close()
    logger.info("<<< [Teacher] 上下文已关闭")


def _teacher_login(page: Page, cfg: dict):
    """Teacher 登录（与 Admin 方案相同，URL 和 API 路径不同）"""
    logger.info("[Teacher] 开始 API 登录...")
    import requests as _requests

    api_base = cfg["teacher"].get("api_base", "http://localhost:9096")
    login_url = f"{api_base}/api/teacher/user/login"
    mobile = cfg["teacher"]["mobile"]
    password = cfg["teacher"]["password"]

    resp = _requests.post(login_url, json={"username": mobile, "password": password}, timeout=10)
    data = resp.json()

    if data.get("status") != 200 or "data" not in data or not data["data"].get("token"):
        logger.error("[Teacher] API 登录失败: %s", data.get("message", "未知错误"))
        import pytest as _pytest
        _pytest.skip(
            f"Teacher API 登录失败: {data.get('message', '未知错误')}\n"
            f"URL={login_url}, mobile={mobile}\n"
            f"请检查后端服务是否正常启动"
        )

    token = data["data"]["token"]
    logger.info("[Teacher] API 登录成功, token=%s...", token[:20])

    teacher_url = cfg["teacher"]["url"]
    logger.info("[Teacher] 导航到登录页: %s/login", teacher_url)
    page.goto(teacher_url + "/login", timeout=30_000)
    page.wait_for_load_state("networkidle", timeout=30_000)

    page.evaluate("(token) => { localStorage.setItem('token', token); }", token)
    logger.info("[Teacher] Token 已注入 localStorage")

    page.goto(teacher_url + "/#/dashboard", timeout=30_000)
    page.wait_for_load_state("networkidle", timeout=15_000)

    assert "#/dashboard" in page.url or "#/login" not in page.url, \
        f"Teacher token 注入后未进入 dashboard。当前 URL: {page.url}"
    logger.info("[Teacher] 已进入 dashboard, url=%s", page.url)


# ── App 学员端 Fixture ─────────────────────────────────

@pytest.fixture(scope="class")
def app_page(browser_instance, cfg) -> Page:
    """App 学员端已登录页面对象"""
    logger.info(">>> [App] 准备创建已登录页面")
    ctx = _new_context(browser_instance, cfg)
    page = ctx.new_page()
    _app_login(page, cfg)
    yield page
    ctx.close()
    logger.info("<<< [App] 上下文已关闭")


def _app_login(page: Page, cfg: dict):
    """App 学员端登录（首页点击"登录/注册"→ 弹出 el-dialog 对话框填写表单）"""
    url = cfg["app"]["url"]

    logger.info("[App] 导航到首页: %s", url)
    page.goto(url, timeout=30_000)
    page.wait_for_load_state("networkidle", timeout=30_000)
    page.wait_for_timeout(1000)

    try:
        page.locator("text=登录/注册").click(timeout=10_000)
    except Exception:
        page.locator(":text('登录')").first.click(timeout=5_000)

    dialog = page.locator(".el-dialog.login")
    dialog.wait_for(state="visible", timeout=10_000)
    logger.info("[App] 登录弹窗已显示")
    page.wait_for_timeout(500)

    mobile_input = dialog.locator("input[placeholder*='手机号']").first
    mobile_input.click(timeout=5_000)
    mobile_input.fill(cfg["app"]["mobile"])

    pwd_input = dialog.locator("input[type='password']").first
    pwd_input.fill(cfg["app"]["password"])

    try:
        dialog.locator("button:has-text('登 录')").click(timeout=5_000)
    except Exception:
        dialog.locator("button:has-text('登录')").click(timeout=5_000)

    logger.info("[App] 已点击登录按钮，等待弹窗关闭...")

    deadline = time.time() + 20
    while time.time() < deadline:
        try:
            if not dialog.is_visible(timeout=500):
                logger.info("[App] 登录成功，弹窗已关闭")
                return
            if dialog.count() == 0:
                logger.info("[App] 登录成功，弹窗已消失")
                return
        except Exception:
            return
        page.wait_for_timeout(500)

    try:
        screenshot = page.screenshot(full_page=True)
        allure.attach(screenshot, name="App登录弹窗未关闭-调试截图",
                      attachment_type=allure.attachment_type.PNG)
    except Exception:
        pass

    logger.warning("[App] 登录弹窗未能在 20s 内关闭, url=%s", page.url)


# ── 全局 Hook：日志清理 + 失败自动截图 ──────────────────

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """每个测试开始前清空日志缓冲区"""
    clear_allure_logs()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """测试失败时：附加日志 + 截图到 Allure 报告"""
    outcome = yield
    rep = outcome.get_result()

    # 测试结束时附加日志文本
    if rep.when == "call":
        log_text = get_allure_log_text().strip()
        if log_text:
            allure.attach(log_text, name="执行日志",
                          attachment_type=allure.attachment_type.TEXT)

    # 失败时额外截图
    if rep.when == "call" and rep.failed:
        logger.error("[%s] 测试失败，正在截取失败截图...", item.name)
        page = None
        for fixture_name in ("admin_page", "teacher_page", "app_page"):
            page = item.funcargs.get(fixture_name)
            if page is not None:
                break

        if page is not None:
            try:
                screenshot = page.screenshot(full_page=True)
                allure.attach(screenshot, name=f"失败截图_{item.name}",
                              attachment_type=allure.attachment_type.PNG)
            except Exception:
                logger.error("[%s] 截图也失败了", item.name)

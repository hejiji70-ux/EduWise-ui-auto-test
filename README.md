# EduWise 智课 — UI 自动化测试

## 项目简介

基于 Python + Playwright 的 UI 自动化测试框架，覆盖 EduWise 智课平台 Admin 后台、Teacher 讲师端、App 学员端三端核心页面操作。

## 技术栈

- Python 3.x
- Playwright（浏览器自动化）
- Pytest（测试框架）
- Pytest-html / Allure（测试报告）

## 项目结构

```
EduWise-ui-auto-test/
├── README.md
├── requirements.txt        # Python 依赖
├── pytest.ini             # Pytest 配置
├── conftest.py           # Pytest 固件（浏览器启动、登录）
├── .gitignore
├── .github/
│   └── workflows/
│       └── ci.yml        # GitHub Actions CI 配置
├── config/
│   └── config.yaml      # 测试环境配置（URL、账号密码）
├── pages/                 # 页面对象（POM 模式）
│   ├── admin_login_page.py
│   ├── admin_user_page.py
│   ├── teacher_login_page.py
│   ├── app_home_page.py
│   └── ...
├── tests/                 # 测试用例
│   ├── test_admin_login.py
│   ├── test_teacher_login.py
│   ├── test_app_login.py
│   └── ...
└── utils/           # 工具类
    └──  logger.py   # 日志

```

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
playwright install chromium
```

### 运行测试

```bash
# 运行全部测试
pytest tests/ -v

# 运行 Admin 端测试
pytest tests/test_admin_login.py -v

# 生成 HTML 报告
pytest tests/ -v --html=reports/report.html

# 生成 Allure 报告
pytest tests/ -v --alluredir=allure-results
allure generate allure-results -o allure-report
```


## 测试结果

- 总用例数：17
- 通过：16
- 跳过：1（需人工确认）
- 通过率：94.1%

## CI/CD

推送到 GitHub 后，Actions 自动运行：
- 安装 Python + Playwright
- 安装 Chromium 浏览器
- 运行 UI 自动化测试
- 上传测试报告和截图作为 Artifacts

## 注意事项

- 运行测试前需启动本地 Docker 服务（前端 + 后端）
- Admin 端访问：http://localhost:9096/admin/
- Teacher 端访问：http://localhost:9096/teacher/
- App 端访问：http://localhost:9096/app/
- 测试使用 API Login + Token 注入方式绕过前端登录页面跨域问题

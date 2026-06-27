# 项目重构与完善规格说明（修订版 v2）

## 1. 目标

将学生学业预警与成长分析平台从当前 85-90% 完成度提升至 100%，修复所有已知缺陷，执行全面重构以达到课程设计交付标准，并推送到 GitHub。

## 2. 范围边界

### 包含
- 修复所有 Critical/High 级别缺陷（含 `make_response` 导入缺失）
- 消除根目录模块重复，统一为 `src/` 单一代码树
- Flask 应用重构为 Blueprint 架构
- 安全加固（认证、RBAC、密码哈希 + 迁移）
- 补齐缺失依赖、修正 README
- 添加单元测试（含冒烟测试）
- 清理冗余文件和运行时数据
- 推送到 GitHub

### 不包含
- 生产级部署配置（WSGI、Docker、CI/CD）
- 前端框架迁移（保持 Flask + 单页 HTML）
- 数据库迁移（保持 JSON 文件存储）
- HTTPS/TLS 配置

### 已知缺陷清单（需在重构中修复）
1. `src/app.py` line 1：缺少 `make_response` 导入 → Excel 模板下载崩溃
2. `src/app.py` line 15：硬编码 secret key
3. `src/app.py` line 7：`numpy` 未使用导入
4. `src/auth/auth.py` line 66：SHA-256 无盐密码哈希
5. `requirements.txt`：缺少 `requests`、`pytest`
6. README：默认凭证与代码不一致

## 3. 技术方案

### 3.1 项目结构重组

**原则**：所有源码保留在 `src/` 下，删除根目录重复模块。

```
项目根目录/
├── run.py                    # 启动入口（更新：调用 create_app()）
├── requirements.txt          # 依赖清单（更新）
├── README.md                 # 文档（更新）
├── llm_config.json           # LLM 配置（保留）
├── .gitignore                # 更新
├── data/                     # 数据文件（保留）
├── advanced_data/            # 高级数据（保留）
├── reports/                  # 生成报告（保留）
├── templates/                # Flask 模板（唯一副本）
├── src/
│   ├── __init__.py           # 包初始化
│   ├── app.py                # Flask 工厂 + Blueprint 注册
│   ├── blueprints/
│   │   ├── __init__.py
│   │   ├── auth_bp.py
│   │   ├── data_bp.py
│   │   ├── warning_bp.py
│   │   ├── analysis_bp.py
│   │   ├── report_bp.py
│   │   └── llm_bp.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── decorators.py     # 认证与 RBAC 装饰器
│   ├── auth/                 # 认证模块
│   ├── data_processing/
│   ├── classification/
│   ├── association_rules/
│   ├── group_analysis/       # 补 __init__.py
│   ├── learning_path_recommendation/
│   ├── report_generator/
│   ├── llm_integration/
│   ├── student_behavior_representation/
│   ├── gnn_explanation/
│   ├── student_behavior_anomaly_detection.py
│   ├── academic_warning.py
│   ├── data_generator.py
│   └── reset_lock.py
├── tests/
│   ├── __init__.py
│   ├── test_app.py           # 冒烟测试：工厂、路由注册、认证保护
│   ├── test_auth.py
│   ├── test_data_processing.py
│   └── test_classification.py
└── instance/                 # 运行时数据（.gitignore 排除）
    └── auth/
        ├── users.json
        ├── login_logs.json
        └── failed_attempts.json
```

**删除的根目录重复包**：`association_rules/`、`classification/`、`data_processing/`、`gnn_explanation/`、`group_analysis/`、`learning_path_recommendation/`、`report_generator/`、`llm_integration/`、`student_behavior_representation/`、`auth/`（仅 .py 源文件副本；运行时 JSON 数据先迁移到 `instance/auth/`）

**删除的冗余文件**：`src/templates/index.html`、`group_dashboard.html`、`__pycache__/`

### 3.2 Flask 工厂模式

```python
# src/app.py
import os
from flask import Flask

def create_app():
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    app = Flask(__name__, template_folder=os.path.join(basedir, 'templates'))
    
    # 配置：不使用 from_pyfile，直接设置
    app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-env')
    app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'data')
    app.config['INSTANCE_PATH'] = os.path.join(basedir, 'instance')
    
    # 注册蓝图
    from src.blueprints.auth_bp import auth_bp
    from src.blueprints.data_bp import data_bp
    from src.blueprints.warning_bp import warning_bp
    from src.blueprints.analysis_bp import analysis_bp
    from src.blueprints.report_bp import report_bp
    from src.blueprints.llm_bp import llm_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(data_bp)
    app.register_blueprint(warning_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(llm_bp)
    
    return app
```

**run.py 更新**：
```python
from src.app import create_app
app = create_app()
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

### 3.3 路由到 Blueprint 映射表

| 当前路由 | Blueprint | 装饰器 |
|:---|:---|:---|
| `GET /` | `data_bp` | `@data_bp.route('/')` |
| `POST /upload` | `data_bp` | `@data_bp.route('/upload', methods=['POST'])` |
| `GET /download-template/<name>` | `data_bp` | `@data_bp.route('/download-template/<template_name>')` |
| `GET /download-excel-template` | `data_bp` | `@data_bp.route('/download-excel-template')` |
| `GET /get-template-info` | `data_bp` | `@data_bp.route('/get-template-info')` |
| `POST /run-warning` | `warning_bp` | `@warning_bp.route('/run-warning', methods=['POST'])` |
| `GET /get-warning-report` | `warning_bp` | `@warning_bp.route('/get-warning-report')` |
| `GET /get-student-detail/<id>` | `warning_bp` | `@warning_bp.route('/get-student-detail/<student_id>')` |
| `GET /send-warning/<id>` | `warning_bp` | `@warning_bp.route('/send-warning/<student_id>')` |
| `POST /send-batch-warning` | `warning_bp` | `@warning_bp.route('/send-batch-warning', methods=['POST'])` |
| `GET /get-group-analysis` | `analysis_bp` | `@analysis_bp.route('/get-group-analysis')` |
| `GET /get-recommendations/<id>` | `analysis_bp` | `@analysis_bp.route('/get-recommendations/<student_id>')` |
| `GET /get-llm-recommendations/<id>` | `analysis_bp` | `@analysis_bp.route('/get-llm-recommendations/<student_id>')` |
| `GET /get-grade-distribution` | `analysis_bp` | `@analysis_bp.route('/get-grade-distribution')` |
| `GET /get-feature-importance` | `analysis_bp` | `@analysis_bp.route('/get-feature-importance')` |
| `GET /get-historical-trend` | `analysis_bp` | `@analysis_bp.route('/get-historical-trend')` |
| `POST /generate-report` | `report_bp` | `@report_bp.route('/generate-report', methods=['POST'])` |
| `GET /get-llm-config` | `llm_bp` | `@llm_bp.route('/get-llm-config')` |
| `POST /save-llm-config` | `llm_bp` | `@llm_bp.route('/save-llm-config', methods=['POST'])` |
| `GET /generate-student-analysis/<id>` | `llm_bp` | `@llm_bp.route('/generate-student-analysis/<student_id>')` |
| `POST /test-llm-connection` | `llm_bp` | `@llm_bp.route('/test-llm-connection', methods=['POST'])` |
| `POST /api/login` | `auth_bp` | `@auth_bp.route('/api/login', methods=['POST'])` |
| `POST /api/logout` | `auth_bp` | `@auth_bp.route('/api/logout', methods=['POST'])` |
| `GET /api/check-auth` | `auth_bp` | `@auth_bp.route('/api/check-auth')` |
| `GET /api/users` | `auth_bp` | `@auth_bp.route('/api/users')` |
| `POST /api/users` | `auth_bp` | `@auth_bp.route('/api/users', methods=['POST'])` |
| `DELETE /api/users/<id>` | `auth_bp` | `@auth_bp.route('/api/users/<user_id>', methods=['DELETE'])` |
| `POST /api/behavior-analysis` | `analysis_bp` | `@analysis_bp.route('/api/behavior-analysis', methods=['POST'])` |
| `POST /api/anomaly-detection` | `analysis_bp` | `@analysis_bp.route('/api/anomaly-detection', methods=['POST'])` |

### 3.4 安全加固

**认证装饰器**（`src/core/decorators.py`）：

```python
from functools import wraps
from flask import session, jsonify

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('authenticated'):
            return jsonify({'status': 'error', 'message': '未登录'}), 401
        return f(*args, **kwargs)
    return decorated

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if session.get('role') not in roles:
                return jsonify({'status': 'error', 'message': '权限不足'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator
```

**密码哈希迁移**：
1. 切换 `src/auth/auth.py` 使用 `werkzeug.security.generate_password_hash` / `check_password_hash`
2. 迁移策略：检测旧格式（64 位十六进制字符串）→ 对 `admin` 账户使用默认密码 `Admin@123` 重新哈希；对其他旧格式账户，标记为"需密码重置"状态，登录时提示联系管理员
3. 迁移日志输出受影响用户数量
4. 迁移代码仅在首次启动时执行一次（检测旧格式后自动转换并保存）
5. 确保 `admin/Admin@123` 在迁移后可正常登录

**AuthManager 路径迁移**：
- 将 `auth/users.json` 等文件迁移到 `instance/auth/`
- `AuthManager.__init__` 接受 `instance_path` 参数，构造绝对路径
- Blueprint 初始化时传入 `app.config['INSTANCE_PATH']`

**Secret Key**：使用 `os.environ.get('SECRET_KEY', 'dev-secret-key-for-local')`（固定开发 fallback，避免重启导致 session 失效）。

### 3.5 Blueprint 实现策略

**不引入 DataService**。Blueprint 中保持原有的 CSV 读取模式（直接 `pd.read_csv()`），与当前行为完全一致。避免引入新的抽象层增加复杂度和风险。后续可作为优化项单独处理。

每个 Blueprint 文件结构：
```python
from flask import Blueprint, request, jsonify, session
from src.core.decorators import login_required, role_required

xxx_bp = Blueprint('xxx', __name__)

@xxx_bp.route('/some-route')
@login_required
def some_handler():
    # 保持与原 app.py 中完全一致的逻辑
    ...
```

### 3.6 依赖更新

```txt
# 核心运行依赖
pandas>=2.0.3
numpy>=1.24.3
scikit-learn>=1.3.0
matplotlib>=3.7.2
seaborn>=0.12.2
Flask>=2.3.2
requests>=2.31.0
openpyxl>=3.1.2

# 深度学习（可选，CPU 版本，需单独安装）
# pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
# pip install torch_geometric torch_scatter torch_sparse torch_cluster torch_spline_conv

# 测试
pytest>=7.4.0
```

### 3.7 测试计划

| 测试文件 | 覆盖范围 |
|:---|:---|
| `tests/test_app.py` | create_app() 返回有效 app；所有路由已注册（`app.url_map`）；`/` 返回 200；未认证访问受保护路由返回 401/403 |
| `tests/test_auth.py` | 登录/登出、密码哈希（werkzeug）、角色检查、锁定机制 |
| `tests/test_data_processing.py` | 数据加载、清洗、特征工程 |
| `tests/test_classification.py` | 分类器训练、预测、特征重要性 |

### 3.8 README 更新

- 修正默认凭证：admin / Admin@123（teacher/student 需管理员创建）
- 更新 students.csv 格式说明（含 gender 列）
- 添加 PyTorch 安装说明（CPU 版本，需单独安装）
- 更新目录结构说明

### 3.9 .gitignore 更新

```
# 已有
paper/
.trae/

# 新增
__pycache__/
*.pyc
instance/
*.egg-info/
.pytest_cache/
.DS_Store
```

### 3.10 GitHub 推送

```bash
# 在 refactor 分支完成所有提交后
git checkout main
git merge refactor
git remote add origin <repo_url>  # 如尚未配置
git push -u origin main
```

## 4. 具体执行步骤（原子提交分组）

### Commit 1: 项目结构重组 + 导入路径修复
0. **创建 refactor 分支** — `git checkout -b refactor`
1. **迁移运行时数据** — 将 `auth/users.json`、`login_logs.json`、`failed_attempts.json` 复制到 `instance/auth/`
2. **更新导入路径** — `src/app.py` 和所有子模块中 `from auth.auth` → `from src.auth.auth`，`from llm_integration.xxx` → `from src.llm_integration.xxx`，以此类推
3. **删除根目录重复模块** — 10 个重复包目录
4. **删除冗余文件** — `src/templates/`、`group_dashboard.html`、`__pycache__/`
5. **补 `src/group_analysis/__init__.py`**
6. **验证** — `python -c "from src.data_processing.pipeline import run_data_pipeline"` 不报错
7. **提交** — `refactor: 统一项目结构，消除模块重复，修复导入路径`

### Commit 2: Flask Blueprint 拆分
8. **创建目录** — `src/blueprints/`、`src/core/`
9. **实现装饰器** — `src/core/decorators.py`
10. **创建 6 个 Blueprint** — `auth_bp.py`、`data_bp.py`、`warning_bp.py`、`analysis_bp.py`、`report_bp.py`、`llm_bp.py`
11. **重构 app.py** — 工厂模式，注册 Blueprint
12. **更新 run.py** — 调用 `create_app()`
13. **修复 make_response 导入** — 在 `data_bp.py` 中正确导入；移除 `app.py` 中未使用的 `import numpy as np`
14. **验证** — `python run.py` 启动无错误，`curl http://127.0.0.1:5000/` 返回 200
15. **提交** — `refactor: 拆分 Flask 单体应用为 Blueprint 架构`

### Commit 3: 安全加固
16. **密码哈希迁移** — `src/auth/auth.py` 改用 werkzeug，添加旧格式自动迁移
17. **AuthManager 路径更新** — 使用 `instance/auth/` 路径
18. **Secret Key** — 环境变量 + 固定开发 fallback
19. **RBAC 装饰器应用** — 管理员路由添加 `@role_required('admin')`，数据路由添加 `@login_required`
20. **清理 auth.py** — 修复 bare except，移除 unused import
21. **提交** — `security: 密码哈希加固、RBAC、认证保护`

### Commit 4: 前端修复 + 依赖更新
22. **Bootstrap Icons CSS** — 在 index.html `<head>` 中添加 CDN 链接
23. **admin-only 样式** — 添加 CSS 规则
24. **requirements.txt** — 更新依赖清单
25. **提交** — `fix: 修复前端图标、更新依赖清单`

### Commit 5: 测试 + 文档
26. **编写测试** — `test_app.py`、`test_auth.py`、`test_data_processing.py`、`test_classification.py`
27. **运行测试** — `pytest tests/ -v`
28. **更新 README.md**
29. **更新 .gitignore**
30. **提交** — `test+docs: 添加单元测试、更新文档`

### Commit 6: 合并 + GitHub 推送
31. **合并到 main** — `git checkout main && git merge refactor`
32. **创建 GitHub 仓库**（如需要）
33. **推送**

## 5. 成功标准

- `python run.py` 启动无错误
- `curl http://127.0.0.1:5000/` 返回 200
- 登录 `admin / Admin@123` 成功
- 未认证访问 `/get-warning-report` 返回 401
- 根目录无重复模块包（无 `association_rules/`、`classification/` 等）
- `pytest tests/` 全部通过
- `git push` 成功

## 6. 回滚方案

在 `refactor` 分支上工作，每个 Commit 是一个原子回滚点：
- Commit 1 失败 → `git reset --hard <main HEAD>`，重新检查导入路径
- Commit N 失败 → `git reset --hard <Commit N-1 hash>`，仅回退失败的变更
- 整体失败 → `git checkout main`，`refactor` 分支保留供后续分析
- 全部成功 → `git checkout main && git merge refactor`

## 7. 风险与对策

| 风险 | 对策 |
|:---|:---|
| Blueprint 拆分导致路由失效 | 保持所有 URL 路径完全不变 |
| 导入路径变更引发连锁错误 | 在 Commit 1 中逐步验证每个模块可导入 |
| 密码迁移导致用户无法登录 | 自动迁移旧格式 + 使用已知默认密码重新哈希 |
| 前端 JS 依赖特定 API 路径 | 保持所有 API 路径完全不变 |
| PyTorch 安装问题 | 作为可选依赖，提供独立安装说明 |
| AuthManager 路径变更丢失用户数据 | 先迁移数据到 instance/，确认后再删源文件 |

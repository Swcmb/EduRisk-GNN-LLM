"""应用冒烟测试：工厂、路由注册、认证保护"""
import pytest
from src.app import create_app


@pytest.fixture
def app():
    """创建测试用 Flask 应用"""
    app = create_app()
    app.config['TESTING'] = True
    yield app


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()


class TestAppFactory:
    """应用工厂测试"""

    def test_create_app_returns_valid_app(self, app):
        """create_app() 应返回有效的 Flask 应用"""
        assert app is not None
        assert app.config['TESTING'] is True

    def test_all_routes_registered(self, app):
        """应注册所有预期的路由"""
        rules = {rule.rule for rule in app.url_map.iter_rules()}
        expected_routes = [
            '/',
            '/upload',
            '/run-warning',
            '/get-warning-report',
            '/get-student-detail/<student_id>',
            '/send-warning/<student_id>',
            '/send-batch-warning',
            '/download-template/<template_name>',
            '/download-excel-template',
            '/get-template-info',
            '/get-group-analysis',
            '/get-recommendations/<student_id>',
            '/get-llm-recommendations/<student_id>',
            '/generate-report',
            '/get-llm-config',
            '/save-llm-config',
            '/generate-student-analysis/<student_id>',
            '/test-llm-connection',
            '/api/login',
            '/api/logout',
            '/api/check-auth',
            '/api/users',
            '/api/users/<username>',
            '/api/users/<username>/enable',
            '/api/users/<username>/disable',
            '/api/users/<username>/change-password',
            '/api/login-logs',
            '/api/anomalies',
            '/api/run-behavior-analysis',
            '/api/update-behavior-baseline',
            '/api/export-behavior-data',
            '/download-behavior-data',
            '/api/get-behavior-representation',
            '/api/get-alert-signals',
            '/api/get-system-status',
            '/api/get-grade-distribution',
            '/api/get-feature-importance',
            '/api/get-historical-data',
        ]
        for route in expected_routes:
            assert route in rules, f'路由 {route} 未注册'


class TestPublicRoutes:
    """公开路由测试"""

    def test_index_returns_200(self, client):
        """首页应返回 200"""
        response = client.get('/')
        assert response.status_code == 200

    def test_check_auth_returns_unauthenticated(self, client):
        """未登录时 check-auth 应返回 authenticated: False"""
        response = client.get('/api/check-auth')
        data = response.get_json()
        assert data['authenticated'] is False


class TestProtectedRoutes:
    """受保护路由测试"""

    def test_upload_requires_auth(self, client):
        """上传路由应要求认证"""
        response = client.post('/upload')
        assert response.status_code == 401

    def test_warning_report_requires_auth(self, client):
        """预警报告路由应要求认证"""
        response = client.get('/get-warning-report')
        assert response.status_code == 401

    def test_group_analysis_requires_auth(self, client):
        """群体分析路由应要求认证"""
        response = client.get('/get-group-analysis')
        assert response.status_code == 401

    def test_generate_report_requires_auth(self, client):
        """报告生成路由应要求认证"""
        response = client.post('/generate-report', json={'report_type': 'admin'})
        assert response.status_code == 401

    def test_llm_config_requires_auth(self, client):
        """LLM 配置路由应要求认证"""
        response = client.get('/get-llm-config')
        assert response.status_code == 401


class TestAuthFlow:
    """认证流程测试"""

    def test_login_success(self, client):
        """管理员登录应成功"""
        response = client.post('/api/login', json={
            'username': 'admin',
            'password': 'Admin@123'
        })
        data = response.get_json()
        assert data['status'] == 'success'
        assert data['user']['role'] == 'admin'

    def test_login_wrong_password(self, client):
        """错误密码应登录失败"""
        response = client.post('/api/login', json={
            'username': 'admin',
            'password': 'wrong'
        })
        data = response.get_json()
        assert data['status'] == 'error'

    def test_login_then_access_protected(self, client):
        """登录后应能访问受保护路由"""
        # 登录
        client.post('/api/login', json={
            'username': 'admin',
            'password': 'Admin@123'
        })
        # 访问受保护路由
        response = client.get('/get-llm-config')
        assert response.status_code == 200

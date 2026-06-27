"""认证模块测试"""
import pytest
import tempfile
import os
from src.auth.auth import AuthManager


@pytest.fixture
def auth_manager(tmp_path):
    """创建使用临时目录的 AuthManager"""
    return AuthManager(instance_path=str(tmp_path))


class TestPasswordHashing:
    """密码哈希测试"""

    def test_hash_password_returns_non_empty(self, auth_manager):
        """哈希后的密码不应为空"""
        hashed = auth_manager.hash_password('Test@1234')
        assert hashed
        assert len(hashed) > 20

    def test_verify_correct_password(self, auth_manager):
        """正确密码应验证通过"""
        hashed = auth_manager.hash_password('Test@1234')
        assert auth_manager.verify_password(hashed, 'Test@1234')

    def test_verify_wrong_password(self, auth_manager):
        """错误密码应验证失败"""
        hashed = auth_manager.hash_password('Test@1234')
        assert not auth_manager.verify_password(hashed, 'wrong')

    def test_different_passwords_different_hashes(self, auth_manager):
        """不同密码应产生不同哈希"""
        hash1 = auth_manager.hash_password('Test@1234')
        hash2 = auth_manager.hash_password('Test@5678')
        assert hash1 != hash2


class TestPasswordComplexity:
    """密码复杂度验证测试"""

    def test_valid_password(self, auth_manager):
        """符合要求的密码应通过"""
        valid, msg = auth_manager.validate_password_complexity('Admin@123')
        assert valid

    def test_too_short(self, auth_manager):
        """过短的密码应被拒绝"""
        valid, msg = auth_manager.validate_password_complexity('Aa@1')
        assert not valid

    def test_no_uppercase(self, auth_manager):
        """缺少大写字母应被拒绝"""
        valid, msg = auth_manager.validate_password_complexity('admin@123')
        assert not valid

    def test_no_special_char(self, auth_manager):
        """缺少特殊字符应被拒绝"""
        valid, msg = auth_manager.validate_password_complexity('Admin1234')
        assert not valid


class TestUserManagement:
    """用户管理测试"""

    def test_default_admin_exists(self, auth_manager):
        """默认管理员账户应存在"""
        assert 'admin' in auth_manager.users
        assert auth_manager.users['admin']['role'] == 'admin'

    def test_add_user(self, auth_manager):
        """应能添加新用户"""
        success, msg = auth_manager.add_user('testuser', 'Test@1234', 'user')
        assert success
        assert 'testuser' in auth_manager.users

    def test_add_duplicate_user(self, auth_manager):
        """不应添加重复用户名"""
        auth_manager.add_user('testuser', 'Test@1234')
        success, msg = auth_manager.add_user('testuser', 'Test@1234')
        assert not success

    def test_delete_user(self, auth_manager):
        """应能删除用户"""
        auth_manager.add_user('testuser', 'Test@1234')
        success, msg = auth_manager.delete_user('testuser')
        assert success
        assert 'testuser' not in auth_manager.users

    def test_cannot_delete_admin(self, auth_manager):
        """不应删除管理员账户"""
        success, msg = auth_manager.delete_user('admin')
        assert not success

    def test_login_success(self, auth_manager):
        """正确凭证应登录成功"""
        success, msg = auth_manager.login('admin', 'Admin@123')
        assert success

    def test_login_wrong_password(self, auth_manager):
        """错误密码应登录失败"""
        success, msg = auth_manager.login('admin', 'wrong')
        assert not success

    def test_account_lockout(self, auth_manager):
        """连续 5 次失败应锁定账户"""
        for _ in range(5):
            auth_manager.login('admin', 'wrong')
        success, msg = auth_manager.login('admin', 'Admin@123')
        assert not success
        assert '锁定' in msg

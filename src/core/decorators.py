"""认证与权限装饰器"""
from functools import wraps
from flask import session, jsonify


def login_required(f):
    """检查用户是否已登录"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('authenticated'):
            return jsonify({'status': 'error', 'message': '未授权访问'}), 401
        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    """检查用户角色权限"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not session.get('authenticated'):
                return jsonify({'status': 'error', 'message': '未授权访问'}), 401
            if session.get('role') not in roles:
                return jsonify({'status': 'error', 'message': '权限不足'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator

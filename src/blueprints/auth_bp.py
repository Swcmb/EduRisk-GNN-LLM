"""认证相关路由"""
from flask import Blueprint, request, jsonify, session
from src.auth.auth import AuthManager

auth_bp = Blueprint('auth', __name__, url_prefix='/api')

# 认证管理器实例（由 app 工厂注入）
_auth_manager = None


def init_auth_bp(instance_path):
    """初始化认证管理器，使用 instance 目录存储数据"""
    global _auth_manager
    _auth_manager = AuthManager(instance_path)


def _get_auth_manager():
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager()
    return _auth_manager


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'status': 'error', 'message': '用户名和密码不能为空'})

        ip_address = request.remote_addr
        user_agent = request.user_agent.string

        auth_mgr = _get_auth_manager()
        success, message = auth_mgr.login(username, password, None, ip_address, user_agent)

        if success:
            session['username'] = username
            session['authenticated'] = True
            user_info = auth_mgr.get_user_info(username)
            session['role'] = user_info['role']
            return jsonify({
                'status': 'success',
                'message': message,
                'user': {'username': username, 'role': user_info['role']}
            })
        else:
            return jsonify({'status': 'error', 'message': message})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'登录过程中出错: {str(e)}'})


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """用户登出"""
    try:
        session.clear()
        return jsonify({'status': 'success', 'message': '登出成功'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'登出过程中出错: {str(e)}'})


@auth_bp.route('/check-auth', methods=['GET'])
def check_auth():
    """检查认证状态"""
    if 'authenticated' in session and session['authenticated']:
        username = session['username']
        auth_mgr = _get_auth_manager()
        user_info = auth_mgr.get_user_info(username)
        return jsonify({
            'status': 'success',
            'authenticated': True,
            'user': {'username': username, 'role': user_info['role']}
        })
    else:
        return jsonify({'status': 'success', 'authenticated': False})


@auth_bp.route('/users', methods=['GET'])
def get_users():
    """获取所有用户"""
    try:
        if 'authenticated' not in session or not session['authenticated']:
            return jsonify({'status': 'error', 'message': '未授权访问'})
        auth_mgr = _get_auth_manager()
        users = auth_mgr.get_all_users()
        return jsonify({'status': 'success', 'users': users})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'获取用户列表失败: {str(e)}'})


@auth_bp.route('/users', methods=['POST'])
def add_user():
    """添加用户"""
    try:
        if 'authenticated' not in session or not session['authenticated']:
            return jsonify({'status': 'error', 'message': '未授权访问'})
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        role = data.get('role', 'user')
        if not username or not password:
            return jsonify({'status': 'error', 'message': '用户名和密码不能为空'})
        auth_mgr = _get_auth_manager()
        success, message = auth_mgr.add_user(username, password, role)
        return jsonify({'status': 'success' if success else 'error', 'message': message})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'添加用户失败: {str(e)}'})


@auth_bp.route('/users/<username>', methods=['DELETE'])
def delete_user(username):
    """删除用户"""
    try:
        if 'authenticated' not in session or not session['authenticated']:
            return jsonify({'status': 'error', 'message': '未授权访问'})
        auth_mgr = _get_auth_manager()
        success, message = auth_mgr.delete_user(username)
        return jsonify({'status': 'success' if success else 'error', 'message': message})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'删除用户失败: {str(e)}'})


@auth_bp.route('/users/<username>/enable', methods=['PUT'])
def enable_user(username):
    """启用用户"""
    try:
        if 'authenticated' not in session or not session['authenticated']:
            return jsonify({'status': 'error', 'message': '未授权访问'})
        auth_mgr = _get_auth_manager()
        success, message = auth_mgr.update_user(username, enabled=True)
        return jsonify({'status': 'success' if success else 'error', 'message': message})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'启用用户失败: {str(e)}'})


@auth_bp.route('/users/<username>/disable', methods=['PUT'])
def disable_user(username):
    """禁用用户"""
    try:
        if 'authenticated' not in session or not session['authenticated']:
            return jsonify({'status': 'error', 'message': '未授权访问'})
        auth_mgr = _get_auth_manager()
        success, message = auth_mgr.update_user(username, enabled=False)
        return jsonify({'status': 'success' if success else 'error', 'message': message})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'禁用用户失败: {str(e)}'})


@auth_bp.route('/users/<username>/change-password', methods=['POST'])
def change_password(username):
    """修改密码"""
    try:
        if 'authenticated' not in session or not session['authenticated']:
            return jsonify({'status': 'error', 'message': '未授权访问'})
        if session['username'] != username:
            return jsonify({'status': 'error', 'message': '只能修改自己的密码'})
        data = request.get_json()
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        if not old_password or not new_password:
            return jsonify({'status': 'error', 'message': '旧密码和新密码不能为空'})
        auth_mgr = _get_auth_manager()
        success, message = auth_mgr.change_password(username, old_password, new_password)
        return jsonify({'status': 'success' if success else 'error', 'message': message})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'修改密码失败: {str(e)}'})


@auth_bp.route('/login-logs', methods=['GET'])
def get_login_logs():
    """获取登录日志"""
    try:
        if 'authenticated' not in session or not session['authenticated']:
            return jsonify({'status': 'error', 'message': '未授权访问'})
        import json
        import os
        log_file = os.path.join(_get_auth_manager().data_dir, 'login_logs.json')
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            return jsonify({'status': 'success', 'logs': logs})
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'读取日志失败: {str(e)}'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'获取登录日志失败: {str(e)}'})


@auth_bp.route('/anomalies', methods=['GET'])
def get_anomalies():
    """获取登录异常"""
    try:
        if 'authenticated' not in session or not session['authenticated']:
            return jsonify({'status': 'error', 'message': '未授权访问'})
        auth_mgr = _get_auth_manager()
        anomalies = auth_mgr.detect_login_anomalies()
        return jsonify({'status': 'success', 'anomalies': anomalies})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'检测异常失败: {str(e)}'})

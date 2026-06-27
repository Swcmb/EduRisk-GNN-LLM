import re
import hashlib
import time
import json
import os
from datetime import datetime, timedelta
import hmac
import base64

class AuthManager:
    def __init__(self, instance_path=None):
        # 使用 instance 目录存储运行时数据，避免污染源码目录
        if instance_path:
            self.data_dir = os.path.join(instance_path, 'auth')
        else:
            self.data_dir = 'auth'
        self.users_file = os.path.join(self.data_dir, 'users.json')
        self.login_logs_file = os.path.join(self.data_dir, 'login_logs.json')
        self.failed_attempts_file = os.path.join(self.data_dir, 'failed_attempts.json')
        self._ensure_files_exist()
        self._load_data()
    
    def _ensure_files_exist(self):
        """确保必要的文件存在"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 创建默认用户
        if not os.path.exists(self.users_file):
            default_user = {
                'admin': {
                    'password_hash': self.hash_password('Admin@123'),
                    'role': 'admin',
                    'enabled': True,
                    'created_at': datetime.now().isoformat(),
                    'last_login': None,
                    'totp_secret': self.generate_totp_secret(),
                    'totp_enabled': False
                }
            }
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(default_user, f, indent=2)
        
        # 创建登录日志文件
        if not os.path.exists(self.login_logs_file):
            with open(self.login_logs_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
        
        # 创建失败尝试记录文件
        if not os.path.exists(self.failed_attempts_file):
            with open(self.failed_attempts_file, 'w', encoding='utf-8') as f:
                json.dump({}, f)
    
    def _load_data(self):
        """加载数据"""
        with open(self.users_file, 'r', encoding='utf-8') as f:
            self.users = json.load(f)
        
        with open(self.failed_attempts_file, 'r', encoding='utf-8') as f:
            self.failed_attempts = json.load(f)
    
    def _save_data(self):
        """保存数据"""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, indent=2)
        
        with open(self.failed_attempts_file, 'w', encoding='utf-8') as f:
            json.dump(self.failed_attempts, f, indent=2)
    
    def hash_password(self, password):
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def validate_password_complexity(self, password):
        """验证密码复杂度：至少8位，包含大小写字母、数字和特殊符号"""
        if len(password) < 8:
            return False, "密码长度至少为8位"
        
        if not re.search(r'[a-z]', password):
            return False, "密码必须包含小写字母"
        
        if not re.search(r'[A-Z]', password):
            return False, "密码必须包含大写字母"
        
        if not re.search(r'[0-9]', password):
            return False, "密码必须包含数字"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "密码必须包含特殊符号"
        
        return True, "密码符合复杂度要求"
    
    def check_failed_attempts(self, username):
        """检查登录失败次数限制"""
        if username not in self.failed_attempts:
            return True, ""
        
        attempts = self.failed_attempts[username]
        current_time = time.time()
        
        # 检查是否被锁定
        if 'locked_until' in attempts and attempts['locked_until'] > current_time:
            remaining_time = int(attempts['locked_until'] - current_time)
            minutes = remaining_time // 60
            seconds = remaining_time % 60
            return False, f"账户已锁定，请在 {minutes}分{seconds}秒后重试"
        
        # 检查失败次数
        if attempts.get('count', 0) >= 5:
            # 锁定30分钟
            self.failed_attempts[username]['locked_until'] = current_time + 30 * 60
            self._save_data()
            return False, "连续5次登录失败，账户已锁定30分钟"
        
        return True, ""
    
    def generate_totp_secret(self):
        """生成TOTP密钥"""
        import secrets
        return secrets.token_hex(16)
    
    def get_totp_qr_url(self, username):
        """获取TOTP二维码URL"""
        if username not in self.users:
            return None
        
        secret = self.users[username]['totp_secret']
        # 使用base32编码
        secret_base32 = base64.b32encode(secret.encode()).decode('utf-8').rstrip('=')
        issuer = "AcademicWarningSystem"
        qr_url = f"otpauth://totp/{issuer}:{username}?secret={secret_base32}&issuer={issuer}"
        return qr_url
    
    def verify_totp_code(self, username, code):
        """验证TOTP验证码"""
        if username not in self.users:
            return False
        
        secret = self.users[username]['totp_secret']
        
        try:
            # 使用当前时间和前后各30秒的窗口验证
            for offset in [-1, 0, 1]:
                if self._verify_totp_code_at_time(secret, code, offset):
                    return True
            return False
        except:
            return False
    
    def _verify_totp_code_at_time(self, secret, code, offset=0):
        """在特定时间偏移下验证TOTP码"""
        timestamp = int(time.time() / 30) + offset
        
        # 将密钥转换为bytes
        secret_bytes = secret.encode()
        
        # 将时间戳转换为bytes
        timestamp_bytes = timestamp.to_bytes(8, byteorder='big')
        
        # 使用HMAC-SHA1计算
        hmac_hash = hmac.new(secret_bytes, timestamp_bytes, hashlib.sha1).digest()
        
        # 取最后4位作为偏移量
        offset = hmac_hash[-1] & 0x0F
        
        # 取4字节作为验证码
        code_bytes = hmac_hash[offset:offset+4]
        code_int = int.from_bytes(code_bytes, byteorder='big') & 0x7FFFFFFF
        
        # 转换为6位数字
        totp_code = str(code_int % 1000000).zfill(6)
        
        return totp_code == code
    
    def log_login_attempt(self, username, success, ip_address=None, user_agent=None):
        """记录登录尝试"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'username': username,
            'success': success,
            'ip_address': ip_address,
            'user_agent': user_agent
        }
        
        try:
            with open(self.login_logs_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            logs.append(log_entry)
            
            # 只保留最近1000条日志
            if len(logs) > 1000:
                logs = logs[-1000:]
            
            with open(self.login_logs_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2)
        except:
            pass
    
    def detect_login_anomalies(self):
        """检测登录异常"""
        try:
            with open(self.login_logs_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            anomalies = []
            
            # 分析最近24小时的登录记录
            twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
            
            recent_logs = [
                log for log in logs 
                if datetime.fromisoformat(log['timestamp']) >= twenty_four_hours_ago
            ]
            
            # 统计每个IP的失败次数
            ip_failure_counts = {}
            for log in recent_logs:
                if not log['success'] and log['ip_address']:
                    ip = log['ip_address']
                    ip_failure_counts[ip] = ip_failure_counts.get(ip, 0) + 1
            
            # 检测异常IP（失败次数超过10次）
            for ip, count in ip_failure_counts.items():
                if count > 10:
                    anomalies.append({
                        'type': 'ip_failure_threshold',
                        'ip_address': ip,
                        'failure_count': count,
                        'message': f"IP地址 {ip} 在24小时内登录失败 {count} 次，可能存在暴力攻击"
                    })
            
            # 检测短时间内的多次失败
            for username in self.users:
                user_logs = [log for log in recent_logs if log['username'] == username]
                failure_logs = [log for log in user_logs if not log['success']]
                
                if len(failure_logs) >= 5:
                    # 检查时间间隔
                    first_failure = datetime.fromisoformat(failure_logs[0]['timestamp'])
                    last_failure = datetime.fromisoformat(failure_logs[-1]['timestamp'])
                    time_diff = (last_failure - first_failure).total_seconds()
                    
                    if time_diff < 300:  # 5分钟内
                        anomalies.append({
                            'type': 'rapid_failures',
                            'username': username,
                            'failure_count': len(failure_logs),
                            'time_window': time_diff,
                            'message': f"用户 {username} 在 {time_diff:.1f} 秒内连续失败 {len(failure_logs)} 次"
                        })
            
            return anomalies
            
        except:
            return []
    
    def login(self, username, password, totp_code=None, ip_address=None, user_agent=None):
        """用户登录"""
        # 检查用户是否存在
        if username not in self.users:
            self.log_login_attempt(username, False, ip_address, user_agent)
            return False, "用户名或密码错误"
        
        # 检查账户是否启用
        if not self.users[username]['enabled']:
            self.log_login_attempt(username, False, ip_address, user_agent)
            return False, "账户已被禁用"
        
        # 检查失败尝试限制
        allowed, message = self.check_failed_attempts(username)
        if not allowed:
            self.log_login_attempt(username, False, ip_address, user_agent)
            return False, message
        
        # 验证密码
        if self.users[username]['password_hash'] != self.hash_password(password):
            # 记录失败尝试
            if username not in self.failed_attempts:
                self.failed_attempts[username] = {'count': 0}
            self.failed_attempts[username]['count'] += 1
            self._save_data()
            
            self.log_login_attempt(username, False, ip_address, user_agent)
            return False, "用户名或密码错误"
        
        # 如果启用了2FA，验证TOTP码
        if self.users[username]['totp_enabled']:
            if not totp_code:
                self.log_login_attempt(username, False, ip_address, user_agent)
                return False, "请输入验证码"
            
            if not self.verify_totp_code(username, totp_code):
                self.log_login_attempt(username, False, ip_address, user_agent)
                return False, "验证码错误"
        
        # 登录成功，重置失败尝试
        if username in self.failed_attempts:
            del self.failed_attempts[username]
        
        # 更新最后登录时间
        self.users[username]['last_login'] = datetime.now().isoformat()
        self._save_data()
        
        self.log_login_attempt(username, True, ip_address, user_agent)
        
        return True, "登录成功"
    
    def add_user(self, username, password, role='user'):
        """添加用户"""
        if username in self.users:
            return False, "用户名已存在"
        
        # 验证密码复杂度
        valid, message = self.validate_password_complexity(password)
        if not valid:
            return False, message
        
        # 创建用户
        self.users[username] = {
            'password_hash': self.hash_password(password),
            'role': role,
            'enabled': True,
            'created_at': datetime.now().isoformat(),
            'last_login': None,
            'totp_secret': self.generate_totp_secret(),
            'totp_enabled': False
        }
        self._save_data()
        
        return True, "用户创建成功"
    
    def change_password(self, username, old_password, new_password):
        """修改密码"""
        if username not in self.users:
            return False, "用户不存在"
        
        # 验证旧密码
        if self.users[username]['password_hash'] != self.hash_password(old_password):
            return False, "旧密码错误"
        
        # 验证新密码复杂度
        valid, message = self.validate_password_complexity(new_password)
        if not valid:
            return False, message
        
        # 更新密码
        self.users[username]['password_hash'] = self.hash_password(new_password)
        self._save_data()
        
        return True, "密码修改成功"
    
    def enable_totp(self, username, totp_code):
        """启用双因素认证"""
        if username not in self.users:
            return False, "用户不存在"
        
        # 验证TOTP码
        if not self.verify_totp_code(username, totp_code):
            return False, "验证码错误"
        
        # 启用2FA
        self.users[username]['totp_enabled'] = True
        self._save_data()
        
        return True, "双因素认证已启用"
    
    def disable_totp(self, username, password):
        """禁用双因素认证"""
        if username not in self.users:
            return False, "用户不存在"
        
        # 验证密码
        if self.users[username]['password_hash'] != self.hash_password(password):
            return False, "密码错误"
        
        # 禁用2FA
        self.users[username]['totp_enabled'] = False
        self._save_data()
        
        return True, "双因素认证已禁用"
    
    def get_user_info(self, username):
        """获取用户信息"""
        if username not in self.users:
            return None
        
        user = self.users[username].copy()
        # 不返回密码哈希和TOTP密钥
        user.pop('password_hash', None)
        user.pop('totp_secret', None)
        return user
    
    def get_all_users(self):
        """获取所有用户信息"""
        users_info = []
        for username, user_data in self.users.items():
            user_info = user_data.copy()
            user_info.pop('password_hash', None)
            user_info.pop('totp_secret', None)
            user_info['username'] = username
            users_info.append(user_info)
        return users_info
    
    def update_user(self, username, enabled=None, role=None):
        """更新用户信息"""
        if username not in self.users:
            return False, "用户不存在"
        
        if enabled is not None:
            self.users[username]['enabled'] = enabled
        
        if role is not None:
            self.users[username]['role'] = role
        
        self._save_data()
        return True, "用户信息已更新"
    
    def delete_user(self, username):
        """删除用户"""
        if username not in self.users:
            return False, "用户不存在"
        
        # 不允许删除admin用户
        if username == 'admin':
            return False, "不能删除管理员账户"
        
        del self.users[username]
        if username in self.failed_attempts:
            del self.failed_attempts[username]
        self._save_data()
        
        return True, "用户已删除"

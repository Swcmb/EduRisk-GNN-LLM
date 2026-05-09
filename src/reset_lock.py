#!/usr/bin/env python3
"""
重置账户锁定状态
"""

import json
import os

def reset_failed_attempts():
    """重置失败尝试记录"""
    failed_attempts_file = 'auth/failed_attempts.json'
    
    if os.path.exists(failed_attempts_file):
        # 清空失败尝试记录
        with open(failed_attempts_file, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=2)
        print("✓ 已重置所有账户的锁定状态")
    else:
        print("✗ 失败尝试记录文件不存在")

if __name__ == '__main__':
    reset_failed_attempts()

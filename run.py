#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
启动脚本 - 用于运行学生学业预警系统
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入并运行Flask应用
from src.app import app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
"""Flask 应用工厂"""
import os
from flask import Flask


def create_app():
    """创建并配置 Flask 应用"""
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    app = Flask(__name__, template_folder=os.path.join(basedir, 'templates'))

    # 配置
    app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-for-local-development')
    app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'data')
    app.config['INSTANCE_PATH'] = os.path.join(basedir, 'instance')

    # 确保上传文件夹存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # 注册蓝图
    from src.blueprints.auth_bp import auth_bp, init_auth_bp
    from src.blueprints.data_bp import data_bp
    from src.blueprints.warning_bp import warning_bp
    from src.blueprints.analysis_bp import analysis_bp
    from src.blueprints.report_bp import report_bp
    from src.blueprints.llm_bp import llm_bp

    # 初始化认证管理器（使用 instance 目录存储运行时数据）
    init_auth_bp(app.config['INSTANCE_PATH'])

    app.register_blueprint(auth_bp)
    app.register_blueprint(data_bp)
    app.register_blueprint(warning_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(llm_bp)

    return app

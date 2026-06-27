"""LLM 配置与调用路由"""
import os
import pandas as pd
from flask import Blueprint, request, jsonify
from src.llm_integration.openai_client import llm_client
from src.core.decorators import login_required

llm_bp = Blueprint('llm', __name__)


@llm_bp.route('/get-llm-config')
@login_required
def get_llm_config():
    """获取LLM配置"""
    try:
        config = llm_client.get_config()
        return jsonify({'status': 'success', 'config': config})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'获取LLM配置失败: {str(e)}'})


@llm_bp.route('/save-llm-config', methods=['POST'])
@login_required
def save_llm_config():
    """保存LLM配置"""
    try:
        config = request.get_json()
        llm_client.save_config(config)
        return jsonify({'status': 'success', 'message': 'LLM配置已保存'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'保存LLM配置失败: {str(e)}'})


@llm_bp.route('/generate-student-analysis/<student_id>', methods=['POST'])
@login_required
def generate_student_analysis(student_id):
    """使用LLM生成学生分析建议"""
    try:
        report_path = 'reports/academic_warning_report.csv'
        if os.path.exists(report_path):
            report = pd.read_csv(report_path)
            student = report[report['学生ID'] == student_id].to_dict('records')
            if student:
                student_data = student[0]
                analysis = llm_client.generate_student_analysis(student_data)
                return jsonify({'status': 'success', 'analysis': analysis})
            else:
                return jsonify({'status': 'error', 'message': '学生不存在'})
        else:
            return jsonify({'status': 'error', 'message': '预警报告不存在'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'生成分析建议失败: {str(e)}'})


@llm_bp.route('/test-llm-connection', methods=['POST'])
@login_required
def test_llm_connection():
    """测试LLM连接"""
    try:
        test_data = {
            '学生ID': 'TEST001',
            '姓名': '测试学生',
            '风险等级': '低风险',
            '风险概率': 0.1,
            '风险因素': '无',
            '行为模式': '正常'
        }
        analysis = llm_client.generate_student_analysis(test_data)
        return jsonify({'status': 'success', 'message': 'LLM连接测试成功', 'analysis': analysis})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'LLM连接测试失败: {str(e)}'})

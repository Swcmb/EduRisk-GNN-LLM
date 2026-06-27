"""报告生成路由"""
import os
import subprocess
from flask import Blueprint, request, jsonify
from src.core.decorators import login_required

report_bp = Blueprint('report', __name__)


@report_bp.route('/generate-report', methods=['POST'])
@login_required
def generate_report_api():
    """生成报告"""
    try:
        data = request.get_json()
        report_type = data.get('report_type', 'admin')
        student_id = data.get('student_id', '')

        if report_type == 'student' and student_id:
            result = subprocess.run(
                ['python', '-c', f'from src.report_generator import generate_student_report; print(generate_student_report("{student_id}"))'],
                capture_output=True, text=True, cwd=os.getcwd()
            )
        elif report_type == 'teacher':
            result = subprocess.run(
                ['python', '-c', 'from src.report_generator import generate_teacher_report; print(generate_teacher_report())'],
                capture_output=True, text=True, cwd=os.getcwd()
            )
        else:
            result = subprocess.run(
                ['python', '-c', 'from src.report_generator import generate_admin_report; print(generate_admin_report())'],
                capture_output=True, text=True, cwd=os.getcwd()
            )

        if result.returncode == 0:
            report_content = result.stdout.strip()
            return jsonify({'status': 'success', 'report': report_content})
        else:
            return jsonify({'status': 'error', 'message': f'生成报告失败: {result.stderr}'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'生成报告失败: {str(e)}'})

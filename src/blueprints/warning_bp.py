"""预警相关路由"""
import os
import subprocess
import pandas as pd
from flask import Blueprint, request, jsonify
from src.core.decorators import login_required

warning_bp = Blueprint('warning', __name__)


@warning_bp.route('/run-warning', methods=['POST'])
@login_required
def run_warning():
    """运行预警系统"""
    try:
        result = subprocess.run(['python', '-m', 'src.academic_warning'],
                              capture_output=True, text=True, cwd=os.getcwd())

        if result.returncode == 0:
            report_path = 'reports/academic_warning_report.csv'
            if os.path.exists(report_path):
                report = pd.read_csv(report_path)
                report_data = report.to_dict('records')
                return jsonify({
                    'status': 'success',
                    'message': '预警系统运行完成',
                    'report': report_data
                })
            else:
                return jsonify({'status': 'error', 'message': '预警报告生成失败'})
        else:
            return jsonify({'status': 'error', 'message': f'预警系统运行失败: {result.stderr}'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'运行预警系统时出错: {str(e)}'})


@warning_bp.route('/get-warning-report')
@login_required
def get_warning_report():
    """获取预警报告"""
    try:
        report_path = 'reports/academic_warning_report.csv'
        if os.path.exists(report_path):
            report = pd.read_csv(report_path)
            report_data = report.to_dict('records')
            return jsonify({'status': 'success', 'report': report_data})
        else:
            return jsonify({'status': 'error', 'message': '预警报告不存在'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'获取预警报告失败: {str(e)}'})


@warning_bp.route('/get-student-detail/<student_id>')
@login_required
def get_student_detail(student_id):
    """获取学生详情"""
    try:
        report_path = 'reports/academic_warning_report.csv'
        if os.path.exists(report_path):
            report = pd.read_csv(report_path)
            student = report[report['学生ID'] == student_id].to_dict('records')
            if student:
                return jsonify({'status': 'success', 'student': student[0]})
            else:
                return jsonify({'status': 'error', 'message': '学生不存在'})
        else:
            return jsonify({'status': 'error', 'message': '预警报告不存在'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'获取学生详情失败: {str(e)}'})


@warning_bp.route('/send-warning/<student_id>', methods=['POST'])
@login_required
def send_warning_notification(student_id):
    """发送单个学生预警通知"""
    try:
        report_path = 'reports/academic_warning_report.csv'
        if os.path.exists(report_path):
            report = pd.read_csv(report_path)
            student = report[report['学生ID'] == student_id].to_dict('records')

            if student:
                student_info = student[0]
                warning_log = {
                    'timestamp': pd.Timestamp.now(),
                    'student_id': student_id,
                    'student_name': student_info.get('姓名', '未知'),
                    'risk_level': student_info.get('风险等级', '未知'),
                    'risk_factors': student_info.get('风险因素', '无'),
                    'notification_type': 'individual',
                    'sent_to': 'student_and_teacher'
                }

                log_file = 'reports/warning_notifications.log'
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(f"{warning_log['timestamp']} - {warning_log['notification_type']} - "
                            f"学生ID: {warning_log['student_id']}, 姓名: {warning_log['student_name']}, "
                            f"风险等级: {warning_log['risk_level']}, 风险因素: {warning_log['risk_factors']}\n")

                return jsonify({
                    'status': 'success',
                    'message': f'已向学生 {student_id} 发送预警通知，教师端也已收到通知',
                    'student_info': student_info
                })
            else:
                return jsonify({'status': 'error', 'message': '学生不存在'})
        else:
            return jsonify({'status': 'error', 'message': '预警报告不存在'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'发送预警失败: {str(e)}'})


@warning_bp.route('/send-batch-warning', methods=['POST'])
@login_required
def send_batch_warning_notification():
    """批量发送预警通知"""
    try:
        data = request.get_json()
        student_ids = data.get('student_ids', [])

        if not student_ids:
            return jsonify({'status': 'error', 'message': '请至少选择一个学生'})

        report_path = 'reports/academic_warning_report.csv'
        if os.path.exists(report_path):
            report = pd.read_csv(report_path)
            success_count = 0
            failed_count = 0
            log_file = 'reports/warning_notifications.log'

            for student_id in student_ids:
                student = report[report['学生ID'] == student_id].to_dict('records')
                if student:
                    student_info = student[0]
                    warning_log = {
                        'timestamp': pd.Timestamp.now(),
                        'student_id': student_id,
                        'student_name': student_info.get('姓名', '未知'),
                        'risk_level': student_info.get('风险等级', '未知'),
                        'risk_factors': student_info.get('风险因素', '无'),
                        'notification_type': 'batch',
                        'sent_to': 'student_and_teacher'
                    }

                    with open(log_file, 'a', encoding='utf-8') as f:
                        f.write(f"{warning_log['timestamp']} - {warning_log['notification_type']} - "
                                f"学生ID: {warning_log['student_id']}, 姓名: {warning_log['student_name']}, "
                                f"风险等级: {warning_log['risk_level']}, 风险因素: {warning_log['risk_factors']}\n")

                    success_count += 1
                else:
                    failed_count += 1

            return jsonify({
                'status': 'success',
                'message': f'批量预警发送完成，成功: {success_count}, 失败: {failed_count}',
                'details': {
                    'success_count': success_count,
                    'failed_count': failed_count,
                    'total': len(student_ids)
                }
            })
        else:
            return jsonify({'status': 'error', 'message': '预警报告不存在'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'批量预警发送失败: {str(e)}'})

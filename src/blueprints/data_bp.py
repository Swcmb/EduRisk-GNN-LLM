"""数据管理路由：首页、文件上传、模板下载"""
import os
import io
import pandas as pd
from flask import Blueprint, request, jsonify, render_template, send_file, make_response
from src.core.decorators import login_required

data_bp = Blueprint('data', __name__)

ALLOWED_EXTENSIONS = {'csv'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@data_bp.route('/')
def index():
    return render_template('index.html')


@data_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    """上传CSV数据文件"""
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': '没有文件被上传'})

    files = request.files.getlist('file')
    filenames = []
    upload_folder = os.path.join(os.getcwd(), 'data')

    for file in files:
        if file and allowed_file(file.filename):
            filename = file.filename
            file.save(os.path.join(upload_folder, filename))
            filenames.append(filename)

    if not filenames:
        return jsonify({'status': 'error', 'message': '没有有效的文件被上传'})

    return jsonify({'status': 'success', 'message': '文件上传成功', 'files': filenames})


@data_bp.route('/download-template/<template_name>')
@login_required
def download_template(template_name):
    """下载CSV模板"""
    try:
        if template_name == 'students':
            data = {
                'student_id': ['S001', 'S002'],
                'name': ['张三', '李四'],
                'age': [19, 20],
                'major': ['计算机科学与技术', '电子工程']
            }
            filename = 'students_template.csv'
        elif template_name == 'grades':
            data = {
                'student_id': ['S001', 'S001', 'S002'],
                'course': ['高等数学', '大学物理', '高等数学'],
                'score': [85, 78, 92],
                'semester': ['第一学期', '第一学期', '第一学期'],
                'year': [2024, 2024, 2024]
            }
            filename = 'grades_template.csv'
        elif template_name == 'attendance':
            data = {
                'student_id': ['S001', 'S001', 'S002'],
                'date': ['2024-03-01', '2024-03-02', '2024-03-01'],
                'course': ['高等数学', '大学物理', '高等数学'],
                'status': ['present', 'late', 'present']
            }
            filename = 'attendance_template.csv'
        elif template_name == 'courses':
            data = {
                'student_id': ['S001', 'S001', 'S002'],
                'course': ['高等数学', '大学物理', '高等数学'],
                'semester': ['第一学期', '第一学期', '第一学期'],
                'year': [2024, 2024, 2024]
            }
            filename = 'courses_template.csv'
        else:
            return jsonify({'status': 'error', 'message': '模板不存在'})

        df = pd.DataFrame(data)
        output = io.StringIO()
        df.to_csv(output, index=False, encoding='utf-8-sig')
        output.seek(0)

        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'下载模板失败: {str(e)}'})


@data_bp.route('/download-excel-template')
@login_required
def download_excel_template():
    """下载Excel格式的多sheet数据上传模板"""
    try:
        from io import BytesIO

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # 学生信息模板
            student_data = {
                'student_id': ['20230001', '20230002'],
                'name': ['张三', '李四'],
                'age': [20, 21],
                'gender': ['男', '女'],
                'major': ['计算机科学', '电子工程']
            }
            pd.DataFrame(student_data).to_excel(writer, sheet_name='学生信息', index=False)

            # 成绩数据模板
            grade_data = {
                'student_id': ['20230001', '20230001'],
                'course': ['高等数学', '大学物理'],
                'score': [85, 78],
                'semester': ['2023-2024-1', '2023-2024-1'],
                'year': [2023, 2023]
            }
            pd.DataFrame(grade_data).to_excel(writer, sheet_name='成绩数据', index=False)

            # 出勤记录模板
            attendance_data = {
                'student_id': ['20230001', '20230002'],
                'date': ['2023-09-01', '2023-09-01'],
                'course': ['高等数学', '大学物理'],
                'status': ['出勤', '缺勤']
            }
            pd.DataFrame(attendance_data).to_excel(writer, sheet_name='出勤记录', index=False)

            # 选课行为模板
            course_data = {
                'student_id': ['20230001', '20230002'],
                'course': ['高等数学', '大学物理'],
                'semester': ['2023-2024-1', '2023-2024-1'],
                'year': [2023, 2023]
            }
            pd.DataFrame(course_data).to_excel(writer, sheet_name='选课行为', index=False)

        output.seek(0)

        response = make_response(output.read())
        response.headers['Content-Disposition'] = 'attachment; filename=学生数据导入模板.xlsx'
        response.headers['Content-type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

        return response
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'下载Excel模板失败: {str(e)}'})


@data_bp.route('/get-template-info')
@login_required
def template_info():
    """获取模板信息"""
    try:
        info = {
            'templates': [
                {'name': 'students', 'description': '学生基本信息', 'fields': ['student_id', 'name', 'age', 'gender', 'major']},
                {'name': 'grades', 'description': '学生成绩数据', 'fields': ['student_id', 'course', 'score', 'semester', 'year']},
                {'name': 'attendance', 'description': '学生出勤记录', 'fields': ['student_id', 'date', 'course', 'status']},
                {'name': 'courses', 'description': '学生选课行为', 'fields': ['student_id', 'course', 'semester', 'year']}
            ]
        }
        return jsonify({'status': 'success', 'info': info})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'获取模板信息失败: {str(e)}'})

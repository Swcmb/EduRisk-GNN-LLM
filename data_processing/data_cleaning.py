import pandas as pd
import numpy as np

def clean_student_data(data):
    """
    清洗学生数据
    
    Args:
        data (dict): 包含不同类型数据的字典
    
    Returns:
        dict: 清洗后的数据
    """
    cleaned_data = {}
    
    # 清洗成绩数据
    if 'grades' in data:
        grades = data['grades'].copy()
        # 标准化列名
        grades.columns = grades.columns.str.lower()
        # 根据实际列名处理缺失值
        required_columns = ['student_id', 'score']
        if 'course' in grades.columns:
            required_columns.append('course')
        elif 'course_id' in grades.columns:
            required_columns.append('course_id')
        grades = grades.dropna(subset=required_columns)
        # 处理异常值
        grades = grades[(grades['score'] >= 0) & (grades['score'] <= 100)]
        cleaned_data['grades'] = grades
    
    # 清洗出勤记录
    if 'attendance' in data:
        attendance = data['attendance'].copy()
        # 标准化列名
        attendance.columns = attendance.columns.str.lower()
        # 根据实际列名处理缺失值
        required_columns = ['student_id', 'date', 'status']
        if 'course' in attendance.columns:
            required_columns.append('course')
        elif 'course_id' in attendance.columns:
            required_columns.append('course_id')
        attendance = attendance.dropna(subset=required_columns)
        # 标准化状态值
        attendance['status'] = attendance['status'].str.strip().str.lower()
        # 过滤无效状态
        valid_statuses = ['present', 'absent', 'late', 'excused']
        attendance = attendance[attendance['status'].isin(valid_statuses)]
        cleaned_data['attendance'] = attendance

    # 清洗选课行为
    if 'courses' in data:
        courses = data['courses'].copy()
        # 标准化列名
        courses.columns = courses.columns.str.lower()
        # 根据实际列名处理缺失值
        required_columns = ['student_id', 'semester', 'year']
        if 'course' in courses.columns:
            required_columns.append('course')
        elif 'course_id' in courses.columns:
            required_columns.append('course_id')
        courses = courses.dropna(subset=required_columns)
        cleaned_data['courses'] = courses
    
    # 清洗学生基本信息
    if 'students' in data:
        students = data['students'].copy()
        # 处理缺失值
        students = students.dropna(subset=['student_id', 'name'])
        # 标准化列名
        students.columns = students.columns.str.lower()
        cleaned_data['students'] = students
    
    return cleaned_data
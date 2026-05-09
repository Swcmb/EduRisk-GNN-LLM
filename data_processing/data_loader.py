import pandas as pd
import os

def load_data(data_dir='data'):
    """
    加载学生数据
    
    Args:
        data_dir (str): 数据目录路径
    
    Returns:
        dict: 包含不同类型数据的字典
    """
    data = {}
    
    # 加载成绩数据
    grades_file = os.path.join(data_dir, 'grades.csv')
    if os.path.exists(grades_file):
        data['grades'] = pd.read_csv(grades_file, encoding='utf-8-sig')
    
    # 加载出勤记录
    attendance_file = os.path.join(data_dir, 'attendance.csv')
    if os.path.exists(attendance_file):
        data['attendance'] = pd.read_csv(attendance_file, encoding='utf-8-sig')
    
    # 加载选课行为
    courses_file = os.path.join(data_dir, 'courses.csv')
    if os.path.exists(courses_file):
        data['courses'] = pd.read_csv(courses_file, encoding='utf-8-sig')
    
    # 加载学生基本信息
    students_file = os.path.join(data_dir, 'students.csv')
    if os.path.exists(students_file):
        data['students'] = pd.read_csv(students_file, encoding='utf-8-sig')
    
    return data
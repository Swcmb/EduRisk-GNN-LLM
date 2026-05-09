import pandas as pd
import numpy as np

def load_and_transform_data(data_dir=r'd:\CourseDesign2026\data'):
    """
    加载并转换数据为交易格式
    
    参数:
    - data_dir: 数据目录路径
    
    返回:
    - transactions: 交易数据列表
    - student_courses: 学生课程映射
    """
    # 读取数据
    grades_df = pd.read_csv(f'{data_dir}\\grades.csv')
    
    # 预处理成绩，将成绩转换为表现等级
    def grade_to_performance(score):
        if score >= 90:
            return '优秀'
        elif score >= 80:
            return '良好'
        elif score >= 70:
            return '中等'
        elif score >= 60:
            return '及格'
        else:
            return '不及格'
    
    grades_df['performance'] = grades_df['score'].apply(grade_to_performance)
    
    # 按学生分组，创建交易数据
    student_groups = grades_df.groupby('student_id')
    transactions = []
    student_courses = {}
    
    for student_id, group in student_groups:
        # 收集学生的课程和表现
        items = []
        courses = []
        
        for _, row in group.iterrows():
            # 根据实际列名获取课程名称
            if 'course_name' in row:
                course_name = row['course_name']
            elif 'course' in row:
                course_name = row['course']
            else:
                course_name = f'课程_{_}'
            performance = row['performance']
            items.append(f'课程:{course_name}')
            items.append(f'表现:{performance}')
            courses.append(course_name)
        
        transactions.append(items)
        student_courses[student_id] = courses
    
    return transactions, student_courses

def create_course_performance_transactions(data_dir=r'd:\CourseDesign2026\data'):
    """
    创建课程和学业表现的交易数据
    
    参数:
    - data_dir: 数据目录路径
    
    返回:
    - transactions: 交易数据列表
    """
    # 读取成绩数据
    grades_df = pd.read_csv(f'{data_dir}\\grades.csv')
    
    # 预处理成绩，将成绩转换为表现等级
    def grade_to_performance(score):
        if score >= 90:
            return '优秀'
        elif score >= 80:
            return '良好'
        elif score >= 70:
            return '中等'
        elif score >= 60:
            return '及格'
        else:
            return '不及格'
    
    grades_df['performance'] = grades_df['score'].apply(grade_to_performance)
    
    # 按学生分组，创建交易数据
    student_groups = grades_df.groupby('student_id')
    transactions = []
    
    for student_id, group in student_groups:
        # 收集学生的课程和表现
        items = []
        
        # 添加课程
        for _, row in group.iterrows():
            # 根据实际列名获取课程名称
            if 'course_name' in row:
                course_name = row['course_name']
            elif 'course' in row:
                course_name = row['course']
            else:
                course_name = f'课程_{_}'
            items.append(course_name)
        
        # 添加整体表现（基于平均成绩）
        avg_score = group['score'].mean()
        overall_performance = grade_to_performance(avg_score)
        items.append(f'整体表现:{overall_performance}')
        
        transactions.append(items)
    
    return transactions

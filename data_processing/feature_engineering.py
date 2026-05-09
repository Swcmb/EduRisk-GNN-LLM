import pandas as pd
import numpy as np

def extract_features(cleaned_data):
    """
    提取学生特征
    
    Args:
        cleaned_data (dict): 清洗后的数据
    
    Returns:
        pd.DataFrame: 提取的特征数据
    """
    # 初始化特征数据
    features = pd.DataFrame()
    
    # 提取学生ID
    if 'students' in cleaned_data:
        features['student_id'] = cleaned_data['students']['student_id']
    elif 'grades' in cleaned_data:
        features['student_id'] = cleaned_data['grades']['student_id'].unique()
    else:
        return features
    
    # 提取学业表现特征
    if 'grades' in cleaned_data:
        grades = cleaned_data['grades']
        # 计算平均成绩
        avg_score = grades.groupby('student_id')['score'].mean().rename('avg_score')
        features = features.merge(avg_score, on='student_id', how='left')
        
        # 计算成绩标准差
        std_score = grades.groupby('student_id')['score'].std().rename('std_score')
        features = features.merge(std_score, on='student_id', how='left')
        
        # 计算不及格课程数
        fail_courses = grades[grades['score'] < 60].groupby('student_id').size().rename('fail_courses')
        features = features.merge(fail_courses, on='student_id', how='left').fillna(0)
    
    # 提取出勤特征
    if 'attendance' in cleaned_data:
        attendance = cleaned_data['attendance']
        # 计算出勤率
        total_classes = attendance.groupby('student_id').size().rename('total_classes')
        present_classes = attendance[attendance['status'] == 'present'].groupby('student_id').size().rename('present_classes')
        attendance_rate = (present_classes / total_classes).rename('attendance_rate')
        features = features.merge(attendance_rate, on='student_id', how='left').fillna(0)
        
        # 计算迟到次数
        late_count = attendance[attendance['status'] == 'late'].groupby('student_id').size().rename('late_count')
        features = features.merge(late_count, on='student_id', how='left').fillna(0)
        
        # 计算缺勤次数
        absent_count = attendance[attendance['status'] == 'absent'].groupby('student_id').size().rename('absent_count')
        features = features.merge(absent_count, on='student_id', how='left').fillna(0)
    
    # 提取选课行为特征
    if 'courses' in cleaned_data:
        courses = cleaned_data['courses']
        # 计算选课数量
        course_count = courses.groupby('student_id').size().rename('course_count')
        features = features.merge(course_count, on='student_id', how='left').fillna(0)
        
        # 计算每学期平均选课数
        semester_courses = courses.groupby(['student_id', 'semester', 'year']).size().groupby('student_id').mean().rename('avg_semester_courses')
        features = features.merge(semester_courses, on='student_id', how='left').fillna(0)
    
    # 填充缺失值
    features = features.fillna(0)
    
    return features
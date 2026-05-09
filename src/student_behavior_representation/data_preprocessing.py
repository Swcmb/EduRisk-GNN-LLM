import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.decomposition import PCA

class DataPreprocessor:
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.students_df = None
        self.grades_df = None
        self.attendance_df = None
        self.processed_data = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
    
    def load_data(self):
        """加载所有数据文件"""
        self.students_df = pd.read_csv(f'{self.data_dir}/students.csv')
        self.grades_df = pd.read_csv(f'{self.data_dir}/grades.csv')
        self.attendance_df = pd.read_csv(f'{self.data_dir}/attendance.csv')
        print(f"加载数据完成: {len(self.students_df)} 名学生")
    
    def process_student_features(self):
        """处理学生基本特征"""
        student_features = self.students_df.copy()
        
        # 编码性别
        le_gender = LabelEncoder()
        student_features['gender_encoded'] = le_gender.fit_transform(student_features['gender'])
        self.label_encoders['gender'] = le_gender
        
        # 编码专业
        le_major = LabelEncoder()
        student_features['major_encoded'] = le_major.fit_transform(student_features['major'])
        self.label_encoders['major'] = le_major
        
        # 编码班级
        le_class = LabelEncoder()
        student_features['class_encoded'] = le_class.fit_transform(student_features['class'])
        self.label_encoders['class'] = le_class
        
        return student_features
    
    def process_grade_features(self):
        """处理成绩特征"""
        # 计算每个学生的成绩统计信息
        grade_stats = self.grades_df.groupby('student_id')['score'].agg([
            'mean', 'std', 'min', 'max', 'count'
        ]).reset_index()
        grade_stats.columns = ['student_id', 'avg_score', 'score_std', 'min_score', 'max_score', 'course_count']
        
        # 计算不及格课程数量
        failed_courses = self.grades_df[self.grades_df['score']<60].groupby('student_id')['score'].count().reset_index()
        failed_courses.columns = ['student_id', 'failed_count']
        
        grade_features = grade_stats.merge(failed_courses, on='student_id', how='left')
        grade_features['failed_count'] = grade_features['failed_count'].fillna(0)
        
        # 计算不及格率
        grade_features['failure_rate'] = grade_features['failed_count'] / grade_features['course_count']
        
        return grade_features
    
    def process_attendance_features(self):
        """处理考勤特征"""
        # 计算每个学生的考勤统计
        attendance_stats = self.attendance_df.groupby('student_id')['status'].value_counts().unstack(fill_value=0)
        
        # 确保所有状态列都存在
        for status in ['present', 'absent', 'late']:
            if status not in attendance_stats.columns:
                attendance_stats[status] = 0
        
        attendance_stats = attendance_stats.reset_index()
        attendance_stats['total_attendance'] = attendance_stats[['present', 'absent', 'late']].sum(axis=1)
        
        # 计算出勤率和迟到率
        attendance_stats['attendance_rate'] = attendance_stats['present'] / attendance_stats['total_attendance']
        attendance_stats['late_rate'] = attendance_stats['late'] / attendance_stats['total_attendance']
        attendance_stats['absent_rate'] = attendance_stats['absent'] / attendance_stats['total_attendance']
        
        return attendance_stats
    
    def integrate_features(self):
        """整合所有特征"""
        student_features = self.process_student_features()
        grade_features = self.process_grade_features()
        attendance_features = self.process_attendance_features()
        
        # 合并所有特征
        integrated = student_features.merge(grade_features, on='student_id', how='left')
        integrated = integrated.merge(attendance_features, on='student_id', how='left')
        
        # 填充缺失值
        integrated = integrated.fillna(0)
        
        return integrated
    
    def prepare_model_input(self, features=None):
        """准备模型输入数据"""
        if features is None:
            features = self.integrate_features()
        
        # 选择特征列
        feature_columns = [
            'age', 'gender_encoded', 'major_encoded', 'class_encoded',
            'avg_score', 'score_std', 'min_score', 'max_score', 'course_count',
            'failed_count', 'failure_rate', 'attendance_rate', 'late_rate', 'absent_rate'
        ]
        
        X = features[feature_columns].values
        
        # 标准化特征
        X_scaled = self.scaler.fit_transform(X)
        
        # 保存处理后的数据
        self.processed_data = {
            'features': X_scaled,
            'student_ids': features['student_id'].values,
            'feature_names': feature_columns
        }
        
        return X_scaled, features['student_id'].values
    
    def transform_new_data(self, new_data):
        """转换新数据以匹配训练数据的格式"""
        # 应用相同的编码和标准化
        for col, le in self.label_encoders.items():
            if col in new_data.columns:
                new_data[f'{col}_encoded'] = le.transform(new_data[col])
        
        feature_columns = [
            'age', 'gender_encoded', 'major_encoded', 'class_encoded',
            'avg_score', 'score_std', 'min_score', 'max_score', 'course_count',
            'failed_count', 'failure_rate', 'attendance_rate', 'late_rate', 'absent_rate'
        ]
        
        X = new_data[feature_columns].values
        X_scaled = self.scaler.transform(X)
        
        return X_scaled
    
    def reduce_dimensions(self, n_components=32):
        """使用PCA降维"""
        if self.processed_data is None:
            self.prepare_model_input()
        
        pca = PCA(n_components=n_components)
        X_reduced = pca.fit_transform(self.processed_data['features'])
        
        return X_reduced, pca
    
    def get_feature_statistics(self):
        """获取特征统计信息"""
        if self.processed_data is None:
            self.prepare_model_input()
        
        stats = {
            'mean': np.mean(self.processed_data['features'], axis=0),
            'std': np.std(self.processed_data['features'], axis=0),
            'min': np.min(self.processed_data['features'], axis=0),
            'max': np.max(self.processed_data['features'], axis=0)
        }
        
        return stats
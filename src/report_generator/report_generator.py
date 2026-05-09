import pandas as pd
import os
from typing import Dict, Any, Optional
from .llm_integration import LLMIntegration
from .report_templates import ReportTemplates
from data_processing.data_loader import load_data
from data_processing.feature_engineering import extract_features
from classification.classification import AcademicRiskClassifier

class ReportGenerator:
    def __init__(self, llm_api_key: Optional[str] = None):
        """
        初始化报告生成器
        
        Args:
            llm_api_key: LLM API密钥
        """
        self.llm_integration = LLMIntegration(api_key=llm_api_key)
        self.templates = ReportTemplates()
        self.classifier = AcademicRiskClassifier()
        self.risk_thresholds = {
            'low': 0.3,
            'medium': 0.6,
            'high': 0.8
        }
        # 缓存数据，避免重复加载和处理
        self.cached_data = None
        self.cached_features = None
        self.cached_X = None
        self.cached_y = None
    
    def load_and_process_data(self):
        """
        加载和处理数据
        
        Returns:
            处理后的数据和特征
        """
        # 检查缓存是否存在
        if self.cached_data is not None and self.cached_features is not None:
            return self.cached_data, self.cached_features, self.cached_X, self.cached_y
        
        # 加载数据
        data = load_data()
        
        # 提取特征
        features = extract_features(data)
        
        # 创建目标变量
        target = []
        for _, row in features.iterrows():
            if row.get('fail_courses', 0) >= 2 or row.get('avg_score', 100) < 60:
                target.append(1)
            else:
                target.append(0)
        
        # 预处理数据
        feature_columns = [col for col in features.columns if col != 'student_id']
        X = features[feature_columns]
        y = target
        
        self.classifier.load_data(X, y)
        self.classifier.preprocess_data()
        
        # 检查是否有多个类别
        if len(set(y)) > 1:
            self.classifier.handle_class_imbalance()
            self.classifier.train_decision_tree()
            self.classifier.train_logistic_regression()
        
        # 缓存数据
        self.cached_data = data
        self.cached_features = features
        self.cached_X = X
        self.cached_y = y
        
        return data, features, X, y
    
    def generate_student_report(self, student_id: str) -> str:
        """
        生成学生报告
        
        Args:
            student_id: 学生ID
        
        Returns:
            生成的报告文本
        """
        # 加载和处理数据
        data, features, X, y = self.load_and_process_data()
        
        # 找到学生对应的特征
        try:
            student_id_int = int(student_id)
            student_features = features[features['student_id'] == student_id_int]
        except ValueError:
            student_features = features[features['student_id'] == student_id]
        
        if student_features.empty:
            return f"未找到学生ID为{student_id}的学生数据"
        
        # 提取学生信息
        students = data.get('students', pd.DataFrame())
        try:
            student_id_int = int(student_id)
            student_info = students[students['student_id'] == student_id_int]
        except ValueError:
            student_info = students[students['student_id'] == student_id]
        student_name = student_info['name'].values[0] if not student_info.empty else '学生'
        
        # 预测风险等级
        student_X = student_features[[col for col in student_features.columns if col != 'student_id']]
        if hasattr(self.classifier, 'decision_tree_model') and self.classifier.decision_tree_model is not None:
            probabilities = self.classifier.decision_tree_model.predict_proba(self.classifier.scaler.transform(student_X))[:, 1]
        else:
            # 基于规则计算风险概率
            fail_courses = student_features['fail_courses'].values[0]
            avg_score = student_features['avg_score'].values[0]
            risk_prob = 0
            if fail_courses >= 2:
                risk_prob = 0.8
            elif fail_courses >= 1:
                risk_prob = 0.5
            elif avg_score < 60:
                risk_prob = 0.7
            elif avg_score < 70:
                risk_prob = 0.3
            else:
                risk_prob = 0.1
            probabilities = [risk_prob]
        
        # 确定风险等级
        risk_prob = probabilities[0]
        if risk_prob >= self.risk_thresholds['high']:
            risk_level = '高风险'
        elif risk_prob >= self.risk_thresholds['medium']:
            risk_level = '中风险'
        elif risk_prob >= self.risk_thresholds['low']:
            risk_level = '低风险'
        else:
            risk_level = '无风险'
        
        # 构建报告数据
        report_data = {
            'student_info': {
                'student_id': student_id,
                'name': student_name
            },
            'risk_info': {
                'risk_level': risk_level,
                'risk_probability': risk_prob
            },
            'academic_info': {
                'avg_score': student_features['avg_score'].values[0],
                'fail_courses': student_features['fail_courses'].values[0],
                'attendance_rate': student_features.get('attendance_rate', 0).values[0]
            }
        }
        
        # 获取模板
        template = self.templates.get_student_template()
        
        # 生成报告
        report = self.llm_integration.generate_report('student', report_data, template)
        
        return report
    
    def generate_teacher_report(self, class_name: str) -> str:
        """
        生成教师报告
        
        Args:
            class_name: 班级名称
        
        Returns:
            生成的报告文本
        """
        # 加载和处理数据
        data, features, X, y = self.load_and_process_data()
        
        # 假设所有学生都属于同一个班级
        total_students = len(features)
        
        # 预测所有学生的风险等级
        if hasattr(self.classifier, 'decision_tree_model') and self.classifier.decision_tree_model is not None:
            probabilities = self.classifier.decision_tree_model.predict_proba(self.classifier.scaler.transform(X))[:, 1]
        else:
            # 基于规则计算风险概率
            probabilities = []
            for _, row in features.iterrows():
                fail_courses = row.get('fail_courses', 0)
                avg_score = row.get('avg_score', 100)
                risk_prob = 0
                if fail_courses >= 2:
                    risk_prob = 0.8
                elif fail_courses >= 1:
                    risk_prob = 0.5
                elif avg_score < 60:
                    risk_prob = 0.7
                elif avg_score < 70:
                    risk_prob = 0.3
                else:
                    risk_prob = 0.1
                probabilities.append(risk_prob)
        
        # 统计风险分布
        high_risk_count = 0
        medium_risk_count = 0
        low_risk_count = 0
        
        for prob in probabilities:
            if prob >= self.risk_thresholds['high']:
                high_risk_count += 1
            elif prob >= self.risk_thresholds['medium']:
                medium_risk_count += 1
            elif prob >= self.risk_thresholds['low']:
                low_risk_count += 1
        
        # 计算平均成绩
        avg_score = features['avg_score'].mean()
        
        # 构建报告数据
        report_data = {
            'class_info': {
                'class_name': class_name,
                'total_students': total_students
            },
            'risk_info': {
                'high_risk_count': high_risk_count,
                'medium_risk_count': medium_risk_count,
                'low_risk_count': low_risk_count
            },
            'academic_info': {
                'avg_score': avg_score
            }
        }
        
        # 获取模板
        template = self.templates.get_teacher_template()
        
        # 生成报告
        report = self.llm_integration.generate_report('teacher', report_data, template)
        
        return report
    
    def generate_admin_report(self) -> str:
        """
        生成管理者报告
        
        Returns:
            生成的报告文本
        """
        # 加载和处理数据
        data, features, X, y = self.load_and_process_data()
        
        # 学生总数
        total_students = len(features)
        
        # 预测所有学生的风险等级
        if hasattr(self.classifier, 'decision_tree_model') and self.classifier.decision_tree_model is not None:
            probabilities = self.classifier.decision_tree_model.predict_proba(self.classifier.scaler.transform(X))[:, 1]
        else:
            # 基于规则计算风险概率
            probabilities = []
            for _, row in features.iterrows():
                fail_courses = row.get('fail_courses', 0)
                avg_score = row.get('avg_score', 100)
                risk_prob = 0
                if fail_courses >= 2:
                    risk_prob = 0.8
                elif fail_courses >= 1:
                    risk_prob = 0.5
                elif avg_score < 60:
                    risk_prob = 0.7
                elif avg_score < 70:
                    risk_prob = 0.3
                else:
                    risk_prob = 0.1
                probabilities.append(risk_prob)
        
        # 统计风险分布
        high_risk_count = 0
        medium_risk_count = 0
        low_risk_count = 0
        
        for prob in probabilities:
            if prob >= self.risk_thresholds['high']:
                high_risk_count += 1
            elif prob >= self.risk_thresholds['medium']:
                medium_risk_count += 1
            elif prob >= self.risk_thresholds['low']:
                low_risk_count += 1
        
        # 计算平均成绩和出勤率
        avg_score = features['avg_score'].mean()
        attendance_rate = features.get('attendance_rate', pd.Series([0])).mean()
        
        # 构建报告数据
        report_data = {
            'school_info': {
                'total_students': total_students
            },
            'risk_info': {
                'high_risk_count': high_risk_count,
                'medium_risk_count': medium_risk_count,
                'low_risk_count': low_risk_count
            },
            'academic_info': {
                'avg_score': avg_score,
                'attendance_rate': attendance_rate
            }
        }
        
        # 获取模板
        template = self.templates.get_admin_template()
        
        # 生成报告
        report = self.llm_integration.generate_report('admin', report_data, template)
        
        return report
    
    def export_report(self, report: str, filename: str, format: str = 'txt') -> bool:
        """
        导出报告
        
        Args:
            report: 报告文本
            filename: 文件名
            format: 格式，支持'txt', 'md'
        
        Returns:
            是否导出成功
        """
        try:
            # 确保文件扩展名正确
            if not filename.endswith(f'.{format}'):
                filename = f"{filename}.{format}"
            
            # 写入文件
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            
            return True
        except Exception as e:
            print(f"导出报告失败: {e}")
            return False
    
    def generate_and_export_report(self, role: str, filename: str, **kwargs) -> bool:
        """
        生成并导出报告
        
        Args:
            role: 角色，如'student', 'teacher', 'admin'
            filename: 文件名
            **kwargs: 额外参数
        
        Returns:
            是否成功
        """
        try:
            if role == 'student':
                student_id = kwargs.get('student_id')
                if not student_id:
                    print("生成学生报告需要提供student_id参数")
                    return False
                report = self.generate_student_report(student_id)
            elif role == 'teacher':
                class_name = kwargs.get('class_name', '班级')
                report = self.generate_teacher_report(class_name)
            elif role == 'admin':
                report = self.generate_admin_report()
            else:
                print(f"未知角色: {role}")
                return False
            
            # 导出报告
            return self.export_report(report, filename)
        except Exception as e:
            print(f"生成和导出报告失败: {e}")
            return False

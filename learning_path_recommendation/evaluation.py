import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from learning_path_recommendation.recommendation import LearningPathRecommender

class RecommendationEvaluator:
    def __init__(self, recommender):
        self.recommender = recommender
    
    def evaluate(self, test_size=0.2, top_n=5):
        """
        评估推荐算法性能
        
        Args:
            test_size: 测试集比例
            top_n: 推荐课程数量
            
        Returns:
            dict: 评估指标
        """
        # 准备数据
        data = self.recommender.data
        courses_data = data['courses']
        
        # 按学生分组
        student_groups = courses_data.groupby('student_id')
        
        # 准备评估数据
        students = []
        actual_courses = []
        predicted_courses = []
        
        for student_id, group in student_groups:
            # 确保学生至少有3门课程
            if len(group) < 3:
                continue
            
            # 分割训练集和测试集
            train_courses, test_courses = train_test_split(group['course_id'].tolist(), test_size=test_size, random_state=42)
            
            # 模拟学生已选课程（使用训练集）
            # 这里需要临时修改recommender的数据
            original_courses = data['courses'].copy()
            data['courses'] = data['courses'][~((data['courses']['student_id'] == student_id) & (~data['courses']['course_id'].isin(train_courses)))]
            
            # 重新拟合模型
            self.recommender.fit(data)
            
            # 获取推荐
            recommendations = self.recommender.recommend_courses(student_id, top_n)
            
            # 恢复原始数据
            data['courses'] = original_courses
            
            # 收集结果
            students.append(student_id)
            actual_courses.append(test_courses)
            predicted_courses.append(recommendations)
        
        # 计算评估指标
        metrics = {
            'precision': self._calculate_precision(actual_courses, predicted_courses),
            'recall': self._calculate_recall(actual_courses, predicted_courses),
            'f1_score': self._calculate_f1_score(actual_courses, predicted_courses),
            'ndcg': self._calculate_ndcg(actual_courses, predicted_courses)
        }
        
        return metrics
    
    def _calculate_precision(self, actual, predicted):
        """
        计算精确率
        """
        precision_scores = []
        for a, p in zip(actual, predicted):
            if len(p) == 0:
                continue
            intersection = set(a) & set(p)
            precision = len(intersection) / len(p)
            precision_scores.append(precision)
        return np.mean(precision_scores) if precision_scores else 0
    
    def _calculate_recall(self, actual, predicted):
        """
        计算召回率
        """
        recall_scores = []
        for a, p in zip(actual, predicted):
            if len(a) == 0:
                continue
            intersection = set(a) & set(p)
            recall = len(intersection) / len(a)
            recall_scores.append(recall)
        return np.mean(recall_scores) if recall_scores else 0
    
    def _calculate_f1_score(self, actual, predicted):
        """
        计算F1分数
        """
        precision = self._calculate_precision(actual, predicted)
        recall = self._calculate_recall(actual, predicted)
        if precision + recall == 0:
            return 0
        return 2 * (precision * recall) / (precision + recall)
    
    def _calculate_ndcg(self, actual, predicted):
        """
        计算NDCG（归一化折损累积增益）
        """
        ndcg_scores = []
        for a, p in zip(actual, predicted):
            # 计算DCG
            dcg = 0
            for i, course in enumerate(p):
                if course in a:
                    dcg += 1 / np.log2(i + 2)  # 位置从1开始
            
            # 计算理想DCG
            ideal_dcg = 0
            for i in range(min(len(a), len(p))):
                ideal_dcg += 1 / np.log2(i + 2)
            
            # 计算NDCG
            ndcg = dcg / ideal_dcg if ideal_dcg > 0 else 0
            ndcg_scores.append(ndcg)
        
        return np.mean(ndcg_scores) if ndcg_scores else 0
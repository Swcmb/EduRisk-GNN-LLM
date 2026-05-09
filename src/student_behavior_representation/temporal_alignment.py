import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple, Dict, Optional


class TemporalAlignment:
    """时序行为对齐与样本对生成模块"""
    
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.students_df = None
        self.grades_df = None
        self.attendance_df = None
        self.temporal_data = None
        self.student_temporal_features = {}
    
    def load_data(self):
        """加载所有数据文件"""
        self.students_df = pd.read_csv(f'{self.data_dir}/students.csv')
        self.grades_df = pd.read_csv(f'{self.data_dir}/grades.csv')
        self.attendance_df = pd.read_csv(f'{self.data_dir}/attendance.csv')
        print(f"加载数据完成: {len(self.students_df)} 名学生")
    
    def build_temporal_features(self):
        """构建时序特征"""
        # 按学期和年份排序
        self.grades_df['semester_order'] = self.grades_df['semester'].map({
            '第一学期': 1, '第二学期': 2, '第三学期': 3,
            '第四学期': 4, '第五学期': 5, '第六学期': 6
        })
        self.grades_df['time_order'] = self.grades_df['year'] * 10 + self.grades_df['semester_order']
        self.grades_df = self.grades_df.sort_values(['student_id', 'time_order'])
        
        # 为每个学生构建时序特征
        for student_id in self.students_df['student_id'].unique():
            student_grades = self.grades_df[self.grades_df['student_id'] == student_id]
            if len(student_grades) >= 2:
                # 计算每个学期的统计特征
                semester_features = []
                for semester, semester_data in student_grades.groupby(['year', 'semester']):
                    features = {
                        'avg_score': semester_data['score'].mean(),
                        'score_std': semester_data['score'].std() if len(semester_data) > 1 else 0,
                        'min_score': semester_data['score'].min(),
                        'max_score': semester_data['score'].max(),
                        'course_count': len(semester_data),
                        'failed_count': (semester_data['score']< 60).sum(),
                        'failure_rate': (semester_data['score']< 60).mean()
                    }
                    semester_features.append(features)
                
                self.student_temporal_features[student_id] = semester_features
        
        print(f"构建时序特征完成: {len(self.student_temporal_features)} 名学生有时序数据")
    
    def create_positive_pairs_with_sliding_window(self, window_size=2, min_similarity=0.3):
        """使用滑动窗口机制构建正样本对"""
        positive_pairs = []
        
        for student_id, features_list in self.student_temporal_features.items():
            n_periods = len(features_list)
            
            # 使用滑动窗口创建同一学生不同周期的正样本对
            for i in range(n_periods - window_size + 1):
                for j in range(i + 1, min(i + window_size, n_periods)):
                    # 提取两个周期的特征向量
                    feat1 = np.array([features_list[i][k] for k in ['avg_score', 'score_std', 'min_score', 'max_score', 
                                                                 'course_count', 'failed_count', 'failure_rate']])
                    feat2 = np.array([features_list[j][k] for k in ['avg_score', 'score_std', 'min_score', 'max_score', 
                                                                 'course_count', 'failed_count', 'failure_rate']])
                    
                    # 计算相似度
                    similarity = self._calculate_similarity(feat1, feat2)
                    
                    # 只保留相似度高于阈值的正样本对
                    if similarity >= min_similarity:
                        positive_pairs.append({
                            'student_id_1': student_id,
                            'student_id_2': student_id,
                            'period_1': i,
                            'period_2': j,
                            'similarity': similarity,
                            'label': 1  # 正样本
                        })
        
        print(f"生成正样本对: {len(positive_pairs)} 对")
        return positive_pairs
    
    def create_negative_pairs(self, max_negatives_per_positive=8, max_similarity=0.9):
        """生成负样本对（不同学生行为序列）"""
        negative_pairs = []
        
        # 获取所有学生的时序特征列表
        student_ids = list(self.student_temporal_features.keys())
        n_students = len(student_ids)
        
        # 为每个学生生成负样本对
        for i, student_id_1 in enumerate(student_ids):
            features_list_1 = self.student_temporal_features[student_id_1]
            
            # 为该学生的每个周期生成负样本
            for period_1, feat1_dict in enumerate(features_list_1):
                feat1 = np.array([feat1_dict[k] for k in ['avg_score', 'score_std', 'min_score', 'max_score', 
                                                        'course_count', 'failed_count', 'failure_rate']])
                
                # 选择其他学生作为负样本
                candidate_students = [student_ids[j] for j in range(n_students) if j != i]
                
                # 计算与其他学生所有周期的相似度
                similarities = []
                for student_id_2 in candidate_students[:10]:  # 只考虑前10个其他学生以提高效率
                    features_list_2 = self.student_temporal_features[student_id_2]
                    for period_2, feat2_dict in enumerate(features_list_2):
                        feat2 = np.array([feat2_dict[k] for k in ['avg_score', 'score_std', 'min_score', 'max_score', 
                                                                'course_count', 'failed_count', 'failure_rate']])
                        similarity = self._calculate_similarity(feat1, feat2)
                        similarities.append({
                            'student_id_2': student_id_2,
                            'period_2': period_2,
                            'similarity': similarity
                        })
                
                # 按相似度排序，选择相似度较低的作为负样本
                similarities.sort(key=lambda x: x['similarity'])
                
                # 选择不超过max_negatives_per_positive个负样本
                selected_negatives = similarities[:max_negatives_per_positive]
                
                for neg in selected_negatives:
                    # 确保负样本对的相似度低于阈值
                    if neg['similarity']< max_similarity:
                        negative_pairs.append({
                            'student_id_1': student_id_1,
                            'student_id_2': neg['student_id_2'],
                            'period_1': period_1,
                            'period_2': neg['period_2'],
                            'similarity': neg['similarity'],
                            'label': 0  # 负样本
                        })
        
        print(f"生成负样本对: {len(negative_pairs)} 对")
        return negative_pairs
    
    def _calculate_similarity(self, vec1, vec2):
        """计算两个特征向量的相似度"""
        # 标准化向量
        vec1_norm = vec1 / (np.linalg.norm(vec1) + 1e-8)
        vec2_norm = vec2 / (np.linalg.norm(vec2) + 1e-8)
        
        # 计算余弦相似度
        similarity = np.dot(vec1_norm, vec2_norm)
        return similarity
    
    def balance_sample_pairs(self, positive_pairs, negative_pairs, target_ratio=(1, 4), max_ratio=(1, 8)):
        """平衡正负样本对比例"""
        n_positive = len(positive_pairs)
        n_negative = len(negative_pairs)
        
        # 计算目标负样本数量范围
        min_negatives = n_positive * target_ratio[1]
        max_negatives = n_positive * max_ratio[1]
        
        # 如果负样本太少，保留所有负样本
        if n_negative <= min_negatives:
            print(f"负样本不足，保留所有 {n_negative} 个负样本")
            return positive_pairs, negative_pairs
        
        # 如果负样本太多，随机抽样
        if n_negative > max_negatives:
            np.random.seed(42)
            selected_indices = np.random.choice(len(negative_pairs), int(max_negatives), replace=False)
            selected_negatives = [negative_pairs[i] for i in selected_indices]
            print(f"负样本过多，随机抽样 {len(selected_negatives)} 个负样本")
            return positive_pairs, selected_negatives
        
        # 负样本数量在目标范围内，无需调整
        print(f"样本对比例合适: {n_positive}:{n_negative}")
        return positive_pairs, negative_pairs
    
    def filter_low_quality_pairs(self, pairs, min_similarity=0.1, max_similarity=0.95):
        """过滤低质量样本对"""
        filtered_pairs = []
        
        for pair in pairs:
            similarity = pair['similarity']
            # 过滤相似度异常的样本对
            if min_similarity <= similarity <= max_similarity:
                filtered_pairs.append(pair)
        
        print(f"过滤后样本对数量: {len(filtered_pairs)}")
        return filtered_pairs
    
    def generate_sample_pairs(self, window_size=2, min_positive_similarity=0.3, 
                            max_negative_similarity=0.7, target_ratio=(1, 4), 
                            max_ratio=(1, 8)):
        """生成最终的样本对"""
        # 构建时序特征
        self.build_temporal_features()
        
        # 创建正样本对
        positive_pairs = self.create_positive_pairs_with_sliding_window(
            window_size=window_size,
            min_similarity=min_positive_similarity
        )
        
        # 创建负样本对
        negative_pairs = self.create_negative_pairs(
            max_negatives_per_positive=max_ratio[1]
        )
        
        # 过滤低质量样本对
        positive_pairs = self.filter_low_quality_pairs(positive_pairs)
        negative_pairs = self.filter_low_quality_pairs(negative_pairs)
        
        # 平衡样本对比例
        balanced_positive, balanced_negative = self.balance_sample_pairs(
            positive_pairs, 
            negative_pairs,
            target_ratio=target_ratio,
            max_ratio=max_ratio
        )
        
        # 合并所有样本对
        all_pairs = balanced_positive + balanced_negative
        
        # 统计信息
        n_positive = len(balanced_positive)
        n_negative = len(balanced_negative)
        ratio = n_negative / n_positive if n_positive > 0 else 0
        
        print(f"\n样本对生成完成:")
        print(f"  正样本对: {n_positive}")
        print(f"  负样本对: {n_negative}")
        print(f"  正负样本比例: 1:{ratio:.2f}")
        
        return all_pairs, balanced_positive, balanced_negative
    
    def analyze_pair_quality(self, pairs):
        """分析样本对质量"""
        if not pairs:
            return {}
        
        similarities = [p['similarity'] for p in pairs]
        positive_similarities = [p['similarity'] for p in pairs if p['label'] == 1]
        negative_similarities = [p['similarity'] for p in pairs if p['label'] == 0]
        
        quality_metrics = {
            'total_pairs': len(pairs),
            'positive_pairs': len(positive_similarities),
            'negative_pairs': len(negative_similarities),
            'avg_similarity': np.mean(similarities),
            'positive_avg_similarity': np.mean(positive_similarities) if positive_similarities else 0,
            'negative_avg_similarity': np.mean(negative_similarities) if negative_similarities else 0,
            'similarity_std': np.std(similarities),
            'positive_similarity_std': np.std(positive_similarities) if positive_similarities else 0,
            'negative_similarity_std': np.std(negative_similarities) if negative_similarities else 0
        }
        
        return quality_metrics
    
    def save_sample_pairs(self, pairs, file_path='sample_pairs.csv'):
        """保存样本对到文件"""
        df = pd.DataFrame(pairs)
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f"样本对已保存到: {file_path}")
    
    def load_sample_pairs(self, file_path='sample_pairs.csv'):
        """从文件加载样本对"""
        df = pd.read_csv(file_path)
        pairs = df.to_dict('records')
        print(f"从 {file_path} 加载了 {len(pairs)} 个样本对")
        return pairs

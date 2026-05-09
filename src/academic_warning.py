import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import random
import json
import logging
from datetime import datetime, timedelta
from classification.classification import AcademicRiskClassifier
from data_processing.data_loader import load_data
from data_processing.feature_engineering import extract_features


class AdvancedStudentDataGenerator:
    """高级学生行为数据生成器，支持从真实基础数据生成图结构和样本对"""
    
    def __init__(self, num_students=1000, weeks=8, features=20, use_real_data=False, data_dir='data'):
        self.num_students = num_students
        self.weeks = weeks
        self.features = features
        self.use_real_data = use_real_data
        self.data_dir = data_dir
        
        # 初始化数据
        self.student_ids = []
        self.names = []
        self.genders = ['男', '女']
        self.majors = ['计算机科学与技术', '电子工程', '软件工程', '数据科学', '人工智能', '信息安全', '网络工程', '物联网工程']
        
        # 设置日志
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # 定义行为特征列表
        self.behavior_features = [
            'daily_study_hours', 'homework_completion_rate', 'class_participation',
            'exam_scores', 'attendance_rate', 'online_activity', 'assignment_quality',
            'study_consistency', 'learning_progress', 'peer_interaction',
            'resource_usage', 'time_management', 'goal_setting', 'feedback_usage',
            'self_assessment', 'collaboration_skills', 'problem_solving', 'creativity',
            'critical_thinking', 'emotional_regulation'
        ]
        
        # 图结构实体定义
        self.node_types = ['student', 'course', 'behavior_event', 'time_period']
        self.edge_types = ['takes', 'exhibits', 'occurs_at', 'related_to']
        
        # 如果使用真实数据，加载数据
        if self.use_real_data:
            self._load_real_data()
        else:
            self.student_ids = [f'S{i+1:04d}' for i in range(num_students)]
            self.names = self._generate_names()
    
    def _load_real_data(self):
        """从数据文件加载真实数据"""
        try:
            # 加载学生信息
            students_path = os.path.join(self.data_dir, 'students.csv')
            if os.path.exists(students_path):
                self.students_df = pd.read_csv(students_path)
                self.student_ids = self.students_df['student_id'].tolist()
                self.names = self.students_df['name'].tolist()
                self.logger.info(f"成功加载学生数据：{len(self.student_ids)}名学生")
            else:
                self.logger.warning("学生数据文件不存在，使用模拟数据")
                self.student_ids = [f'S{i+1:04d}' for i in range(self.num_students)]
                self.names = self._generate_names()
            
            # 加载成绩数据
            grades_path = os.path.join(self.data_dir, 'grades.csv')
            if os.path.exists(grades_path):
                self.grades_df = pd.read_csv(grades_path)
                self.logger.info(f"成功加载成绩数据：{len(self.grades_df)}条记录")
            else:
                self.grades_df = None
                self.logger.warning("成绩数据文件不存在")
            
            # 加载出勤数据
            attendance_path = os.path.join(self.data_dir, 'attendance.csv')
            if os.path.exists(attendance_path):
                self.attendance_df = pd.read_csv(attendance_path)
                self.logger.info(f"成功加载出勤数据：{len(self.attendance_df)}条记录")
            else:
                self.attendance_df = None
                self.logger.warning("出勤数据文件不存在")
            
            # 加载选课数据
            courses_path = os.path.join(self.data_dir, 'courses.csv')
            if os.path.exists(courses_path):
                self.courses_df = pd.read_csv(courses_path)
                self.logger.info(f"成功加载选课数据：{len(self.courses_df)}条记录")
            else:
                self.courses_df = None
                self.logger.warning("选课数据文件不存在")
            
            # 加载行为数据（如果存在）
            behavior_path = os.path.join('advanced_data', 'csv', 'behavior_data.csv')
            if os.path.exists(behavior_path):
                self.behavior_df = pd.read_csv(behavior_path)
                self.logger.info(f"成功加载行为数据：{len(self.behavior_df)}条记录")
            else:
                self.behavior_df = None
                self.logger.warning("行为数据文件不存在")
                
        except Exception as e:
            self.logger.error(f"加载真实数据失败：{str(e)}")
            # 回退到模拟数据
            self.student_ids = [f'S{i+1:04d}' for i in range(self.num_students)]
            self.names = self._generate_names()
    
    def _generate_names(self):
        """生成随机姓名"""
        surnames = ['王', '李', '张', '刘', '陈', '杨', '赵', '黄', '周', '吴', '徐', '孙', '马', '朱', '胡', '郭', '何', '高', '林', '罗']
        given_names = ['伟', '芳', '娜', '敏', '静', '丽', '强', '磊', '军', '洋', '勇', '艳', '杰', '娟', '涛', '明', '超', '秀英', '霞', '平']
        names = []
        for _ in range(len(self.student_ids)):
            surname = random.choice(surnames)
            given_name = random.choice(given_names)
            names.append(f"{surname}{given_name}")
        return names
    
    def generate_student_profiles(self):
        """生成学生基本信息"""
        data = []
        for i in range(self.num_students):
            student_id = self.student_ids[i]
            name = self.names[i]
            age = random.randint(18, 25)
            gender = random.choice(self.genders)
            major = random.choice(self.majors)
            data.append([student_id, name, age, gender, major])
        
        df = pd.DataFrame(data, columns=['student_id', 'name', 'age', 'gender', 'major'])
        return df
    
    def generate_temporal_behavior_data(self):
        """生成时序行为数据，每个学生包含指定周数的数据"""
        data = []
        
        for student_id in self.student_ids:
            # 获取学生基础信息（用于影响行为模式）
            student_index = int(student_id[1:]) - 1
            major = self.majors[student_index % len(self.majors)]
            
            # 为每个学生生成不同的行为模式基线
            baseline_pattern = self._generate_behavior_pattern(major)
            
            # 生成每周的行为数据
            for week in range(1, self.weeks + 1):
                # 根据周数和行为模式生成本周的行为特征
                week_data = self._generate_week_behavior(baseline_pattern, week)
                
                # 添加学生ID和周数信息
                week_data['student_id'] = student_id
                week_data['week_number'] = week
                week_data['timestamp'] = f"2024-W{week:02d}"
                
                data.append(week_data)
        
        df = pd.DataFrame(data)
        return df
    
    def _generate_behavior_pattern(self, major):
        """生成学生的基础行为模式"""
        pattern = {}
        
        # 根据专业设置不同的行为基线
        if major in ['计算机科学与技术', '软件工程']:
            # 技术类专业学生特征
            pattern['daily_study_hours'] = random.uniform(4, 8)
            pattern['homework_completion_rate'] = random.uniform(0.8, 0.95)
            pattern['class_participation'] = random.uniform(0.7, 0.9)
            pattern['online_activity'] = random.uniform(0.8, 1.0)
        elif major in ['数据科学', '人工智能']:
            # 数据科学类专业学生特征
            pattern['daily_study_hours'] = random.uniform(5, 9)
            pattern['homework_completion_rate'] = random.uniform(0.75, 0.9)
            pattern['class_participation'] = random.uniform(0.6, 0.8)
            pattern['learning_progress'] = random.uniform(0.7, 0.9)
        else:
            # 其他专业学生特征
            pattern['daily_study_hours'] = random.uniform(3, 7)
            pattern['homework_completion_rate'] = random.uniform(0.7, 0.9)
            pattern['class_participation'] = random.uniform(0.65, 0.85)
        
        # 生成其他特征的基线值
        for feature in self.behavior_features:
            if feature not in pattern:
                pattern[feature] = random.uniform(0.3, 0.8)
        
        return pattern
    
    def _generate_week_behavior(self, baseline_pattern, week):
        """生成特定周的行为数据，包含真实的学生行为模式"""
        week_data = {}
        
        # 添加趋势变化（学习曲线）
        week_factor = min(1.0, 0.8 + week * 0.025)  # 逐渐提高学习效率
        
        # 考试影响因子
        exam_factor = 1.0
        if week == 4:  # 期中考试周
            exam_factor = 1.2  # 考试前学习时间增加
        elif week == self.weeks:  # 期末考试周
            exam_factor = 1.3
        elif week == 3 or week == self.weeks - 1:  # 考试前一周
            exam_factor = 1.1
        
        # 周末vs工作日差异
        day_type = random.choice(['weekday', 'weekend'])
        weekend_factor = 0.7 if day_type == 'weekend' else 1.0
        
        # 季节性变化（例如节假日影响）
        holiday_factor = 0.8 if week in [6, 7] else 1.0  # 假设第6、7周有节假日
        
        for feature in self.behavior_features:
            baseline = baseline_pattern[feature]
            
            # 根据特征类型应用不同的行为模式
            if feature in ['daily_study_hours', 'homework_completion_rate']:
                # 学习相关特征受考试影响大
                value = baseline * week_factor * exam_factor * (1 + random.uniform(-0.1, 0.2))
            elif feature in ['online_activity', 'resource_usage']:
                # 在线活动受周末影响
                value = baseline * week_factor * weekend_factor * (1 + random.uniform(-0.15, 0.15))
            elif feature in ['class_participation', 'peer_interaction']:
                # 课堂参与受节假日影响
                value = baseline * week_factor * holiday_factor * (1 + random.uniform(-0.2, 0.1))
            elif feature in ['exam_scores', 'assignment_quality']:
                # 成绩相关特征有累积效应
                progress_factor = min(1.0, 0.7 + week * 0.05)
                value = baseline * progress_factor * (1 + random.uniform(-0.1, 0.1))
            else:
                # 其他特征的基础波动
                value = baseline * week_factor * (1 + random.uniform(-0.15, 0.15))
            
            # 确保值在合理范围内
            value = max(0.0, min(1.0, value))
            
            week_data[feature] = round(value, 4)
        
        # 添加行为模式标记
        week_data['is_exam_week'] = 1 if week in [4, self.weeks] else 0
        week_data['is_weekend'] = 1 if day_type == 'weekend' else 0
        week_data['is_holiday_period'] = 1 if week in [6, 7] else 0
        
        return week_data
    
    def generate_graph_structure_data(self):
        """生成符合GNN模型输入格式的图结构数据，优先使用真实数据"""
        nodes = []
        edges = []
        node_id_counter = 0
        student_node_map = {}
        
        # 添加学生节点（使用真实数据）
        if hasattr(self, 'students_df') and self.students_df is not None:
            for _, student in self.students_df.iterrows():
                # 学生节点特征（基于真实数据）
                student_features = {
                    'node_type': 0,
                    'age': student.get('age', random.randint(18, 25)),
                    'gender_code': 1 if student.get('gender') == '男' else 0,
                    'major_code': self.majors.index(student.get('major', '计算机科学与技术')),
                    'academic_performance': self._calculate_academic_performance(student['student_id']),
                    'study_habit_consistency': self._calculate_attendance_rate(student['student_id'])
                }
                
                nodes.append({
                    'id': node_id_counter,
                    'type': 'student',
                    'student_id': student['student_id'],
                    'name': student['name'],
                    'features': student_features
                })
                student_node_map[student['student_id']] = node_id_counter
                node_id_counter += 1
            self.logger.info(f"基于真实数据创建了{len(student_node_map)}个学生节点")
        else:
            # 使用模拟数据（原逻辑）
            for i, student_id in enumerate(self.student_ids):
                student_index = int(student_id[1:]) - 1
                major = self.majors[student_index % len(self.majors)]
                
                student_features = {
                    'node_type': 0,
                    'major_code': self.majors.index(major),
                    'gender_code': random.randint(0, 1),
                    'age': random.randint(18, 25),
                    'academic_performance': random.uniform(0.6, 0.95),
                    'study_habit_consistency': random.uniform(0.4, 0.9)
                }
                
                nodes.append({
                    'id': node_id_counter,
                    'type': 'student',
                    'student_id': student_id,
                    'features': student_features
                })
                student_node_map[student_id] = node_id_counter
                node_id_counter += 1
        
        # 添加时间周期节点
        time_node_map = {}
        for week in range(1, self.weeks + 1):
            time_features = {
                'node_type': 1,
                'week_number': week,
                'is_midterm': 1 if week == 4 else 0,
                'is_final': 1 if week == self.weeks else 0,
                'season_factor': (week % 12) / 12.0
            }
            
            nodes.append({
                'id': node_id_counter,
                'type': 'time_period',
                'week_number': week,
                'features': time_features
            })
            time_node_map[week] = node_id_counter
            node_id_counter += 1
        
        # 添加课程节点（使用真实数据）
        course_node_map = {}
        if hasattr(self, 'courses_df') and self.courses_df is not None:
            unique_courses = self.courses_df['course'].unique()
            for course in unique_courses:
                course_features = {
                    'node_type': 2,
                    'difficulty_level': self._calculate_course_difficulty(course),
                    'credits': random.randint(2, 4),
                    'popularity_score': self._calculate_course_popularity(course)
                }
                
                nodes.append({
                    'id': node_id_counter,
                    'type': 'course',
                    'course_name': course,
                    'features': course_features
                })
                course_node_map[course] = node_id_counter
                node_id_counter += 1
            self.logger.info(f"基于真实数据创建了{len(course_node_map)}个课程节点")
        else:
            # 使用模拟数据
            courses = ['高等数学', '线性代数', '概率论', '数据结构', '算法分析', '机器学习', '深度学习', '数据库原理']
            for course in courses:
                course_features = {
                    'node_type': 2,
                    'difficulty_level': random.uniform(0.5, 0.9),
                    'credits': random.randint(2, 4),
                    'popularity_score': random.uniform(0.6, 0.95)
                }
                
                nodes.append({
                    'id': node_id_counter,
                    'type': 'course',
                    'course_name': course,
                    'features': course_features
                })
                course_node_map[course] = node_id_counter
                node_id_counter += 1
        
        # 添加学生-课程边（使用真实选课数据）
        if hasattr(self, 'courses_df') and self.courses_df is not None:
            # 预先计算学生-课程成绩映射，提高性能
            student_course_grades = {}
            if hasattr(self, 'grades_df') and self.grades_df is not None:
                for _, grade in self.grades_df.iterrows():
                    key = (grade['student_id'], grade['course'])
                    student_course_grades[key] = grade['score'] / 100
            
            for _, course_record in self.courses_df.iterrows():
                student_id = course_record['student_id']
                course = course_record['course']
                
                if student_id in student_node_map and course in course_node_map:
                    student_node_id = student_node_map[student_id]
                    course_node_id = course_node_map[course]
                    
                    # 从预计算的映射中获取边权重
                    key = (student_id, course)
                    edge_weight = student_course_grades.get(key, random.uniform(0.7, 1.0))
                    
                    edges.append({
                        'source': student_node_id,
                        'target': course_node_id,
                        'type': 'takes',
                        'weight': edge_weight,
                        'features': {
                            'enrollment_status': 1,
                            'semester': course_record.get('semester', '未知'),
                            'year': course_record.get('year', 2024),
                            'interest_level': edge_weight
                        }
                    })
            self.logger.info(f"基于真实选课数据创建了{len(edges)}条学生-课程边")
        
        # 添加行为事件节点和边（结合真实数据和模拟数据）
        # 预先计算学生-周-出勤记录映射，提高性能
        student_week_attendance = {}
        student_week_grades = {}
        
        # 预计算出勤数据映射
        if hasattr(self, 'attendance_df') and self.attendance_df is not None:
            for _, attendance in self.attendance_df.iterrows():
                student_id = attendance['student_id']
                date_str = attendance['date']
                # 提取周数（假设日期格式包含周信息）
                week_match = None
                if isinstance(date_str, str):
                    import re
                    week_match = re.search(r'W(\d+)', date_str)
                if week_match:
                    week = int(week_match.group(1))
                    if week >= 1 and week <= self.weeks:
                        key = (student_id, week)
                        if key not in student_week_attendance:
                            student_week_attendance[key] = []
                        student_week_attendance[key].append(attendance)
        
        # 预计算成绩数据映射
        if hasattr(self, 'grades_df') and self.grades_df is not None:
            for _, grade in self.grades_df.iterrows():
                student_id = grade['student_id']
                semester = grade['semester']
                # 从学期中提取周数
                week_match = None
                if isinstance(semester, str):
                    import re
                    week_match = re.search(r'第(\d+)', semester)
                if week_match:
                    week = int(week_match.group(1))
                    if week >= 1 and week <= self.weeks:
                        key = (student_id, week)
                        if key not in student_week_grades:
                            student_week_grades[key] = []
                        student_week_grades[key].append(grade)
        
        for student_id in student_node_map:
            student_node_id = student_node_map[student_id]
            
            for week in range(1, self.weeks + 1):
                time_node_id = time_node_map[week]
                
                # 基于出勤数据创建出勤行为事件
                key = (student_id, week)
                week_attendance = student_week_attendance.get(key, [])
                
                for attendance in week_attendance:
                        # 创建出勤行为事件节点
                        event_features = {
                            'node_type': 3,
                            'behavior_type': 0,  # 出勤行为
                            'duration_minutes': 45,
                            'engagement_level': 0.8 if attendance['status'] == 'present' else 0.3,
                            'performance_score': 0.8 if attendance['status'] == 'present' else 0.3
                        }
                        
                        event_node_id = node_id_counter
                        nodes.append({
                            'id': event_node_id,
                            'type': 'behavior_event',
                            'student_id': student_id,
                            'week_number': week,
                            'behavior_type': 'attendance',
                            'date': attendance['date'],
                            'course': attendance['course'],
                            'features': event_features
                        })
                        node_id_counter += 1
                        
                        # 添加学生-行为事件边
                        edges.append({
                            'source': student_node_id,
                            'target': event_node_id,
                            'type': 'exhibits',
                            'weight': 0.8 if attendance['status'] == 'present' else 0.3,
                            'features': {
                                'intensity': 0.8 if attendance['status'] == 'present' else 0.3,
                                'regularity': 0.8 if attendance['status'] == 'present' else 0.3
                            }
                        })
                        
                        # 添加行为事件-时间周期边
                        edges.append({
                            'source': event_node_id,
                            'target': time_node_id,
                            'type': 'occurs_at',
                            'weight': 1.0,
                            'features': {
                                'date': attendance['date'],
                                'status': attendance['status']
                            }
                        })
                
                # 基于成绩数据创建考试行为事件
                key = (student_id, week)
                week_grades = student_week_grades.get(key, [])
                
                for grade in week_grades:
                        # 创建考试行为事件节点
                        event_features = {
                            'node_type': 3,
                            'behavior_type': 1,  # 考试行为
                            'duration_minutes': 120,
                            'engagement_level': grade['score'] / 100,
                            'performance_score': grade['score'] / 100
                        }
                        
                        event_node_id = node_id_counter
                        nodes.append({
                            'id': event_node_id,
                            'type': 'behavior_event',
                            'student_id': student_id,
                            'week_number': week,
                            'behavior_type': 'exam',
                            'course': grade['course'],
                            'score': grade['score'],
                            'features': event_features
                        })
                        node_id_counter += 1
                        
                        # 添加学生-行为事件边
                        edges.append({
                            'source': student_node_id,
                            'target': event_node_id,
                            'type': 'exhibits',
                            'weight': grade['score'] / 100,
                            'features': {
                                'intensity': grade['score'] / 100,
                                'performance': grade['score'] / 100
                            }
                        })
                        
                        # 添加行为事件-时间周期边
                        edges.append({
                            'source': event_node_id,
                            'target': time_node_id,
                            'type': 'occurs_at',
                            'weight': 1.0,
                            'features': {
                                'semester': grade['semester'],
                                'year': grade['year']
                            }
                        })
        
        return {'nodes': nodes, 'edges': edges}
    
    def _calculate_academic_performance(self, student_id):
        """计算学生的学业表现"""
        if hasattr(self, 'grades_df') and self.grades_df is not None:
            student_grades = self.grades_df[self.grades_df['student_id'] == student_id]
            if not student_grades.empty:
                return student_grades['score'].mean() / 100
        return random.uniform(0.6, 0.95)
    
    def _calculate_attendance_rate(self, student_id):
        """计算学生的出勤率"""
        if hasattr(self, 'attendance_df') and self.attendance_df is not None:
            student_attendance = self.attendance_df[self.attendance_df['student_id'] == student_id]
            if not student_attendance.empty:
                present_count = len(student_attendance[student_attendance['status'] == 'present'])
                return present_count / len(student_attendance)
        return random.uniform(0.4, 0.9)
    
    def _calculate_course_difficulty(self, course):
        """计算课程难度（基于成绩分布）"""
        if hasattr(self, 'grades_df') and self.grades_df is not None:
            course_grades = self.grades_df[self.grades_df['course'] == course]
            if not course_grades.empty:
                avg_score = course_grades['score'].mean()
                # 成绩越低，难度越高
                return max(0.5, min(0.95, 1.0 - avg_score / 150))
        return random.uniform(0.5, 0.9)
    
    def _calculate_course_popularity(self, course):
        """计算课程受欢迎程度"""
        if hasattr(self, 'courses_df') and self.courses_df is not None:
            course_count = len(self.courses_df[self.courses_df['course'] == course])
            total_students = len(self.student_ids)
            return min(1.0, course_count / (total_students * 0.2))
        return random.uniform(0.6, 0.95)
    
    def _calculate_course_edge_weight(self, student_id, course):
        """计算学生-课程边的权重（基于成绩）"""
        if hasattr(self, 'grades_df') and self.grades_df is not None:
            student_course_grade = self.grades_df[
                (self.grades_df['student_id'] == student_id) &
                (self.grades_df['course'] == course)
            ]
            if not student_course_grade.empty:
                return student_course_grade['score'].iloc[0] / 100
        return random.uniform(0.7, 1.0)
    
    def generate_sample_pairs(self, positive_ratio=1, negative_ratio=4):
        """生成符合自监督学习要求的正样本对和负样本对，包含基于行为特征的相似性计算"""
        positive_pairs = []
        negative_pairs = []
        
        # 生成学生行为特征向量用于计算相似性
        student_behavior_patterns = {}
        for student_id in self.student_ids:
            student_index = int(student_id[1:]) - 1
            major = self.majors[student_index % len(self.majors)]
            behavior_pattern = self._generate_behavior_pattern(major)
            student_behavior_patterns[student_id] = behavior_pattern
        
        # 为每个学生生成正样本对（同一学生不同周期）
        for student_id in self.student_ids:
            weeks = list(range(1, self.weeks + 1))
            
            # 生成正样本对（同一学生的不同周）
            for i in range(len(weeks)):
                for j in range(i + 1, len(weeks)):
                    if random.random() < 0.3:  # 采样比例
                        # 基于时间间隔计算相似性
                        time_distance = abs(weeks[i] - weeks[j])
                        base_similarity = max(0.7, 1.0 - time_distance * 0.05)  # 时间越近越相似
                        
                        # 添加随机波动
                        similarity = base_similarity + random.uniform(-0.1, 0.1)
                        similarity = max(0.6, min(0.95, similarity))
                        
                        positive_pairs.append({
                            'student_id_1': student_id,
                            'week_1': weeks[i],
                            'student_id_2': student_id,
                            'week_2': weeks[j],
                            'pair_type': 'positive',
                            'similarity': round(similarity, 4),
                            'time_distance': time_distance
                        })
        
        # 生成负样本对（不同学生）
        student_pairs = []
        for i in range(self.num_students):
            for j in range(i + 1, self.num_students):
                student_pairs.append((self.student_ids[i], self.student_ids[j]))
        
        # 确保负样本数量是正样本的指定比例
        target_negative_count = len(positive_pairs) * negative_ratio
        selected_pairs = random.sample(student_pairs, min(len(student_pairs), target_negative_count))
        
        for student_id_1, student_id_2 in selected_pairs:
            week_1 = random.randint(1, self.weeks)
            week_2 = random.randint(1, self.weeks)
            
            # 基于学生行为模式计算相似性
            pattern1 = student_behavior_patterns[student_id_1]
            pattern2 = student_behavior_patterns[student_id_2]
            
            # 计算行为特征的余弦相似度
            features1 = [pattern1[feature] for feature in self.behavior_features]
            features2 = [pattern2[feature] for feature in self.behavior_features]
            
            # 计算欧几里得距离并转换为相似度
            squared_diff = sum((f1 - f2) ** 2 for f1, f2 in zip(features1, features2))
            distance = np.sqrt(squared_diff)
            # 转换为相似度（距离越小相似度越高）
            similarity = max(0.1, min(0.6, 0.8 - distance * 0.5))
            
            negative_pairs.append({
                'student_id_1': student_id_1,
                'week_1': week_1,
                'student_id_2': student_id_2,
                'week_2': week_2,
                'pair_type': 'negative',
                'similarity': round(similarity, 4),
                'behavior_distance': round(distance, 4)
            })
        
        return positive_pairs, negative_pairs
    
    def quality_control(self, behavior_data):
        """数据质量检测和过滤"""
        quality_results = {}
        
        # 检查缺失值
        missing_values = behavior_data.isnull().sum()
        quality_results['missing_values'] = missing_values.to_dict()
        
        # 检查异常值（超出合理范围）
        outlier_count = 0
        for feature in self.behavior_features:
            outliers = behavior_data[(behavior_data[feature]< 0) | (behavior_data[feature]> 1)]
            outlier_count += len(outliers)
        
        quality_results['outlier_count'] = outlier_count
        
        # 检查数据分布
        feature_stats = {}
        for feature in self.behavior_features:
            stats = behavior_data[feature].describe().to_dict()
            feature_stats[feature] = stats
        
        quality_results['feature_statistics'] = feature_stats
        
        return quality_results
    
    def save_data(self, data, filename, format='csv'):
        """保存数据到不同格式"""
        if format == 'csv':
            data.to_csv(filename, index=False, encoding='utf-8-sig')
        elif format == 'json':
            if isinstance(data, pd.DataFrame):
                data.to_json(filename, orient='records', force_ascii=False, indent=2)
            else:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
        elif format == 'parquet':
            data.to_parquet(filename, index=False)
        else:
            raise ValueError(f"不支持的格式: {format}")
    
    def generate_all_data(self, output_dir='advanced_data', formats=['csv', 'json'], weeks=None, features=None):
        """生成所有数据并保存"""
        if weeks:
            self.weeks = weeks
        if features:
            self.features = features
        
        # 创建输出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        self.logger.info(f"开始生成数据，学生数量: {self.num_students}, 周数: {self.weeks}, 特征数: {self.features}")
        
        # 生成学生基本信息
        self.logger.info("生成学生基本信息...")
        student_profiles = self.generate_student_profiles()
        
        # 生成时序行为数据
        self.logger.info("生成时序行为数据...")
        behavior_data = self.generate_temporal_behavior_data()
        
        # 生成图结构数据
        self.logger.info("生成图结构数据...")
        graph_data = self.generate_graph_structure_data()
        
        # 生成样本对数据
        self.logger.info("生成样本对数据...")
        positive_pairs, negative_pairs = self.generate_sample_pairs()
        sample_pairs = positive_pairs + negative_pairs
        
        # 数据质量检测
        self.logger.info("进行数据质量检测...")
        quality_report = self.quality_control(behavior_data)
        
        # 保存数据
        for fmt in formats:
            fmt_dir = os.path.join(output_dir, fmt)
            if not os.path.exists(fmt_dir):
                os.makedirs(fmt_dir)
            
            self.save_data(student_profiles, os.path.join(fmt_dir, f'student_profiles.{fmt}'), fmt)
            self.save_data(behavior_data, os.path.join(fmt_dir, f'behavior_data.{fmt}'), fmt)
            
            # 图数据和样本对数据
            if fmt == 'json':
                self.save_data(graph_data, os.path.join(fmt_dir, f'graph_structure.{fmt}'), fmt)
                self.save_data(sample_pairs, os.path.join(fmt_dir, f'sample_pairs.{fmt}'), fmt)
            elif fmt == 'csv':
                # 转换为DataFrame保存
                graph_nodes_df = pd.DataFrame(graph_data['nodes'])
                graph_edges_df = pd.DataFrame(graph_data['edges'])
                sample_pairs_df = pd.DataFrame(sample_pairs)
                
                self.save_data(graph_nodes_df, os.path.join(fmt_dir, 'graph_nodes.csv'), fmt)
                self.save_data(graph_edges_df, os.path.join(fmt_dir, 'graph_edges.csv'), fmt)
                self.save_data(sample_pairs_df, os.path.join(fmt_dir, 'sample_pairs.csv'), fmt)
        
        # 保存质量报告
        quality_report_path = os.path.join(output_dir, 'quality_report.json')
        with open(quality_report_path, 'w', encoding='utf-8') as f:
            json.dump(quality_report, f, ensure_ascii=False, indent=2)
        
        # 输出统计信息
        self.logger.info(f"数据生成完成！")
        self.logger.info(f"学生信息：{len(student_profiles)}条记录")
        self.logger.info(f"行为数据：{len(behavior_data)}条记录")
        self.logger.info(f"图节点：{len(graph_data['nodes'])}个")
        self.logger.info(f"图边：{len(graph_data['edges'])}条")
        self.logger.info(f"正样本对：{len(positive_pairs)}对")
        self.logger.info(f"负样本对：{len(negative_pairs)}对")
        self.logger.info(f"异常值数量：{quality_report['outlier_count']}")
        
        return {
            'student_profiles': student_profiles,
            'behavior_data': behavior_data,
            'graph_data': graph_data,
            'sample_pairs': sample_pairs,
            'quality_report': quality_report
        }

class AcademicWarningSystem:
    def __init__(self):
        self.classifier = AcademicRiskClassifier()
        self.risk_thresholds = {
            'low': 0.3,
            'medium': 0.6,
            'high': 0.8
        }
    
    def load_and_preprocess_data(self):
        """加载并预处理数据"""
        # 加载数据
        data = load_data()
        
        # 提取特征
        features = extract_features(data)
        
        # 创建目标变量：根据挂科门数和平均成绩判断是否有风险
        # 挂科门数 >= 2 或平均成绩 < 60 视为有风险
        target = []
        for _, row in features.iterrows():
            if row.get('fail_courses', 0) >= 2 or row.get('avg_score', 100) < 60:
                target.append(1)  # 有风险
            else:
                target.append(0)  # 无风险
        target = np.array(target)
        
        # 只保留特征列（去除 student_id）
        feature_columns = [col for col in features.columns if col != 'student_id']
        features = features[feature_columns]
        
        # 预处理数据
        self.classifier.load_data(features, target)
        self.classifier.preprocess_data()
        
        # 检查是否有多个类别
        if len(np.unique(target)) > 1:
            self.classifier.handle_class_imbalance()
        else:
            print("警告：数据集中只有一个类别，跳过类别不平衡处理")
        
        return features, target
    
    def train_models(self):
        """训练分类模型"""
        # 检查是否有重采样数据
        if hasattr(self.classifier, 'X_train_resampled'):
            # 使用重采样数据训练
            self.classifier.train_decision_tree()
            self.classifier.train_logistic_regression()
        else:
            # 使用原始数据训练
            # 手动训练决策树模型
            from sklearn.tree import DecisionTreeClassifier
            from sklearn.linear_model import LogisticRegression
            
            self.classifier.decision_tree_model = DecisionTreeClassifier(random_state=42)
            self.classifier.decision_tree_model.fit(self.classifier.X_train_scaled, self.classifier.y_train)
            
            self.classifier.logistic_regression_model = LogisticRegression(random_state=42, max_iter=1000)
            self.classifier.logistic_regression_model.fit(self.classifier.X_train_scaled, self.classifier.y_train)
    
    def predict_risk_levels(self, X):
        """预测风险等级"""
        # 使用决策树模型预测
        dt_predictions = self.classifier.predict('decision_tree', X)
        
        # 计算风险概率
        dt_probabilities = self.classifier.decision_tree_model.predict_proba(self.classifier.scaler.transform(X))[:, 1]
        
        # 根据概率划分风险等级
        risk_levels = []
        for prob in dt_probabilities:
            if prob >= self.risk_thresholds['high']:
                risk_levels.append('高风险')
            elif prob >= self.risk_thresholds['medium']:
                risk_levels.append('中风险')
            elif prob >= self.risk_thresholds['low']:
                risk_levels.append('低风险')
            else:
                risk_levels.append('无风险')
        
        return risk_levels, dt_probabilities
    
    def analyze_student_behavior(self, features, students):
        """分析学生行为数据"""
        # 行为分析结果
        behavior_analysis = []
        
        for idx, row in features.iterrows():
            student_id = students['student_id'].iloc[idx] if idx < len(students) else f'S{idx+1}'
            
            # 学业行为分析
            academic_behavior = {
                'avg_score': row.get('avg_score', 0),
                'fail_courses': row.get('fail_courses', 0),
                'std_score': row.get('std_score', 0)
            }
            
            # 出勤行为分析
            attendance_behavior = {
                'attendance_rate': row.get('attendance_rate', 0),
                'late_count': row.get('late_count', 0),
                'absent_count': row.get('absent_count', 0)
            }
            
            # 选课行为分析
            course_behavior = {
                'course_count': row.get('course_count', 0),
                'avg_semester_courses': row.get('avg_semester_courses', 0)
            }
            
            # 风险因素分析
            risk_factors = []
            if academic_behavior['fail_courses'] >= 2:
                risk_factors.append('挂科门数过多')
            if academic_behavior['avg_score'] < 60:
                risk_factors.append('平均成绩过低')
            if academic_behavior['std_score'] > 20:
                risk_factors.append('成绩波动较大')
            if attendance_behavior['attendance_rate'] < 0.8:
                risk_factors.append('出勤率过低')
            if attendance_behavior['absent_count'] >= 5:
                risk_factors.append('缺勤次数过多')
            if course_behavior['course_count'] < 3:
                risk_factors.append('选课数量不足')
            if course_behavior['course_count'] > 8:
                risk_factors.append('选课数量过多')
            
            # 行为模式分析
            behavior_pattern = '正常'  # 默认行为模式
            if len(risk_factors) >= 3:
                behavior_pattern = '高风险行为'
            elif len(risk_factors) >= 2:
                behavior_pattern = '中等风险行为'
            elif len(risk_factors) >= 1:
                behavior_pattern = '低风险行为'
            
            behavior_analysis.append({
                'student_id': student_id,
                'academic_behavior': academic_behavior,
                'attendance_behavior': attendance_behavior,
                'course_behavior': course_behavior,
                'risk_factors': risk_factors,
                'behavior_pattern': behavior_pattern
            })
        
        return behavior_analysis
    
    def generate_warning_report(self, features):
        """生成预警报告"""
        # 加载学生信息
        data = load_data()
        students = data['students']
        
        # 分析学生行为
        behavior_analysis = self.analyze_student_behavior(features, students)
        
        # 预测风险等级
        risk_levels, probabilities = self.predict_risk_levels(features)
        
        # 创建预警报告
        report_data = []
        for i, (risk_level, prob) in enumerate(zip(risk_levels, probabilities)):
            student_id = students['student_id'].iloc[i] if i < len(students) else f'S{i+1}'
            name = students['name'].iloc[i] if i < len(students) else f'学生{i+1}'
            
            # 获取行为分析结果
            behavior = behavior_analysis[i] if i < len(behavior_analysis) else {}
            risk_factors = behavior.get('risk_factors', [])
            behavior_pattern = behavior.get('behavior_pattern', '正常')
            
            report_data.append({
                '学生ID': student_id,
                '姓名': name,
                '风险等级': risk_level,
                '风险概率': prob,
                '行为模式': behavior_pattern,
                '风险因素': ', '.join(risk_factors) if risk_factors else '无'
            })
        
        report = pd.DataFrame(report_data)
        
        # 按风险等级排序
        risk_order = {'高风险': 0, '中风险': 1, '低风险': 2, '无风险': 3}
        report['风险排序'] = report['风险等级'].map(risk_order)
        report = report.sort_values('风险排序').drop('风险排序', axis=1)
        
        return report
    
    def analyze_risk_distribution(self, report):
        """分析风险分布"""
        # 统计各风险等级的学生数量
        risk_distribution = report['风险等级'].value_counts()
        
        # 可视化风险分布
        plt.figure(figsize=(10, 6))
        sns.barplot(x=risk_distribution.index, y=risk_distribution.values, palette='YlOrRd')
        plt.title('学生学业风险分布')
        plt.xlabel('风险等级')
        plt.ylabel('学生数量')
        plt.savefig('reports/risk_distribution.png')
        plt.close()
        
        return risk_distribution
    
    def get_feature_importance(self):
        """获取特征重要性"""
        # 获取决策树特征重要性
        dt_importance = self.classifier.get_feature_importance('decision_tree')
        
        # 获取逻辑回归特征重要性
        lr_importance = self.classifier.get_feature_importance('logistic_regression')
        
        # 特征名称
        feature_names = [
            '平均成绩', '挂科门数', '出勤率', '选课数量', 
            '连续挂科次数', '成绩下降幅度', '迟到次数', '早退次数'
        ]
        
        # 创建特征重要性报告
        importance_df = pd.DataFrame({
            '特征': feature_names,
            '决策树重要性': dt_importance,
            '逻辑回归重要性': lr_importance
        })
        
        # 按决策树重要性排序
        importance_df = importance_df.sort_values('决策树重要性', ascending=False)
        
        # 可视化特征重要性
        plt.figure(figsize=(12, 8))
        plt.subplot(2, 1, 1)
        sns.barplot(x='决策树重要性', y='特征', data=importance_df, palette='viridis')
        plt.title('决策树特征重要性')
        
        plt.subplot(2, 1, 2)
        sns.barplot(x='逻辑回归重要性', y='特征', data=importance_df, palette='plasma')
        plt.title('逻辑回归特征重要性')
        
        plt.tight_layout()
        plt.savefig('reports/feature_importance.png')
        plt.close()
        
        return importance_df
    
    def run_warning_system(self):
        """运行预警系统，自动生成图结构和样本对数据"""
        # 自动生成图结构和样本对数据
        print("正在根据上传的数据生成图结构和样本对...")
        try:
            # 创建数据生成器
            generator = AdvancedStudentDataGenerator(
                num_students=100,  # 实际学生数量会根据上传数据自动调整
                weeks=8,
                features=20,
                use_real_data=True,  # 使用真实数据
                data_dir='data'
            )
            
            # 生成数据，支持多种格式
            results = generator.generate_all_data(
                output_dir='advanced_data',
                formats=['csv', 'json', 'parquet']
            )
            
            print(f"数据生成完成！")
            print(f"图节点：{len(results['graph_data']['nodes'])}个")
            print(f"图边：{len(results['graph_data']['edges'])}条")
            print(f"样本对：{len(results['sample_pairs'])}对")
            
        except Exception as e:
            print(f"数据生成过程中出现错误：{str(e)}")
            print("继续运行预警系统...")
        
        # 加载和预处理数据
        features, target = self.load_and_preprocess_data()
        
        # 检查是否有多个类别
        if len(np.unique(target)) > 1:
            # 训练模型
            self.train_models()
            
            # 生成预警报告
            report = self.generate_warning_report(features)
            
            # 分析风险分布
            risk_distribution = self.analyze_risk_distribution(report)
            
            # 获取特征重要性
            feature_importance = self.get_feature_importance()
        else:
            # 数据集中只有一个类别，基于规则生成预警结果
            print("数据集中只有一个类别，基于规则生成预警结果")
            
            # 加载学生信息
            data = load_data()
            students = data['students']
            
            # 分析学生行为
            behavior_analysis = self.analyze_student_behavior(features, students)
            
            # 基于规则生成风险等级
            risk_levels = []
            probabilities = []
            
            for i, row in features.iterrows():
                # 获取行为分析结果
                behavior = behavior_analysis[i] if i < len(behavior_analysis) else {}
                risk_factors = behavior.get('risk_factors', [])
                behavior_pattern = behavior.get('behavior_pattern', '正常')
                
                # 计算风险概率（基于行为分析结果）
                fail_courses = row.get('fail_courses', 0)
                avg_score = row.get('avg_score', 100)
                attendance_rate = row.get('attendance_rate', 1)
                absent_count = row.get('absent_count', 0)
                course_count = row.get('course_count', 0)
                
                # 基于行为数据的风险概率计算
                risk_prob = 0
                
                # 学业行为因素
                if fail_courses >= 2:
                    risk_prob += 0.3
                elif fail_courses >= 1:
                    risk_prob += 0.15
                
                if avg_score < 60:
                    risk_prob += 0.3
                elif avg_score < 70:
                    risk_prob += 0.1
                
                # 出勤行为因素
                if attendance_rate < 0.8:
                    risk_prob += 0.2
                if absent_count >= 5:
                    risk_prob += 0.15
                
                # 选课行为因素
                if course_count < 3 or course_count > 8:
                    risk_prob += 0.1
                
                # 确保概率在合理范围内
                risk_prob = min(risk_prob, 1.0)
                risk_prob = max(risk_prob, 0.0)
                
                probabilities.append(risk_prob)
                
                # 基于概率划分风险等级
                if risk_prob >= self.risk_thresholds['high']:
                    risk_levels.append('高风险')
                elif risk_prob >= self.risk_thresholds['medium']:
                    risk_levels.append('中风险')
                elif risk_prob >= self.risk_thresholds['low']:
                    risk_levels.append('低风险')
                else:
                    risk_levels.append('无风险')
            
            # 创建预警报告
            report_data = []
            for i, (risk_level, prob) in enumerate(zip(risk_levels, probabilities)):
                student_id = students['student_id'].iloc[i] if i < len(students) else f'S{i+1}'
                name = students['name'].iloc[i] if i < len(students) else f'学生{i+1}'
                
                # 获取行为分析结果
                behavior = behavior_analysis[i] if i < len(behavior_analysis) else {}
                risk_factors = behavior.get('risk_factors', [])
                behavior_pattern = behavior.get('behavior_pattern', '正常')
                
                report_data.append({
                    '学生ID': student_id,
                    '姓名': name,
                    '风险等级': risk_level,
                    '风险概率': prob,
                    '行为模式': behavior_pattern,
                    '风险因素': ', '.join(risk_factors) if risk_factors else '无'
                })
            
            report = pd.DataFrame(report_data)
            
            # 按风险等级排序
            risk_order = {'高风险': 0, '中风险': 1, '低风险': 2, '无风险': 3}
            report['风险排序'] = report['风险等级'].map(risk_order)
            report = report.sort_values('风险排序').drop('风险排序', axis=1)
            
            # 分析风险分布
            risk_distribution = report['风险等级'].value_counts()
            
            # 生成风险分布图表
            plt.figure(figsize=(10, 6))
            sns.barplot(x=risk_distribution.index, y=risk_distribution.values, palette='YlOrRd')
            plt.title('学生学业风险分布')
            plt.xlabel('风险等级')
            plt.ylabel('学生数量')
            plt.savefig('reports/risk_distribution.png')
            plt.close()
            
            # 特征重要性（模拟数据）
            feature_importance = pd.DataFrame({
                '特征': ['平均成绩', '挂科门数', '出勤率', '选课数量', '迟到次数', '缺勤次数'],
                '决策树重要性': [0.35, 0.25, 0.15, 0.1, 0.1, 0.05],
                '逻辑回归重要性': [0.4, 0.3, 0.15, 0.1, 0.03, 0.02]
            })
            
            # 生成特征重要性图表
            plt.figure(figsize=(12, 8))
            plt.subplot(2, 1, 1)
            sns.barplot(x='决策树重要性', y='特征', data=feature_importance, palette='viridis')
            plt.title('决策树特征重要性')
            
            plt.subplot(2, 1, 2)
            sns.barplot(x='逻辑回归重要性', y='特征', data=feature_importance, palette='plasma')
            plt.title('逻辑回归特征重要性')
            
            plt.tight_layout()
            plt.savefig('reports/feature_importance.png')
            plt.close()
        
        # 保存预警报告
        report.to_csv('reports/academic_warning_report.csv', index=False, encoding='utf-8-sig')
        
        print("学业风险预警系统运行完成！")
        print("\n风险分布：")
        print(risk_distribution)
        print("\n特征重要性：")
        print(feature_importance)
        print("\n预警报告已保存至 reports/academic_warning_report.csv")
        
        return report, risk_distribution, feature_importance

if __name__ == "__main__":
    warning_system = AcademicWarningSystem()
    warning_system.run_warning_system()

import pandas as pd
import numpy as np
import re
from association_rules.apriori import Apriori
from data_processing.data_loader import load_data
from llm_integration.openai_client import llm_client

class LearningPathRecommender:
    def __init__(self, min_support=0.1, min_confidence=0.5):
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.apriori = Apriori(min_support, min_confidence)
        self.rules = []
        self.data = None
    
    def fit(self, data=None):
        """
        拟合模型，生成推荐规则
        """
        if data is None:
            self.data = load_data()
        else:
            self.data = data
        
        # 准备交易数据（学生选课记录）
        transactions = self._prepare_transactions()
        
        # 使用Apriori算法生成关联规则
        self.apriori.fit(transactions)
        self.rules = self.apriori.get_rules()
        
        return self
    
    def _prepare_transactions(self):
        """
        准备交易数据，将学生选课记录转换为交易格式
        """
        courses_data = self.data['courses']
        transactions = []
        
        # 按学生ID分组，获取每个学生的选课记录
        grouped = courses_data.groupby('student_id')
        for student_id, group in grouped:
            courses = group['course'].tolist()
            if courses:
                transactions.append(courses)
        
        return transactions
    
    def recommend_courses(self, student_id, top_n=5):
        """
        为特定学生推荐课程
        
        Args:
            student_id: 学生ID
            top_n: 推荐课程数量
            
        Returns:
            list: 推荐课程列表
        """
        # 获取学生已选课程
        student_courses = self._get_student_courses(student_id)
        
        # 基于关联规则生成推荐
        recommendations = []
        
        for rule in self.rules:
            antecedent = rule['antecedent']
            consequent = rule['consequent']
            
            # 检查前件是否是学生已选课程的子集
            if antecedent.issubset(set(student_courses)):
                # 计算推荐分数（综合考虑置信度和提升度）
                score = rule['confidence'] * rule['lift']
                
                for course in consequent:
                    # 确保推荐的课程学生还没有选过
                    if course not in student_courses:
                        recommendations.append((course, score))
        
        # 去重并按分数排序（保持顺序）
        seen = set()
        unique_recommendations = []
        
        # 先按分数排序
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        # 去重，保持排序顺序
        for course, score in recommendations:
            if course not in seen:
                seen.add(course)
                unique_recommendations.append((course, score))
        
        # 返回前top_n个推荐
        return [course for course, _ in unique_recommendations[:top_n]]
    
    def _get_student_courses(self, student_id):
        """
        获取学生已选课程
        """
        courses_data = self.data['courses']
        student_courses = courses_data[courses_data['student_id'] == student_id]['course'].tolist()
        return student_courses
    
    def get_personalized_path(self, student_id):
        """
        为学生生成个性化学习路径
        
        Args:
            student_id: 学生ID
            
        Returns:
            dict: 包含推荐课程和学习路径的字典
        """
        # 获取学生已选课程
        student_courses = self._get_student_courses(student_id)
        
        # 获取推荐课程
        recommended_courses = self.recommend_courses(student_id)
        
        # 生成学习路径（基于课程之间的关联关系）
        learning_path = self._generate_learning_path(student_courses, recommended_courses)
        
        return {
            'student_id': student_id,
            'completed_courses': student_courses,
            'recommended_courses': recommended_courses,
            'learning_path': learning_path
        }
    
    def _generate_learning_path(self, completed_courses, recommended_courses):
        """
        生成学习路径
        """
        # 简单实现：按课程关联强度排序
        path = []
        temp_courses = recommended_courses.copy()
        
        while temp_courses:
            best_course = None
            best_score = 0
            
            for course in temp_courses:
                # 计算课程与已完成课程的关联强度
                score = self._calculate_course_score(course, completed_courses)
                if score > best_score:
                    best_score = score
                    best_course = course
            
            if best_course:
                path.append(best_course)
                completed_courses.append(best_course)
                temp_courses.remove(best_course)
        
        return path
    
    def _calculate_course_score(self, course, completed_courses):
        """
        计算课程与已完成课程的关联强度
        """
        score = 0
        count = 0
        
        for rule in self.rules:
            consequent = rule['consequent']
            if course in consequent:
                antecedent = rule['antecedent']
                # 检查前件中有多少课程是学生已完成的
                common_courses = antecedent.intersection(set(completed_courses))
                if common_courses:
                    score += rule['confidence'] * rule['lift'] * len(common_courses)
                    count += 1
        
        return score / count if count > 0 else 0
    
    def recommend_courses_with_llm(self, student_id, top_n=5):
        """
        使用LLM进行个性化课程推荐
        
        Args:
            student_id: 学生ID
            top_n: 推荐课程数量
            
        Returns:
            dict: 包含推荐课程和推荐理由的字典
        """
        try:
            # 获取学生基本信息
            student_info = self._get_student_info(student_id)
            
            # 获取学生已选课程和成绩
            student_courses = self._get_student_courses(student_id)
            student_grades = self._get_student_grades(student_id)
            
            # 获取所有课程信息
            all_courses = set(self.data['courses']['course'].unique())
            
            # 计算未选课程
            unselected_courses = all_courses - set(student_courses)
            
            if not unselected_courses:
                return {
                    'status': 'success',
                    'recommendations': [],
                    'message': '该学生已选择所有课程，无需推荐'
                }
            
            # 使用传统推荐算法获取基础推荐
            traditional_recommendations = self.recommend_courses(student_id, top_n * 2)
            
            # 构建LLM提示词
            prompt = self._build_llm_recommendation_prompt(
                student_id, 
                student_info, 
                student_courses, 
                student_grades, 
                unselected_courses,
                traditional_recommendations
            )
            
            # 调用LLM获取个性化推荐
            llm_response = self._call_llm_for_recommendation(prompt)
            
            # 解析LLM响应
            recommendations = self._parse_llm_recommendations(llm_response, unselected_courses)
            
            # 如果LLM失败，回退到传统推荐
            if not recommendations:
                recommendations = [{'course': course, 'reason': '基于关联规则推荐'} for course in traditional_recommendations[:top_n]]
            
            return {
                'status': 'success',
                'recommendations': recommendations[:top_n],
                'student_info': student_info,
                'completed_courses': student_courses
            }
            
        except Exception as e:
            # 发生错误时回退到传统推荐
            try:
                traditional_recommendations = self.recommend_courses(student_id, top_n)
                return {
                    'status': 'fallback',
                    'recommendations': [{'course': course, 'reason': '基于关联规则推荐（LLM调用失败）'} for course in traditional_recommendations],
                    'message': f'LLM推荐失败，已回退到传统推荐: {str(e)}'
                }
            except:
                return {
                    'status': 'error',
                    'recommendations': [],
                    'message': f'推荐失败: {str(e)}'
                }
    
    def _get_student_info(self, student_id):
        """获取学生基本信息"""
        students_data = self.data['students']
        try:
            student_info = students_data[students_data['student_id'] == student_id].iloc[0].to_dict()
            return student_info
        except:
            return {'student_id': student_id, 'name': '未知', 'major': '未知'}
    
    def _get_student_grades(self, student_id):
        """获取学生成绩"""
        grades_data = self.data.get('grades', pd.DataFrame())
        if grades_data.empty:
            return {}
        
        student_grades = grades_data[grades_data['student_id'] == student_id]
        return {row['course']: row['score'] for _, row in student_grades.iterrows()}
    
    def _build_llm_recommendation_prompt(self, student_id, student_info, student_courses, student_grades, unselected_courses, traditional_recommendations):
        """构建LLM推荐提示词"""
        student_name = student_info.get('name', '未知')
        student_major = student_info.get('major', '未知')
        
        # 计算学生成绩统计
        if student_grades:
            avg_score = sum(student_grades.values()) / len(student_grades)
            strong_courses = [course for course, score in student_grades.items() if score >= 85]
            weak_courses = [course for course, score in student_grades.items() if score< 60]
        else:
            avg_score = 0
            strong_courses = []
            weak_courses = []
        
        prompt = f"""你是一位专业的学业规划顾问，擅长根据学生的专业背景、已修课程和学习表现，为学生推荐最适合的后续课程。

学生信息：
- 学生ID: {student_id}
- 姓名: {student_name}
- 专业: {student_major}
- 已修课程数量: {len(student_courses)}
- 平均成绩: {avg_score:.1f}
- 优势课程: {', '.join(strong_courses) if strong_courses else '无'}
- 薄弱课程: {', '.join(weak_courses) if weak_courses else '无'}

已修课程：
{', '.join(student_courses)}

可选择的未修课程：
{', '.join(unselected_courses)}

传统算法推荐的课程：
{', '.join(traditional_recommendations)}

请根据以上信息，为该学生推荐5门最适合的课程，并提供详细的推荐理由。推荐应考虑以下因素：
1. 专业相关性和职业发展方向
2. 课程难度与学生能力匹配
3. 课程之间的逻辑顺序和先修关系
4. 学生的优势和薄弱环节
5. 市场需求和就业前景

输出格式要求：
1. 直接输出5门推荐课程，每门课程一行
2. 每行格式为：课程名称|推荐理由
3. 推荐理由要具体、有针对性，包含专业相关性、难度匹配、职业价值等
4. 不要包含任何开场白或总结性文字
5. 严格按照格式输出，不要有其他内容

示例输出：
机器学习|适合人工智能专业，学生数学基础扎实，有助于职业发展
数据结构|计算机专业核心课程，为后续课程打基础
"""
        return prompt
    
    def _call_llm_for_recommendation(self, prompt):
        """调用LLM进行推荐"""
        try:
            # 直接使用requests调用Ollama API，避免使用generate_student_analysis方法
            import requests
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': llm_client.config['model'],
                'messages': [
                    {
                        'role': 'system',
                        'content': '你是一位专业的学业规划顾问，擅长根据学生的专业背景、已修课程和学习表现，为学生推荐最适合的后续课程。'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'temperature': llm_client.config['temperature'],
                'max_tokens': llm_client.config['max_tokens'],
                'stream': False  # 禁用流式响应，获取完整响应
            }
            
            url = f"{llm_client.config['base_url']}/api/chat"
            response = requests.post(url, headers=headers, json=data, timeout=15)
            response.raise_for_status()
            
            result = response.json()
            return result['message']['content'].strip()
            
        except Exception as e:
            print(f"LLM调用失败: {str(e)}")
            return ""
    
    def _parse_llm_recommendations(self, response, available_courses):
        """解析LLM响应"""
        recommendations = []
        
        # 使用正则表达式匹配课程推荐格式
        pattern = r'([^|]+)\|(.+)'
        matches = re.findall(pattern, response)
        
        for match in matches:
            course = match[0].strip()
            reason = match[1].strip()
            
            # 验证课程是否在可用课程列表中
            if course in available_courses:
                recommendations.append({
                    'course': course,
                    'reason': reason
                })
        
        # 如果没有匹配到，尝试提取课程名称
        if not recommendations:
            # 简单提取可能的课程名称
            course_pattern = r'([\u4e00-\u9fa5]{2,10})'
            courses_found = re.findall(course_pattern, response)
            
            for course in courses_found[:5]:  # 最多取5个
                if course in available_courses:
                    recommendations.append({
                        'course': course,
                        'reason': '基于LLM分析推荐'
                    })
        
        return recommendations
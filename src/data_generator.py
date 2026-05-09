import pandas as pd
import numpy as np
import random
import os

class StudentDataGenerator:
    def __init__(self, num_students=1000):
        self.num_students = num_students
        self.student_ids = [f'S{i+1:04d}' for i in range(num_students)]
        self.names = self._generate_names()
        self.genders = ['男', '女']
        self.majors = ['计算机科学与技术', '电子工程', '软件工程', '数据科学', '人工智能', '信息安全', '网络工程', '物联网工程']
        # 扩充课程数据集，添加课程类别、难度和先修条件
        self.course_catalog = {
            # 基础课程（难度：低）
            '高等数学': {'category': '基础课程', 'level': '低', 'prerequisites': []},
            '大学物理': {'category': '基础课程', 'level': '低', 'prerequisites': ['高等数学']},
            '线性代数': {'category': '基础课程', 'level': '低', 'prerequisites': ['高等数学']},
            '概率论与数理统计': {'category': '基础课程', 'level': '低', 'prerequisites': ['高等数学']},
            
            # 专业基础课程（难度：中）
            '程序设计基础': {'category': '专业基础', 'level': '中', 'prerequisites': []},
            '离散数学': {'category': '专业基础', 'level': '中', 'prerequisites': ['高等数学']},
            '计算机组成原理': {'category': '专业基础', 'level': '中', 'prerequisites': ['大学物理']},
            
            # 核心课程（难度：高）
            '数据结构': {'category': '核心课程', 'level': '高', 'prerequisites': ['程序设计基础']},
            '算法设计与分析': {'category': '核心课程', 'level': '高', 'prerequisites': ['数据结构']},
            '操作系统': {'category': '核心课程', 'level': '高', 'prerequisites': ['计算机组成原理']},
            '计算机网络': {'category': '核心课程', 'level': '高', 'prerequisites': []},
            '数据库原理': {'category': '核心课程', 'level': '高', 'prerequisites': ['数据结构']},
            
            # 专业方向课程（难度：中高）
            '软件工程': {'category': '专业方向', 'level': '中高', 'prerequisites': ['数据结构', '操作系统']},
            '人工智能导论': {'category': '专业方向', 'level': '中高', 'prerequisites': ['数据结构', '概率论与数理统计']},
            '机器学习': {'category': '专业方向', 'level': '中高', 'prerequisites': ['人工智能导论', '概率论与数理统计']},
            '深度学习': {'category': '专业方向', 'level': '中高', 'prerequisites': ['机器学习']},
            '计算机视觉': {'category': '专业方向', 'level': '中高', 'prerequisites': ['机器学习']},
            '自然语言处理': {'category': '专业方向', 'level': '中高', 'prerequisites': ['机器学习']},
            '数据挖掘': {'category': '专业方向', 'level': '中高', 'prerequisites': ['数据库原理', '机器学习']},
            '云计算': {'category': '专业方向', 'level': '中高', 'prerequisites': ['计算机网络', '操作系统']},
            '大数据技术': {'category': '专业方向', 'level': '中高', 'prerequisites': ['数据库原理', '操作系统']},
            '信息安全': {'category': '专业方向', 'level': '中高', 'prerequisites': ['计算机网络', '操作系统']},
            '密码学基础': {'category': '专业方向', 'level': '中高', 'prerequisites': ['高等数学', '离散数学']},
            '嵌入式系统': {'category': '专业方向', 'level': '中高', 'prerequisites': ['计算机组成原理']},
            '物联网技术': {'category': '专业方向', 'level': '中高', 'prerequisites': ['计算机网络', '嵌入式系统']},
            
            # 前沿技术课程（难度：高）
            '区块链技术': {'category': '前沿技术', 'level': '高', 'prerequisites': ['计算机网络', '密码学基础']},
            '量子计算导论': {'category': '前沿技术', 'level': '高', 'prerequisites': ['线性代数', '概率论与数理统计']},
            '强化学习': {'category': '前沿技术', 'level': '高', 'prerequisites': ['机器学习']},
            '自动驾驶技术': {'category': '前沿技术', 'level': '高', 'prerequisites': ['计算机视觉', '机器学习']}
        }
        self.courses = list(self.course_catalog.keys())
        self.semesters = ['第一学期', '第二学期', '第三学期', '第四学期', '第五学期', '第六学期']
        self.years = [2023, 2024, 2025]
        
    def _generate_names(self):
        """生成随机姓名"""
        surnames = ['王', '李', '张', '刘', '陈', '杨', '赵', '黄', '周', '吴', '徐', '孙', '马', '朱', '胡', '郭', '何', '高', '林', '罗']
        given_names = ['伟', '芳', '娜', '敏', '静', '丽', '强', '磊', '军', '洋', '勇', '艳', '杰', '娟', '涛', '明', '超', '秀英', '霞', '平']
        names = []
        for _ in range(self.num_students):
            surname = random.choice(surnames)
            given_name = random.choice(given_names)
            names.append(f"{surname}{given_name}")
        return names
    
    def generate_students(self):
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
    
    def generate_grades(self):
        """生成成绩数据，与选课数据保持一致"""
        data = []
        
        # 先生成选课数据以获取每个学生的选课情况
        courses_df = self.generate_courses()
        
        for student_id in self.student_ids:
            # 获取该学生的所有选课记录
            student_courses = courses_df[courses_df['student_id'] == student_id]
            
            for _, course_row in student_courses.iterrows():
                course = course_row['course']
                semester = course_row['semester']
                year = course_row['year']
                
                # 根据课程难度设置不同的成绩分布
                course_level = self.course_catalog[course]['level']
                
                if course_level == '低':
                    # 基础课程成绩较好
                    if random.random()< 0.05:
                        score = random.randint(50, 65)
                    else:
                        score = random.randint(70, 95)
                elif course_level == '中':
                    # 中等难度课程
                    if random.random()< 0.1:
                        score = random.randint(45, 65)
                    else:
                        score = random.randint(65, 90)
                elif course_level == '中高':
                    # 中高难度课程
                    if random.random()< 0.15:
                        score = random.randint(40, 65)
                    else:
                        score = random.randint(60, 85)
                else:  # '高'
                    # 高难度课程
                    if random.random()< 0.2:
                        score = random.randint(35, 65)
                    else:
                        score = random.randint(55, 80)
                
                data.append([student_id, course, score, semester, year])
        
        df = pd.DataFrame(data, columns=['student_id', 'course', 'score', 'semester', 'year'])
        return df
    
    def generate_attendance(self):
        """生成出勤记录，与选课数据保持一致"""
        data = []
        statuses = ['present', 'absent', 'late']
        
        # 先生成选课数据以获取每个学生的选课情况
        courses_df = self.generate_courses()
        
        for student_id in self.student_ids:
            # 获取该学生的所有选课记录
            student_courses = courses_df[courses_df['student_id'] == student_id]['course'].unique()
            
            if len(student_courses) == 0:
                continue
            
            # 为每门课生成多次出勤记录
            for course in student_courses:
                # 每门课8-12次出勤记录
                class_count = random.randint(8, 12)
                
                for _ in range(class_count):
                    # 根据课程重要性和学生表现设置出勤概率
                    course_level = self.course_catalog[course]['level']
                    
                    if course_level == '低':
                        # 基础课程出勤率较高
                        if random.random()< 0.8:
                            status = 'present'
                        elif random.random()< 0.15:
                            status = 'late'
                        else:
                            status = 'absent'
                    elif course_level == '中':
                        # 中等难度课程
                        if random.random()< 0.75:
                            status = 'present'
                        elif random.random()< 0.15:
                            status = 'late'
                        else:
                            status = 'absent'
                    elif course_level == '中高':
                        # 中高难度课程
                        if random.random()< 0.7:
                            status = 'present'
                        elif random.random()< 0.15:
                            status = 'late'
                        else:
                            status = 'absent'
                    else:  # '高'
                        # 高难度课程出勤率可能较低
                        if random.random()< 0.65:
                            status = 'present'
                        elif random.random()< 0.15:
                            status = 'late'
                        else:
                            status = 'absent'
                    
                    date = f"2024-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
                    data.append([student_id, date, course, status])
        
        df = pd.DataFrame(data, columns=['student_id', 'date', 'course', 'status'])
        return df
    
    def generate_courses(self):
        """生成选课行为数据，实施学生选课机制"""
        data = []
        
        # 根据专业设置不同的选课模式
        major_course_patterns = {
            '计算机科学与技术': ['高等数学', '程序设计基础', '数据结构', '算法设计与分析', '操作系统', '计算机网络', '数据库原理', '软件工程'],
            '电子工程': ['高等数学', '大学物理', '线性代数', '计算机组成原理', '嵌入式系统', '信息安全'],
            '软件工程': ['高等数学', '程序设计基础', '数据结构', '操作系统', '软件工程', '数据库原理'],
            '数据科学': ['高等数学', '线性代数', '概率论与数理统计', '数据结构', '数据库原理', '机器学习', '数据挖掘'],
            '人工智能': ['高等数学', '线性代数', '概率论与数理统计', '人工智能导论', '机器学习', '深度学习'],
            '信息安全': ['高等数学', '计算机网络', '操作系统', '信息安全', '密码学基础'],
            '网络工程': ['高等数学', '计算机网络', '操作系统', '云计算', '大数据技术'],
            '物联网工程': ['高等数学', '大学物理', '计算机网络', '嵌入式系统', '物联网技术']
        }
        
        for student_id in self.student_ids:
            # 获取学生专业
            student_index = int(student_id[1:]) - 1
            major = self.majors[student_index % len(self.majors)]
            
            # 获取该专业的核心课程
            major_courses = major_course_patterns.get(major, [])
            
            # 每个学生总共选择8-15门课程（不是全部课程）
            total_courses_to_take = random.randint(8, 15)
            
            # 确保至少包含专业核心课程的大部分
            core_courses_count = max(3, len(major_courses) // 2)
            selected_core_courses = random.sample(major_courses, min(core_courses_count, len(major_courses)))
            
            # 从其他课程中选择一些课程
            other_courses = [course for course in self.courses if course not in major_courses]
            additional_courses_count = total_courses_to_take - len(selected_core_courses)
            selected_additional_courses = random.sample(other_courses, min(additional_courses_count, len(other_courses)))
            
            # 合并已选课程
            all_selected_courses = selected_core_courses + selected_additional_courses
            
            # 确保遵循先修条件的选课顺序
            course_sequence = self._generate_course_sequence(all_selected_courses)
            
            # 分配到各个学期
            semesters = []
            for year in self.years:
                for semester in self.semesters:
                    semesters.append((year, semester))
            
            # 分配课程到学期，确保先修课程先选
            course_semester_map = {}
            current_semester_index = 0
            
            for course in course_sequence:
                if current_semester_index< len(semesters):
                    year, semester = semesters[current_semester_index]
                    course_semester_map[course] = (year, semester)
                    # 每学期2-4门课
                    if random.random() < 0.3 or len([c for c, s in course_semester_map.items() if s == (year, semester)]) >= 4:
                        current_semester_index += 1
            
            # 生成选课记录
            for course, (year, semester) in course_semester_map.items():
                data.append([student_id, course, semester, year])
        
        df = pd.DataFrame(data, columns=['student_id', 'course', 'semester', 'year'])
        return df
    
    def _generate_course_sequence(self, courses):
        """根据先修条件生成合理的选课顺序"""
        # 复制课程列表
        remaining_courses = set(courses)
        sequence = []
        
        while remaining_courses:
            # 找出当前可以选的课程（先修条件已满足或没有先修条件）
            available_courses = []
            for course in remaining_courses:
                prerequisites = self.course_catalog[course]['prerequisites']
                # 检查所有先修课程是否已在序列中
                if all(prereq in sequence for prereq in prerequisites):
                    available_courses.append(course)
            
            if not available_courses:
                # 如果没有可用课程，随机选一个（处理循环依赖）
                available_courses = list(remaining_courses)
            
            # 随机选择一个可用课程
            selected_course = random.choice(available_courses)
            sequence.append(selected_course)
            remaining_courses.remove(selected_course)
        
        return sequence
    
    def generate_all_data(self, output_dir='data'):
        """生成所有数据并保存到文件"""
        # 创建输出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 先生成选课数据，供其他方法使用
        courses_df = self.generate_courses()
        
        # 生成数据
        students_df = self.generate_students()
        grades_df = self.generate_grades_with_courses(courses_df)
        attendance_df = self.generate_attendance_with_courses(courses_df)
        
        # 保存数据
        students_df.to_csv(os.path.join(output_dir, 'students.csv'), index=False, encoding='utf-8-sig')
        grades_df.to_csv(os.path.join(output_dir, 'grades.csv'), index=False, encoding='utf-8-sig')
        attendance_df.to_csv(os.path.join(output_dir, 'attendance.csv'), index=False, encoding='utf-8-sig')
        courses_df.to_csv(os.path.join(output_dir, 'courses.csv'), index=False, encoding='utf-8-sig')
        
        print(f"成功生成{self.num_students}个学生的数据")
        print(f"数据已保存到{output_dir}目录")
        print(f"学生信息：{len(students_df)}条记录")
        print(f"成绩数据：{len(grades_df)}条记录")
        print(f"出勤记录：{len(attendance_df)}条记录")
        print(f"选课行为：{len(courses_df)}条记录")
    
    def generate_grades_with_courses(self, courses_df):
        """生成成绩数据，使用已有的选课数据"""
        data = []
        
        for student_id in self.student_ids:
            # 获取该学生的所有选课记录
            student_courses = courses_df[courses_df['student_id'] == student_id]
            
            for _, course_row in student_courses.iterrows():
                course = course_row['course']
                semester = course_row['semester']
                year = course_row['year']
                
                # 根据课程难度设置不同的成绩分布
                course_level = self.course_catalog[course]['level']
                
                if course_level == '低':
                    # 基础课程成绩较好
                    if random.random()< 0.05:
                        score = random.randint(50, 65)
                    else:
                        score = random.randint(70, 95)
                elif course_level == '中':
                    # 中等难度课程
                    if random.random()< 0.1:
                        score = random.randint(45, 65)
                    else:
                        score = random.randint(65, 90)
                elif course_level == '中高':
                    # 中高难度课程
                    if random.random()< 0.15:
                        score = random.randint(40, 65)
                    else:
                        score = random.randint(60, 85)
                else:  # '高'
                    # 高难度课程
                    if random.random()< 0.2:
                        score = random.randint(35, 65)
                    else:
                        score = random.randint(55, 80)
                
                data.append([student_id, course, score, semester, year])
        
        df = pd.DataFrame(data, columns=['student_id', 'course', 'score', 'semester', 'year'])
        return df
    
    def generate_attendance_with_courses(self, courses_df):
        """生成出勤记录，使用已有的选课数据"""
        data = []
        statuses = ['present', 'absent', 'late']
        
        for student_id in self.student_ids:
            # 获取该学生的所有选课记录
            student_courses = courses_df[courses_df['student_id'] == student_id]['course'].unique()
            
            if len(student_courses) == 0:
                continue
            
            # 为每门课生成多次出勤记录
            for course in student_courses:
                # 每门课8-12次出勤记录
                class_count = random.randint(8, 12)
                
                for _ in range(class_count):
                    # 根据课程重要性和学生表现设置出勤概率
                    course_level = self.course_catalog[course]['level']
                    
                    if course_level == '低':
                        # 基础课程出勤率较高
                        if random.random()< 0.8:
                            status = 'present'
                        elif random.random()< 0.15:
                            status = 'late'
                        else:
                            status = 'absent'
                    elif course_level == '中':
                        # 中等难度课程
                        if random.random()< 0.75:
                            status = 'present'
                        elif random.random()< 0.15:
                            status = 'late'
                        else:
                            status = 'absent'
                    elif course_level == '中高':
                        # 中高难度课程
                        if random.random()< 0.7:
                            status = 'present'
                        elif random.random()< 0.15:
                            status = 'late'
                        else:
                            status = 'absent'
                    else:  # '高'
                        # 高难度课程出勤率可能较低
                        if random.random()< 0.65:
                            status = 'present'
                        elif random.random()< 0.15:
                            status = 'late'
                        else:
                            status = 'absent'
                    
                    date = f"2024-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
                    data.append([student_id, date, course, status])
        
        df = pd.DataFrame(data, columns=['student_id', 'date', 'course', 'status'])
        return df

if __name__ == "__main__":
    generator = StudentDataGenerator(num_students=1000)
    generator.generate_all_data()
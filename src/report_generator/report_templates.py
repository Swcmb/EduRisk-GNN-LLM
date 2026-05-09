class ReportTemplates:
    """
    报告模板类，定义不同角色的报告结构
    """
    
    @staticmethod
    def get_student_template() -> str:
        """
        获取学生报告模板
        """
        return """
# {student_name}同学的学业分析报告

## 整体概况
您好，{student_name}同学！基于您的学业数据，我们为您生成了这份个性化分析报告。

### 风险评估
您当前的学业风险等级为：**{risk_level}**

### 学业表现
- 平均成绩：{avg_score}
- 挂科门数：{fail_courses}
- 出勤率：{attendance_rate}

## 详细分析

### 学习优势
- [学习优势1]
- [学习优势2]

### 需要改进的方面
- [需要改进的方面1]
- [需要改进的方面2]

## 个性化建议
1. [建议1]
2. [建议2]
3. [建议3]
4. [建议4]

## 学习路径推荐
根据您的学习情况，我们为您推荐以下学习路径：
- [学习路径1]
- [学习路径2]
- [学习路径3]

希望这份报告对您有所帮助，祝您学业进步！
        """
    
    @staticmethod
    def get_teacher_template() -> str:
        """
        获取教师报告模板
        """
        return """
# {class_name}班级学业分析报告

## 班级概况
您好，老师！基于{class_name}的学业数据，我们为您生成了这份班级分析报告。

### 班级基本信息
- 班级人数：{total_students}
- 班级平均成绩：{avg_score}

### 风险分布
- 高风险学生：{high_risk_count}人
- 中风险学生：{medium_risk_count}人
- 低风险学生：{low_risk_count}人

## 详细分析

### 学业表现分析
- 班级整体成绩分布情况
- 各课程成绩分析
- 学生出勤情况分析

### 风险学生分析
- 高风险学生主要集中在哪些课程
- 风险学生的共同特征
- 需要重点关注的学生名单

## 教学建议
1. [教学建议1]
2. [教学建议2]
3. [教学建议3]
4. [教学建议4]

## 后续行动建议
- [后续行动建议1]
- [后续行动建议2]
- [后续行动建议3]

希望这份报告对您的教学工作有所帮助！
        """
    
    @staticmethod
    def get_admin_template() -> str:
        """
        获取管理者报告模板
        """
        return """
# 学校学业风险分析报告

## 整体概况
您好，管理者！基于学校的学业数据，我们为您生成了这份综合分析报告。

### 学校基本信息
- 学生总数：{total_students}
- 整体平均成绩：{avg_score}
- 整体出勤率：{attendance_rate}

### 风险分布
- 高风险学生：{high_risk_count}人 ({high_risk_percentage})
- 中风险学生：{medium_risk_count}人 ({medium_risk_percentage})
- 低风险学生：{low_risk_count}人 ({low_risk_percentage})

## 详细分析

### 学院/专业分析
- 各学院风险分布情况
- 各专业风险分布情况
- 重点关注的学院和专业

### 趋势分析
- 风险学生数量变化趋势
- 整体成绩变化趋势
- 出勤率变化趋势

## 管理建议
1. [管理建议1]
2. [管理建议2]
3. [管理建议3]
4. [管理建议4]

## 资源分配建议
- [资源分配建议1]
- [资源分配建议2]
- [资源分配建议3]
- [资源分配建议4]

希望这份报告对学校的管理决策有所帮助！
        """
    
    @staticmethod
    def get_template_by_role(role: str) -> str:
        """
        根据角色获取对应的报告模板
        
        Args:
            role: 角色，如'student', 'teacher', 'admin'
        
        Returns:
            报告模板字符串
        """
        template_map = {
            'student': ReportTemplates.get_student_template(),
            'teacher': ReportTemplates.get_teacher_template(),
            'admin': ReportTemplates.get_admin_template()
        }
        return template_map.get(role, "")

from .recommendation import LearningPathRecommender


def get_recommendations(student_id, top_n=5):
    """
    获取学生的课程推荐（传统算法）
    
    Args:
        student_id: 学生ID
        top_n: 推荐课程数量
        
    Returns:
        list: 推荐课程列表
    """
    recommender = LearningPathRecommender(min_support=0.05)
    recommender.fit()
    recommended_courses = recommender.recommend_courses(student_id, top_n)
    
    # 如果没有推荐课程，检查学生是否已选所有课程
    if not recommended_courses:
        student_courses = recommender._get_student_courses(student_id)
        all_courses = set(recommender.data['courses']['course'].unique())
        if len(set(student_courses)) == len(all_courses):
            return ["该学生已选择所有课程，无需推荐"]
    
    return recommended_courses


def get_llm_recommendations(student_id, top_n=5):
    """
    使用LLM获取学生的个性化课程推荐
    
    Args:
        student_id: 学生ID
        top_n: 推荐课程数量
        
    Returns:
        dict: 包含推荐课程和推荐理由的字典
    """
    recommender = LearningPathRecommender(min_support=0.05)
    recommender.fit()
    return recommender.recommend_courses_with_llm(student_id, top_n)


def get_learning_path(student_id):
    """
    获取学生的个性化学习路径
    
    Args:
        student_id: 学生ID
        
    Returns:
        dict: 包含推荐课程和学习路径的字典
    """
    recommender = LearningPathRecommender()
    recommender.fit()
    return recommender.get_personalized_path(student_id)

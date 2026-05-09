from .report_generator import ReportGenerator


def generate_student_report(student_id):
    """
    生成学生报告
    
    Args:
        student_id: 学生ID
        
    Returns:
        str: 生成的报告文本
    """
    generator = ReportGenerator()
    return generator.generate_student_report(student_id)


def generate_teacher_report(class_name='班级'):
    """
    生成教师报告
    
    Args:
        class_name: 班级名称
        
    Returns:
        str: 生成的报告文本
    """
    generator = ReportGenerator()
    return generator.generate_teacher_report(class_name)


def generate_admin_report():
    """
    生成管理者报告
    
    Returns:
        str: 生成的报告文本
    """
    generator = ReportGenerator()
    return generator.generate_admin_report()


def export_report(report, filename, format='txt'):
    """
    导出报告
    
    Args:
        report: 报告文本
        filename: 文件名
        format: 格式，支持'txt', 'md'
        
    Returns:
        bool: 是否导出成功
    """
    generator = ReportGenerator()
    return generator.export_report(report, filename, format)


def generate_and_export_report(role, filename, **kwargs):
    """
    生成并导出报告
    
    Args:
        role: 角色，如'student', 'teacher', 'admin'
        filename: 文件名
        **kwargs: 额外参数
        
    Returns:
        bool: 是否成功
    """
    generator = ReportGenerator()
    return generator.generate_and_export_report(role, filename, **kwargs)

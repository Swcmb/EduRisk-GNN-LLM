from .data_loader import load_data
from .data_cleaning import clean_student_data
from .feature_engineering import extract_features
from .data_quality import evaluate_data_quality

def run_data_pipeline(data_dir='data'):
    """
    运行完整的数据处理流程
    
    Args:
        data_dir (str): 数据目录路径
    
    Returns:
        dict: 包含处理结果的字典
    """
    # 加载数据
    data = load_data(data_dir)
    
    # 清洗数据
    cleaned_data = clean_student_data(data)
    
    # 评估数据质量
    quality_report = evaluate_data_quality(cleaned_data)
    
    # 提取特征
    features = extract_features(cleaned_data)
    
    return {
        'raw_data': data,
        'cleaned_data': cleaned_data,
        'quality_report': quality_report,
        'features': features
    }
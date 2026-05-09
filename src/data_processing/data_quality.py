import pandas as pd
import numpy as np

def evaluate_data_quality(data):
    """
    评估数据质量
    
    Args:
        data (dict): 包含不同类型数据的字典
    
    Returns:
        dict: 数据质量评估结果
    """
    quality_report = {}
    
    for data_type, df in data.items():
        if isinstance(df, pd.DataFrame):
            report = {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'missing_values': {}
            }
            
            # 计算每列的缺失值
            for col in df.columns:
                missing_count = df[col].isnull().sum()
                missing_percent = (missing_count / len(df)) * 100
                report['missing_values'][col] = {
                    'count': int(missing_count),
                    'percentage': round(missing_percent, 2)
                }
            
            # 计算整体缺失率
            total_cells = len(df) * len(df.columns)
            total_missing = df.isnull().sum().sum()
            report['overall_missing_rate'] = round((total_missing / total_cells) * 100, 2)
            
            # 检查数据类型
            report['data_types'] = df.dtypes.to_dict()
            
            # 检查唯一性
            if 'student_id' in df.columns:
                unique_students = df['student_id'].nunique()
                report['unique_students'] = unique_students
            
            quality_report[data_type] = report
    
    return quality_report
import time
import pandas as pd
import numpy as np
from .apriori import Apriori

def evaluate_performance(transactions, param_grid=None):
    """
    评估Apriori算法在不同参数下的性能
    
    参数:
    - transactions: 交易数据
    - param_grid: 参数网格，包含不同的min_support和min_confidence值
    
    返回:
    - 性能评估结果的DataFrame
    """
    if param_grid is None:
        param_grid = {
            'min_support': [0.05, 0.1, 0.15, 0.2],
            'min_confidence': [0.4, 0.5, 0.6, 0.7]
        }
    
    results = []
    
    for min_support in param_grid['min_support']:
        for min_confidence in param_grid['min_confidence']:
            start_time = time.time()
            
            # 训练模型
            model = Apriori(min_support=min_support, min_confidence=min_confidence)
            model.fit(transactions)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # 收集结果
            n_frequent_itemsets = len(model.get_frequent_itemsets())
            n_rules = len(model.get_rules())
            
            results.append({
                'min_support': min_support,
                'min_confidence': min_confidence,
                'execution_time': execution_time,
                'n_frequent_itemsets': n_frequent_itemsets,
                'n_rules': n_rules
            })
    
    return pd.DataFrame(results)

def evaluate_scalability(transactions, scale_factors=None):
    """
    评估Apriori算法的可扩展性
    
    参数:
    - transactions: 原始交易数据
    - scale_factors: 数据规模因子列表
    
    返回:
    - 可扩展性评估结果的DataFrame
    """
    if scale_factors is None:
        scale_factors = [0.25, 0.5, 0.75, 1.0]
    
    results = []
    
    for factor in scale_factors:
        # 按比例采样数据
        n_samples = int(len(transactions) * factor)
        sampled_transactions = transactions[:n_samples]
        
        start_time = time.time()
        
        # 训练模型
        model = Apriori(min_support=0.1, min_confidence=0.5)
        model.fit(sampled_transactions)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 收集结果
        n_frequent_itemsets = len(model.get_frequent_itemsets())
        n_rules = len(model.get_rules())
        
        results.append({
            'data_size': n_samples,
            'scale_factor': factor,
            'execution_time': execution_time,
            'n_frequent_itemsets': n_frequent_itemsets,
            'n_rules': n_rules
        })
    
    return pd.DataFrame(results)

def optimize_parameters(transactions, param_grid=None):
    """
    优化Apriori算法的参数
    
    参数:
    - transactions: 交易数据
    - param_grid: 参数网格
    
    返回:
    - 最佳参数组合
    """
    if param_grid is None:
        param_grid = {
            'min_support': [0.05, 0.1, 0.15, 0.2],
            'min_confidence': [0.4, 0.5, 0.6, 0.7]
        }
    
    performance_df = evaluate_performance(transactions, param_grid)
    
    # 基于规则数量和执行时间的加权评分
    performance_df['score'] = performance_df['n_rules'] / (performance_df['execution_time'] + 1)
    
    # 选择最佳参数
    best_params = performance_df.loc[performance_df['score'].idxmax()]
    
    return {
        'min_support': best_params['min_support'],
        'min_confidence': best_params['min_confidence'],
        'score': best_params['score'],
        'execution_time': best_params['execution_time'],
        'n_rules': best_params['n_rules']
    }

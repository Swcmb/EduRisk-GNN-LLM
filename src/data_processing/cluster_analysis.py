import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from sklearn.preprocessing import StandardScaler


def kmeans_clustering(features, n_clusters=3, random_state=42):
    """
    使用K-means算法进行聚类
    
    Args:
        features (pd.DataFrame): 特征数据
        n_clusters (int): 聚类数量
        random_state (int): 随机种子
    
    Returns:
        pd.DataFrame: 带有聚类标签的数据
        dict: 聚类评估指标
    """
    # 提取特征列（排除student_id）
    feature_cols = [col for col in features.columns if col != 'student_id']
    X = features[feature_cols].values
    
    # 标准化特征
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 应用K-means
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state)
    labels = kmeans.fit_predict(X_scaled)
    
    # 计算评估指标
    metrics = {
        'silhouette_score': silhouette_score(X_scaled, labels),
        'davies_bouldin_score': davies_bouldin_score(X_scaled, labels),
        'calinski_harabasz_score': calinski_harabasz_score(X_scaled, labels),
        'inertia': kmeans.inertia_
    }
    
    # 添加聚类标签
    result = features.copy()
    result['cluster'] = labels
    
    return result, metrics


def dbscan_clustering(features, eps=0.5, min_samples=5):
    """
    使用DBSCAN算法进行聚类
    
    Args:
        features (pd.DataFrame): 特征数据
        eps (float): 邻域半径
        min_samples (int): 最小样本数
    
    Returns:
        pd.DataFrame: 带有聚类标签的数据
        dict: 聚类评估指标
    """
    # 提取特征列（排除student_id）
    feature_cols = [col for col in features.columns if col != 'student_id']
    X = features[feature_cols].values
    
    # 标准化特征
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 应用DBSCAN
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    labels = dbscan.fit_predict(X_scaled)
    
    # 计算评估指标（只在有至少两个聚类时计算）
    metrics = {}
    if len(set(labels)) > 1:
        metrics = {
            'silhouette_score': silhouette_score(X_scaled, labels),
            'davies_bouldin_score': davies_bouldin_score(X_scaled, labels),
            'calinski_harabasz_score': calinski_harabasz_score(X_scaled, labels),
            'n_clusters': len(set(labels)) - (1 if -1 in labels else 0),
            'n_noise': list(labels).count(-1)
        }
    else:
        metrics = {
            'n_clusters': 0,
            'n_noise': len(labels)
        }
    
    # 添加聚类标签
    result = features.copy()
    result['cluster'] = labels
    
    return result, metrics


def optimize_kmeans(features, k_range=range(2, 10)):
    """
    优化K-means算法的聚类数量
    
    Args:
        features (pd.DataFrame): 特征数据
        k_range (range): 聚类数量范围
    
    Returns:
        dict: 不同k值的评估指标
        int: 最优k值
    """
    # 提取特征列（排除student_id）
    feature_cols = [col for col in features.columns if col != 'student_id']
    X = features[feature_cols].values
    n_samples = X.shape[0]
    
    # 标准化特征
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 计算不同k值的评估指标
    metrics = {}
    # 确保k值不超过样本数量-1
    valid_k_range = [k for k in k_range if k < n_samples]
    
    for k in valid_k_range:
        kmeans = KMeans(n_clusters=k, random_state=42)
        labels = kmeans.fit_predict(X_scaled)
        metrics[k] = {
            'silhouette_score': silhouette_score(X_scaled, labels),
            'davies_bouldin_score': davies_bouldin_score(X_scaled, labels),
            'calinski_harabasz_score': calinski_harabasz_score(X_scaled, labels),
            'inertia': kmeans.inertia_
        }
    
    # 选择最优k值（基于轮廓系数）
    if metrics:
        best_k = max(metrics, key=lambda k: metrics[k]['silhouette_score'])
    else:
        best_k = 2  # 默认值
    
    return metrics, best_k


def optimize_dbscan(features, eps_range=np.arange(0.1, 1.0, 0.1), min_samples_range=range(3, 8)):
    """
    优化DBSCAN算法的参数
    
    Args:
        features (pd.DataFrame): 特征数据
        eps_range (np.ndarray): eps参数范围
        min_samples_range (range): min_samples参数范围
    
    Returns:
        dict: 不同参数组合的评估指标
        tuple: 最优参数组合 (eps, min_samples)
    """
    # 提取特征列（排除student_id）
    feature_cols = [col for col in features.columns if col != 'student_id']
    X = features[feature_cols].values
    
    # 标准化特征
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 计算不同参数组合的评估指标
    metrics = {}
    best_score = -1
    best_params = (0.5, 5)
    
    for eps in eps_range:
        for min_samples in min_samples_range:
            dbscan = DBSCAN(eps=eps, min_samples=min_samples)
            labels = dbscan.fit_predict(X_scaled)
            
            if len(set(labels)) > 1:
                score = silhouette_score(X_scaled, labels)
                metrics[(eps, min_samples)] = {
                    'silhouette_score': score,
                    'davies_bouldin_score': davies_bouldin_score(X_scaled, labels),
                    'calinski_harabasz_score': calinski_harabasz_score(X_scaled, labels),
                    'n_clusters': len(set(labels)) - (1 if -1 in labels else 0),
                    'n_noise': list(labels).count(-1)
                }
                
                if score > best_score:
                    best_score = score
                    best_params = (eps, min_samples)
            else:
                # 记录没有有效聚类的情况
                metrics[(eps, min_samples)] = {
                    'n_clusters': 0,
                    'n_noise': len(labels)
                }
    
    return metrics, best_params


def analyze_clusters(clustered_data):
    """
    分析聚类结果，计算每个聚类的特征统计
    
    Args:
        clustered_data (pd.DataFrame): 带有聚类标签的数据
    
    Returns:
        pd.DataFrame: 每个聚类的特征统计
    """
    # 提取特征列（排除student_id）
    feature_cols = [col for col in clustered_data.columns if col not in ['student_id', 'cluster']]
    
    # 计算每个聚类的统计信息
    cluster_stats = clustered_data.groupby('cluster')[feature_cols].agg([
        'mean', 'std', 'min', 'max'
    ]).round(2)
    
    # 添加聚类大小
    cluster_sizes = clustered_data['cluster'].value_counts().sort_index()
    cluster_stats['size'] = cluster_sizes
    
    return cluster_stats
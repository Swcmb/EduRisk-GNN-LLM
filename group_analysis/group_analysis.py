import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sklearn.preprocessing import StandardScaler
from data_processing.cluster_analysis import kmeans_clustering, dbscan_clustering, optimize_kmeans, analyze_clusters
from data_processing.data_loader import load_data


def load_and_preprocess_data():
    """
    加载并预处理数据，为群体特征分析做准备
    
    Returns:
        pd.DataFrame: 包含学生特征的综合数据集
    """
    # 加载数据
    data = load_data()
    students = data['students']
    grades = data['grades']
    attendance = data['attendance']
    
    # 计算每个学生的平均成绩
    student_grades = grades.groupby('student_id')['score'].agg(['mean', 'std', 'count']).reset_index()
    student_grades.columns = ['student_id', 'avg_score', 'score_std', 'course_count']
    
    # 计算每个学生的出勤率
    attendance['is_present'] = attendance['status'].apply(lambda x: 1 if x == 'present' else 0)
    student_attendance = attendance.groupby('student_id')['is_present'].agg(['mean', 'count']).reset_index()
    student_attendance.columns = ['student_id', 'attendance_rate', 'attendance_count']
    
    # 合并数据
    student_data = students.merge(student_grades, on='student_id', how='left')
    student_data = student_data.merge(student_attendance, on='student_id', how='left')
    
    # 处理缺失值
    student_data = student_data.fillna(0)
    
    # 提取特征（包含gender，但仅用于统计）
    features = student_data[['student_id', 'age', 'avg_score', 'score_std', 'course_count', 'attendance_rate']]
    
    return student_data, features


def analyze_student_groups():
    """
    分析学生群体特征，使用聚类算法识别不同类型的学生
    
    Returns:
        dict: 包含聚类结果和分析的综合信息
    """
    # 加载和预处理数据
    student_data, features = load_and_preprocess_data()
    
    # 优化K-means聚类
    metrics, best_k = optimize_kmeans(features)
    print(f"最优聚类数量: {best_k}")
    print("聚类评估指标:")
    for k, metric in metrics.items():
        print(f"k={k}: 轮廓系数={metric['silhouette_score']:.3f}")
    
    # 使用最优参数进行聚类
    clustered_data, cluster_metrics = kmeans_clustering(features, n_clusters=best_k)
    
    # 分析每个聚类的特征
    cluster_stats = analyze_clusters(clustered_data)
    print("\n聚类统计信息:")
    print(cluster_stats)
    
    # 合并原始数据和聚类标签
    student_data_with_cluster = student_data.merge(clustered_data[['student_id', 'cluster']], on='student_id')
    
    # 分析不同聚类的行为模式
    group_analysis = analyze_group_behavior(student_data_with_cluster)
    
    return {
        'clustered_data': student_data_with_cluster,
        'cluster_stats': cluster_stats,
        'cluster_metrics': cluster_metrics,
        'group_behavior': group_analysis
    }


def analyze_group_behavior(clustered_data):
    """
    分析不同聚类的行为模式和学习特点
    
    Args:
        clustered_data (pd.DataFrame): 带有聚类标签的学生数据
    
    Returns:
        dict: 不同群体的行为分析结果
    """
    analysis = {}
    
    # 按聚类分组分析
    for cluster_id in clustered_data['cluster'].unique():
        cluster_data = clustered_data[clustered_data['cluster'] == cluster_id]
        
        # 计算该群体的基本统计
        analysis[cluster_id] = {
            'size': len(cluster_data),
            'avg_age': cluster_data['age'].mean(),
            'avg_score': cluster_data['avg_score'].mean(),
            'avg_attendance': cluster_data['attendance_rate'].mean(),
            'gender_distribution': cluster_data['gender'].value_counts().to_dict() if 'gender' in cluster_data.columns else {'未知': len(cluster_data)},
            'major_distribution': cluster_data['major'].value_counts().to_dict(),
            'avg_courses': cluster_data['course_count'].mean()
        }
    
    return analysis


def generate_group_report(analysis_results, output_file='group_analysis_report.csv'):
    """
    生成群体特征分析报告
    
    Args:
        analysis_results (dict): 群体分析结果
        output_file (str): 报告输出文件路径
    """
    clustered_data = analysis_results['clustered_data']
    group_behavior = analysis_results['group_behavior']
    
    # 创建报告数据
    report_data = []
    for cluster_id, behavior in group_behavior.items():
        report_data.append({
            'cluster_id': cluster_id,
            'group_size': behavior['size'],
            'avg_age': behavior['avg_age'],
            'avg_score': behavior['avg_score'],
            'avg_attendance': behavior['avg_attendance'],
            'avg_courses': behavior['avg_courses'],
            'gender_distribution': str(behavior['gender_distribution']),
            'major_distribution': str(behavior['major_distribution'])
        })
    
    # 转换为DataFrame并保存
    report_df = pd.DataFrame(report_data)
    report_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"群体特征分析报告已保存到 {output_file}")
    
    return report_df


def create_group_visualization(analysis_results, output_dir='group_visualizations'):
    """
    创建群体特征可视化
    
    Args:
        analysis_results (dict): 群体分析结果
        output_dir (str): 可视化输出目录
    """
    import os
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    clustered_data = analysis_results['clustered_data']
    cluster_stats = analysis_results['cluster_stats']
    
    # 1. 群体大小分布
    plt.figure(figsize=(10, 6))
    cluster_sizes = clustered_data['cluster'].value_counts().sort_index()
    sns.barplot(x=cluster_sizes.index, y=cluster_sizes.values)
    plt.title('不同群体的学生数量')
    plt.xlabel('群体ID')
    plt.ylabel('学生数量')
    plt.savefig(os.path.join(output_dir, 'group_size.png'))
    plt.close()
    
    # 2. 群体成绩分布
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='cluster', y='avg_score', data=clustered_data)
    plt.title('不同群体的平均成绩分布')
    plt.xlabel('群体ID')
    plt.ylabel('平均成绩')
    plt.savefig(os.path.join(output_dir, 'group_scores.png'))
    plt.close()
    
    # 3. 群体出勤率分布
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='cluster', y='attendance_rate', data=clustered_data)
    plt.title('不同群体的出勤率分布')
    plt.xlabel('群体ID')
    plt.ylabel('出勤率')
    plt.savefig(os.path.join(output_dir, 'group_attendance.png'))
    plt.close()
    
    # 4. 群体特征雷达图
    features = ['avg_score', 'attendance_rate', 'course_count', 'age']
    clusters = clustered_data['cluster'].unique()
    
    if len(clusters) > 0:
        # 根据聚类数量确定布局
        if len(clusters) <= 4:
            plt.figure(figsize=(12, 10))
            rows, cols = 2, 2
        elif len(clusters) <= 6:
            plt.figure(figsize=(15, 12))
            rows, cols = 3, 2
        else:
            plt.figure(figsize=(18, 15))
            rows, cols = 4, 2
        
        for i, cluster_id in enumerate(clusters):
            if i >= rows * cols:
                break
                
            cluster_data = clustered_data[clustered_data['cluster'] == cluster_id]
            values = [cluster_data[feature].mean() for feature in features]
            
            # 标准化值
            scaler = StandardScaler()
            values_scaled = scaler.fit_transform(np.array(values).reshape(-1, 1)).flatten()
            
            # 雷达图
            angles = np.linspace(0, 2 * np.pi, len(features), endpoint=False).tolist()
            values_scaled = np.concatenate((values_scaled, [values_scaled[0]]))
            angles += angles[:1]
            
            ax = plt.subplot(rows, cols, i+1, polar=True)
            ax.plot(angles, values_scaled, 'o-', linewidth=2, label=f'群体 {cluster_id}')
            ax.fill(angles, values_scaled, alpha=0.25)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(features)
            ax.set_title(f'群体 {cluster_id} 特征')
            ax.grid(True)
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'group_features_radar.png'))
    plt.close()
    
    print(f"群体特征可视化已保存到 {output_dir} 目录")


def create_group_dashboard(analysis_results, output_file='group_dashboard.html'):
    """
    创建群体特征可视化仪表盘
    
    Args:
        analysis_results (dict): 群体分析结果
        output_file (str): 仪表盘输出文件路径
    """
    clustered_data = analysis_results['clustered_data']
    group_behavior = analysis_results['group_behavior']
    
    # 生成HTML仪表盘
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>学生群体特征分析仪表盘</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.8/dist/chart.umd.min.js"></script>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .chart-container {{ position: relative; height: 400px; margin-bottom: 30px; }}
            .card {{ margin-bottom: 20px; }}
            h1, h2, h3 {{ color: #333; }}
            .summary-card {{ text-align: center; padding: 20px; }}
            .summary-value {{ font-size: 24px; font-weight: bold; color: #007bff; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="text-center mb-4">学生群体特征分析仪表盘</h1>
            
            <!-- 总体概览 -->
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="card">
                        <div class="card-body summary-card">
                            <h3>总学生数</h3>
                            <div class="summary-value">{len(clustered_data)}</div>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card">
                        <div class="card-body summary-card">
                            <h3>群体数量</h3>
                            <div class="summary-value">{len(clustered_data['cluster'].unique())}</div>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card">
                        <div class="card-body summary-card">
                            <h3>平均成绩</h3>
                            <div class="summary-value">{clustered_data['avg_score'].mean():.2f}</div>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card">
                        <div class="card-body summary-card">
                            <h3>平均出勤率</h3>
                            <div class="summary-value">{clustered_data['attendance_rate'].mean():.2f}</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 群体大小分布 -->
            <div class="card mb-4">
                <div class="card-header">
                    <h2>群体大小分布</h2>
                </div>
                <div class="card-body">
                    <div class="chart-container">
                        <canvas id="groupSizeChart"></canvas>
                    </div>
                </div>
            </div>
            
            <!-- 群体成绩分布 -->
            <div class="card mb-4">
                <div class="card-header">
                    <h2>群体成绩分布</h2>
                </div>
                <div class="card-body">
                    <div class="chart-container">
                        <canvas id="groupScoreChart"></canvas>
                    </div>
                </div>
            </div>
            
            <!-- 群体出勤率分布 -->
            <div class="card mb-4">
                <div class="card-header">
                    <h2>群体出勤率分布</h2>
                </div>
                <div class="card-body">
                    <div class="chart-container">
                        <canvas id="groupAttendanceChart"></canvas>
                    </div>
                </div>
            </div>
            
            <!-- 群体特征表格 -->
            <div class="card mb-4">
                <div class="card-header">
                    <h2>群体特征详细信息</h2>
                </div>
                <div class="card-body">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>群体ID</th>
                                <th>学生数量</th>
                                <th>平均年龄</th>
                                <th>平均成绩</th>
                                <th>平均出勤率</th>
                                <th>平均课程数</th>
                                <th>性别分布</th>
                                <th>专业分布</th>
                            </tr>
                        </thead>
                        <tbody>
    """
    
    # 添加表格内容
    for cluster_id, behavior in group_behavior.items():
        html_content += f"""
                            <tr>
                                <td>{cluster_id}</td>
                                <td>{behavior['size']}</td>
                                <td>{behavior['avg_age']:.2f}</td>
                                <td>{behavior['avg_score']:.2f}</td>
                                <td>{behavior['avg_attendance']:.2f}</td>
                                <td>{behavior['avg_courses']:.2f}</td>
                                <td>{behavior['gender_distribution']}</td>
                                <td>{behavior['major_distribution']}</td>
                            </tr>
        """
    
    # 完成HTML内容
    html_content += f"""
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <script>
            // 群体大小分布
            const groupSizeCtx = document.getElementById('groupSizeChart').getContext('2d');
            new Chart(groupSizeCtx, {{
                type: 'bar',
                data: {{
                    labels: [{','.join([f'"{k}"' for k in group_behavior.keys()])}],
                    datasets: [{{
                        label: '学生数量',
                        data: [{','.join([f'{v["size"]}' for v in group_behavior.values()])}],
                        backgroundColor: 'rgba(54, 162, 235, 0.6)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{ display: false }},
                        title: {{ display: true, text: '不同群体的学生数量' }}
                    }},
                    scales: {{
                        y: {{ beginAtZero: true }}
                    }}
                }}
            }});
            
            // 群体成绩分布
            const groupScoreCtx = document.getElementById('groupScoreChart').getContext('2d');
            new Chart(groupScoreCtx, {{
                type: 'bar',
                data: {{
                    labels: [{','.join([f'"{k}"' for k in group_behavior.keys()])}],
                    datasets: [{{
                        label: '平均成绩',
                        data: [{','.join([f'{v["avg_score"]:.2f}' for v in group_behavior.values()])}],
                        backgroundColor: 'rgba(75, 192, 192, 0.6)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{ display: false }},
                        title: {{ display: true, text: '不同群体的平均成绩' }}
                    }},
                    scales: {{
                        y: {{ beginAtZero: true, max: 100 }}
                    }}
                }}
            }});
            
            // 群体出勤率分布
            const groupAttendanceCtx = document.getElementById('groupAttendanceChart').getContext('2d');
            new Chart(groupAttendanceCtx, {{
                type: 'bar',
                data: {{
                    labels: [{','.join([f'"{k}"' for k in group_behavior.keys()])}],
                    datasets: [{{
                        label: '平均出勤率',
                        data: [{','.join([f'{v["avg_attendance"]:.2f}' for v in group_behavior.values()])}],
                        backgroundColor: 'rgba(153, 102, 255, 0.6)',
                        borderColor: 'rgba(153, 102, 255, 1)',
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{ display: false }},
                        title: {{ display: true, text: '不同群体的平均出勤率' }}
                    }},
                    scales: {{
                        y: {{ beginAtZero: true, max: 1 }}
                    }}
                }}
            }});
        </script>
    </body>
    </html>
    """
    
    # 保存HTML文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"群体特征可视化仪表盘已保存到 {output_file}")


if __name__ == "__main__":
    # 执行群体特征分析
    analysis_results = analyze_student_groups()
    
    # 生成分析报告
    generate_group_report(analysis_results)
    
    # 创建可视化
    create_group_visualization(analysis_results)
    
    # 创建仪表盘
    create_group_dashboard(analysis_results)

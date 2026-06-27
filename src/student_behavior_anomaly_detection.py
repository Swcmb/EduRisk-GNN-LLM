import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from sklearn.neighbors import LocalOutlierFactor
from sklearn.metrics import pairwise_distances
from sklearn.preprocessing import StandardScaler

from src.student_behavior_representation import StudentBehaviorRepresentationSystem
from src.data_processing.data_loader import load_data
from src.data_processing.feature_engineering import extract_features

class StudentBehaviorAnomalyDetection:
    """学生行为异常检测系统"""
    
    def __init__(self, data_dir='data', model_path=None, device='cpu'):
        self.data_dir = data_dir
        self.device = device
        self.model_path = model_path
        
        # 初始化行为表征系统
        self.behavior_system = StudentBehaviorRepresentationSystem(
            data_dir=data_dir, 
            model_path=model_path,
            device=device
        )
        
        # 异常检测相关参数
        self.anomaly_thresholds = {
            'warning': 0.7,      # 预警阈值
            'alert': 0.85,       # 告警阈值
            'critical': 0.95     # 严重告警阈值
        }
        
        # 动态阈值调整参数
        self.dynamic_threshold_enabled = True
        self.history_window_days = 30
        self.confidence_level = 0.95
        
        # 存储历史数据
        self.anomaly_history = {}
        self.student_profiles = {}
        self.last_update_time = datetime.now()
        
        # 加载初始数据
        self._initialize_system()
    
    def _initialize_system(self):
        """初始化系统"""
        # 如果模型未加载，训练模型
        if self.model_path is None:
            print("训练学生行为表征模型...")
            self.behavior_system.train(num_epochs=50)
            self.model_path = 'models/student_behavior_model.pth'
            self.behavior_system.save_model(self.model_path)
        
        # 获取所有学生的表征向量
        self.student_representations = self.behavior_system.get_all_representations()
        
        # 初始化学生行为基线
        self._initialize_student_baselines()
    
    def _initialize_student_baselines(self):
        """初始化学生行为基线"""
        data = load_data()
        students = data['students']
        
        for idx, row in students.iterrows():
            student_id = row['student_id']
            if student_id in self.student_representations:
                self.student_profiles[student_id] = {
                    'baseline_representation': self.student_representations[student_id],
                    'anomaly_scores': [],
                    'detection_history': [],
                    'last_anomaly_time': None,
                    'alert_level': 'normal'
                }
    
    def calculate_anomaly_score(self, student_id, current_representation):
        """计算异常分数"""
        if student_id not in self.student_profiles:
            raise ValueError(f"学生ID {student_id} 不存在")
        
        baseline = self.student_profiles[student_id]['baseline_representation']
        
        # 计算余弦相似度
        from sklearn.metrics.pairwise import cosine_similarity
        similarity = cosine_similarity([current_representation], [baseline])[0][0]
        
        # 转换为异常分数（相似度越低，异常分数越高）
        anomaly_score = 1 - similarity
        
        return anomaly_score
    
    def detect_anomaly(self, student_id, student_data):
        """检测学生行为异常"""
        # 获取当前行为表征
        current_representation = self.behavior_system.get_student_representation(student_id)
        
        # 计算异常分数
        anomaly_score = self.calculate_anomaly_score(student_id, current_representation)
        
        # 根据动态阈值调整
        adjusted_thresholds = self._get_dynamic_thresholds(student_id)
        
        # 确定告警级别
        alert_level = self._determine_alert_level(anomaly_score, adjusted_thresholds)
        
        # 更新学生档案
        self._update_student_profile(student_id, anomaly_score, alert_level)
        
        return {
            'student_id': student_id,
            'anomaly_score': anomaly_score,
            'alert_level': alert_level,
            'timestamp': datetime.now(),
            'thresholds': adjusted_thresholds
        }
    
    def _get_dynamic_thresholds(self, student_id):
        """获取动态调整后的阈值"""
        if not self.dynamic_threshold_enabled:
            return self.anomaly_thresholds
        
        profile = self.student_profiles.get(student_id, {})
        history_scores = profile.get('anomaly_scores', [])
        
        if len(history_scores) < 10:
            return self.anomaly_thresholds
        
        # 计算历史分数的统计信息
        scores = np.array(history_scores)
        mean_score = np.mean(scores)
        std_score = np.std(scores)
        
        # 根据历史数据调整阈值
        adjusted_thresholds = {}
        for level, base_threshold in self.anomaly_thresholds.items():
            # 根据历史波动调整阈值
            adjustment = std_score * 0.5
            adjusted_threshold = min(base_threshold + adjustment, 0.99)
            adjusted_thresholds[level] = adjusted_threshold
        
        return adjusted_thresholds
    
    def _determine_alert_level(self, anomaly_score, thresholds):
        """根据异常分数确定告警级别"""
        if anomaly_score >= thresholds['critical']:
            return 'critical'
        elif anomaly_score >= thresholds['alert']:
            return 'alert'
        elif anomaly_score >= thresholds['warning']:
            return 'warning'
        else:
            return 'normal'
    
    def _update_student_profile(self, student_id, anomaly_score, alert_level):
        """更新学生档案"""
        if student_id not in self.student_profiles:
            return
        
        profile = self.student_profiles[student_id]
        
        # 添加异常分数到历史记录
        profile['anomaly_scores'].append(anomaly_score)
        
        # 保持历史记录在窗口范围内
        if len(profile['anomaly_scores']) > 100:
            profile['anomaly_scores'] = profile['anomaly_scores'][-100:]
        
        # 更新检测历史
        profile['detection_history'].append({
            'timestamp': datetime.now(),
            'anomaly_score': anomaly_score,
            'alert_level': alert_level
        })
        
        # 更新最后异常时间
        if alert_level != 'normal':
            profile['last_anomaly_time'] = datetime.now()
        
        # 更新当前告警级别
        profile['alert_level'] = alert_level
    
    def batch_detect_anomalies(self):
        """批量检测所有学生的行为异常"""
        results = []
        
        for student_id in self.student_representations:
            try:
                # 获取学生数据
                data = load_data()
                students = data['students']
                student_data = students[students['student_id'] == student_id]
                
                if not student_data.empty:
                    result = self.detect_anomaly(student_id, student_data.iloc[0])
                    results.append(result)
            except Exception as e:
                print(f"检测学生 {student_id} 异常时出错: {e}")
        
        return results
    
    def update_behavior_baseline(self, student_id, new_representation, confidence=0.7):
        """更新学生行为基线（增量学习）"""
        if student_id not in self.student_profiles:
            raise ValueError(f"学生ID {student_id} 不存在")
        
        # 计算与当前基线的相似度
        baseline = self.student_profiles[student_id]['baseline_representation']
        from sklearn.metrics.pairwise import cosine_similarity
        similarity = cosine_similarity([new_representation], [baseline])[0][0]
        
        # 如果相似度足够高，更新基线
        if similarity >= confidence:
            # 渐进式更新基线
            alpha = 0.3  # 更新率
            new_baseline = baseline * (1 - alpha) + new_representation * alpha
            self.student_profiles[student_id]['baseline_representation'] = new_baseline
            return True
        else:
            return False
    
    def periodic_update(self, update_interval_days=7):
        """定期更新行为基座"""
        current_time = datetime.now()
        time_since_last_update = current_time - self.last_update_time
        
        if time_since_last_update.days >= update_interval_days:
            print("执行定期行为基座更新...")
            
            # 获取最新数据
            data = load_data()
            features = extract_features(data)
            
            # 增量更新模型
            self.behavior_system.incremental_update(features, num_epochs=10)
            
            # 更新所有学生的表征向量
            self.student_representations = self.behavior_system.get_all_representations()
            
            # 更新学生基线
            for student_id, representation in self.student_representations.items():
                if student_id in self.student_profiles:
                    self.update_behavior_baseline(student_id, representation)
            
            self.last_update_time = current_time
            print("行为基座更新完成")
            return True
        else:
            return False
    
    def generate_anomaly_report(self):
        """生成异常检测报告"""
        report_data = []
        
        for student_id, profile in self.student_profiles.items():
            # 获取最新的检测结果
            recent_history = profile['detection_history'][-5:] if len(profile['detection_history']) >= 5 else profile['detection_history']
            
            if recent_history:
                latest_result = recent_history[-1]
                
                report_data.append({
                    'student_id': student_id,
                    'latest_anomaly_score': latest_result['anomaly_score'],
                    'alert_level': latest_result['alert_level'],
                    'last_detection_time': latest_result['timestamp'],
                    'average_anomaly_score': np.mean(profile['anomaly_scores']) if profile['anomaly_scores'] else 0,
                    'alert_count_7days': sum(1 for d in profile['detection_history'] 
                                          if (datetime.now() - d['timestamp']).days <= 7 
                                          and d['alert_level'] != 'normal')
                })
        
        report = pd.DataFrame(report_data)
        
        # 按告警级别和异常分数排序
        alert_order = {'critical': 0, 'alert': 1, 'warning': 2, 'normal': 3}
        report['alert_order'] = report['alert_level'].map(alert_order)
        report = report.sort_values(['alert_order', 'latest_anomaly_score'], ascending=[True, False])
        report = report.drop('alert_order', axis=1)
        
        return report
    
    def visualize_anomaly_patterns(self, student_id=None):
        """可视化异常模式"""
        if student_id:
            # 单个学生的异常模式
            if student_id not in self.student_profiles:
                print(f"学生 {student_id} 不存在")
                return
            
            profile = self.student_profiles[student_id]
            history = profile['detection_history']
            
            if len(history) < 5:
                print(f"学生 {student_id} 的历史数据不足")
                return
            
            timestamps = [h['timestamp'] for h in history]
            scores = [h['anomaly_score'] for h in history]
            levels = [h['alert_level'] for h in history]
            
            plt.figure(figsize=(12, 6))
            plt.plot(timestamps, scores, 'o-', label='异常分数')
            
            # 绘制阈值线
            for level, threshold in self.anomaly_thresholds.items():
                plt.axhline(y=threshold, linestyle='--', alpha=0.7, label=f'{level}阈值')
            
            plt.title(f'学生 {student_id} 的行为异常模式')
            plt.xlabel('时间')
            plt.ylabel('异常分数')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(f'anomaly_pattern_{student_id}.png')
            plt.close()
            
            print(f"学生 {student_id} 的异常模式图已保存")
            
        else:
            # 所有学生的异常分布
            report = self.generate_anomaly_report()
            
            plt.figure(figsize=(10, 6))
            sns.countplot(x='alert_level', data=report, 
                         order=['critical', 'alert', 'warning', 'normal'],
                         palette=['red', 'orange', 'yellow', 'green'])
            plt.title('学生行为异常分布')
            plt.xlabel('告警级别')
            plt.ylabel('学生数量')
            plt.savefig('anomaly_distribution.png')
            plt.close()
            
            print("异常分布统计图已保存")
    
    def get_system_status(self):
        """获取系统状态"""
        total_students = len(self.student_profiles)
        alert_counts = {}
        
        for profile in self.student_profiles.values():
            level = profile['alert_level']
            alert_counts[level] = alert_counts.get(level, 0) + 1
        
        status = {
            'total_students': total_students,
            'alert_distribution': alert_counts,
            'last_update_time': self.last_update_time,
            'model_loaded': self.model_path is not None,
            'dynamic_threshold_enabled': self.dynamic_threshold_enabled
        }
        
        return status
    
    def run_anomaly_detection_system(self):
        """运行完整的异常检测系统"""
        print("启动学生行为异常检测系统...")
        
        # 执行定期更新
        self.periodic_update()
        
        # 批量检测异常
        results = self.batch_detect_anomalies()
        
        # 生成报告
        report = self.generate_anomaly_report()
        
        # 可视化异常模式
        self.visualize_anomaly_patterns()
        
        # 保存报告
        report.to_csv('anomaly_detection_report.csv', index=False, encoding='utf-8-sig')
        
        # 获取系统状态
        status = self.get_system_status()
        
        print("\n异常检测系统运行完成！")
        print(f"检测学生数量: {status['total_students']}")
        print("告警分布:")
        for level, count in status['alert_distribution'].items():
            print(f"  {level}: {count}")
        
        return report, status

if __name__ == "__main__":
    # 初始化异常检测系统
    anomaly_system = StudentBehaviorAnomalyDetection(data_dir='data', device='cpu')
    
    # 运行异常检测
    report, status = anomaly_system.run_anomaly_detection_system()
    
    # 显示报告摘要
    print("\n异常检测报告摘要:")
    print(report.head())
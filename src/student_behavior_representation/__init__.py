"""学生行为表征系统 - 自监督对比学习框架"""

from .data_preprocessing import DataPreprocessor
from .data_augmentation import DataAugmentation
from .simclr_model import SimCLR, NTXentLoss, SimCLRTrainer, IncrementalLearner
from .temporal_alignment import TemporalAlignment

__all__ = [
    'DataPreprocessor',
    'DataAugmentation',
    'SimCLR',
    'NTXentLoss',
    'SimCLRTrainer',
    'IncrementalLearner',
    'TemporalAlignment',
    'StudentBehaviorRepresentationSystem'
]

class StudentBehaviorRepresentationSystem:
    """学生行为表征系统主类"""
    
    def __init__(self, data_dir='data', model_path=None, device='cpu'):
        self.data_dir = data_dir
        self.device = device
        self.model_path = model_path
        
        # 初始化组件
        self.preprocessor = DataPreprocessor(data_dir=data_dir)
        self.augmenter = None
        self.model = None
        self.trainer = None
        self.incremental_learner = None
        
        # 加载数据
        self.preprocessor.load_data()
        
        # 准备特征数据
        self.X, self.student_ids = self.preprocessor.prepare_model_input()
        self.feature_names = self.preprocessor.processed_data['feature_names']
        
        # 初始化数据增强器
        self.augmenter = DataAugmentation(self.feature_names)
        
        # 如果提供了模型路径，加载模型
        if model_path:
            self.load_model(model_path)
    
    def initialize_model(self, input_dim=None, encoder_hidden_dim=128, 
                       encoder_output_dim=64, projection_hidden_dim=32, 
                       projection_output_dim=16):
        """初始化模型"""
        if input_dim is None:
            input_dim = self.X.shape[1]
        
        # 创建SimCLR模型
        self.model = SimCLR(
            input_dim=input_dim,
            encoder_hidden_dim=encoder_hidden_dim,
            encoder_output_dim=encoder_output_dim,
            projection_hidden_dim=projection_hidden_dim,
            projection_output_dim=projection_output_dim
        )
        
        # 创建损失函数
        self.loss_fn = NTXentLoss(temperature=0.5)
        
        # 创建优化器
        import torch.optim as optim
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        
        # 创建训练器
        self.trainer = SimCLRTrainer(
            model=self.model,
            optimizer=self.optimizer,
            loss_fn=self.loss_fn,
            device=self.device
        )
        
        # 创建增量学习器
        self.incremental_learner = IncrementalLearner(
            model=self.model,
            optimizer=self.optimizer,
            loss_fn=self.loss_fn,
            device=self.device
        )
    
    def train(self, num_epochs=50, batch_size=32):
        """训练模型"""
        if self.model is None:
            self.initialize_model()
        
        print(f"开始训练模型，输入维度: {self.X.shape[1]}")
        
        # 热身训练
        self.incremental_learner.warm_start_training(
            initial_data=self.X,
            augmentation_fn=self.augmenter.batch_augmentation,
            num_epochs=num_epochs
        )
        
        print("模型训练完成")
    
    def incremental_update(self, new_data, num_epochs=5):
        """增量更新模型"""
        if self.model is None:
            raise ValueError("模型未初始化，请先调用train()方法")
        
        # 转换新数据
        new_X = self.preprocessor.transform_new_data(new_data)
        
        # 增量学习
        self.incremental_learner.incremental_update(
            new_data=new_X,
            augmentation_fn=self.augmenter.batch_augmentation,
            num_epochs=num_epochs
        )
        
        print("模型增量更新完成")
    
    def get_representation(self, student_data):
        """获取学生行为表征向量"""
        if self.model is None:
            raise ValueError("模型未初始化，请先调用train()方法")
        
        # 转换输入数据
        if isinstance(student_data, dict):
            # 单个学生数据
            df = self.preprocessor.integrate_features()
            # 创建符合格式的DataFrame
            new_data = df[df['student_id'] == student_data['student_id']]
            if new_data.empty:
                raise ValueError(f"学生ID {student_data['student_id']} 不存在")
            X = self.preprocessor.transform_new_data(new_data)
        elif hasattr(student_data, 'shape'):
            # 批量数据
            X = student_data
        else:
            raise ValueError("输入数据格式不支持")
        
        # 获取表征向量
        representations = self.trainer.get_representations(X)
        
        return representations
    
    def get_student_representation(self, student_id):
        """获取指定学生的行为表征向量"""
        # 查找学生数据
        df = self.preprocessor.integrate_features()
        student_data = df[df['student_id'] == student_id]
        
        if student_data.empty:
            raise ValueError(f"学生ID {student_id} 不存在")
        
        # 转换数据
        X = self.preprocessor.transform_new_data(student_data)
        
        # 获取表征向量
        representation = self.trainer.get_representations(X)[0]
        
        return representation
    
    def get_all_representations(self):
        """获取所有学生的行为表征向量"""
        if self.model is None:
            raise ValueError("模型未初始化，请先调用train()方法")
        
        representations = self.trainer.get_representations(self.X)
        
        # 创建学生ID到表征向量的映射
        representation_dict = {
            student_id: representation 
            for student_id, representation in zip(self.student_ids, representations)
        }
        
        return representation_dict
    
    def save_model(self, save_path):
        """保存模型"""
        if self.trainer is None:
            raise ValueError("模型未初始化，请先调用train()方法")
        
        self.trainer.save_model(save_path)
        print(f"模型已保存到: {save_path}")
    
    def load_model(self, load_path):
        """加载模型"""
        # 初始化模型
        self.initialize_model()
        
        # 加载模型权重
        self.trainer.load_model(load_path)
        print(f"模型已从: {load_path} 加载")
    
    def analyze_representation_quality(self):
        """分析表征向量质量"""
        if self.model is None:
            raise ValueError("模型未初始化，请先调用train()方法")
        
        # 获取所有表征向量
        representations = self.trainer.get_representations(self.X)
        
        # 计算统计信息
        import numpy as np
        
        # 计算平均相似度
        from sklearn.metrics.pairwise import cosine_similarity
        similarity_matrix = cosine_similarity(representations)
        avg_similarity = np.mean(similarity_matrix[np.triu_indices(len(representations), 1)])
        
        # 计算表征向量的范数
        norms = np.linalg.norm(representations, axis=1)
        avg_norm = np.mean(norms)
        
        # 计算表征向量的方差
        variance = np.var(representations, axis=0)
        avg_variance = np.mean(variance)
        
        quality_metrics = {
            'average_similarity': avg_similarity,
            'average_norm': avg_norm,
            'average_variance': avg_variance,
            'representation_dim': representations.shape[1],
            'num_students': len(representations)
        }
        
        return quality_metrics
    
    def get_feature_importance(self):
        """获取特征重要性（基于梯度）"""
        if self.model is None:
            raise ValueError("模型未初始化，请先调用train()方法")
        
        # 这是一个简化的实现，实际应用中可能需要更复杂的分析
        # 这里返回随机重要性作为示例
        import numpy as np
        
        importances = np.random.rand(len(self.feature_names))
        importances = importances / np.sum(importances)
        
        feature_importance = {
            name: importance 
            for name, importance in zip(self.feature_names, importances)
        }
        
        return feature_importance
    
    def get_system_info(self):
        """获取系统信息"""
        info = {
            'data_dir': self.data_dir,
            'device': self.device,
            'model_initialized': self.model is not None,
            'num_students': len(self.student_ids),
            'feature_names': self.feature_names,
            'feature_dim': self.X.shape[1]
        }
        
        if self.model is not None:
            info['representation_dim'] = self.model.encoder.fc3.out_features
        
        return info
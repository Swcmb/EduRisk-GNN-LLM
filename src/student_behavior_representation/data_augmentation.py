import numpy as np
import torch

class DataAugmentation:
    def __init__(self, feature_names):
        self.feature_names = feature_names
        self.feature_indices = {name: i for i, name in enumerate(feature_names)}
    
    def add_gaussian_noise(self, x, noise_std=0.1):
        """添加高斯噪声"""
        noise = np.random.normal(0, noise_std, x.shape)
        return x + noise
    
    def scale_features(self, x, scale_range=(0.8, 1.2)):
        """缩放特征值"""
        scales = np.random.uniform(scale_range[0], scale_range[1], x.shape)
        return x * scales
    
    def shift_features(self, x, shift_range=(-0.2, 0.2)):
        """平移特征值"""
        shifts = np.random.uniform(shift_range[0], shift_range[1], x.shape)
        return x + shifts
    
    def mask_features(self, x, mask_ratio=0.1):
        """随机掩码部分特征"""
        mask = np.random.random(x.shape) < mask_ratio
        x_masked = x.copy()
        x_masked[mask] = 0
        return x_masked
    
    def shuffle_features(self, x, shuffle_prob=0.1):
        """随机打乱特征顺序"""
        if np.random.random()< shuffle_prob:
            indices = np.random.permutation(x.shape[1])
            return x[:, indices]
        return x
    
    def interpolate_features(self, x1, x2, alpha=None):
        """在两个样本之间进行插值"""
        if alpha is None:
            alpha = np.random.random()
        return alpha * x1 + (1 - alpha) * x2
    
    def augment_single_sample(self, x, augmentation_prob=0.8):
        """对单个样本应用数据增强"""
        if np.random.random()< augmentation_prob:
            aug_methods = [
                (self.add_gaussian_noise, {'noise_std': 0.05}),
                (self.scale_features, {'scale_range': (0.9, 1.1)}),
                (self.shift_features, {'shift_range': (-0.1, 0.1)}),
                (self.mask_features, {'mask_ratio': 0.05})
            ]
            
            # 随机选择一种增强方法
            method, kwargs = aug_methods[np.random.randint(len(aug_methods))]
            x_augmented = method(x, **kwargs)
            
            # 确保特征在合理范围内
            x_augmented = np.clip(x_augmented, -3, 3)
            
            return x_augmented
        return x
    
    def create_contrastive_pairs(self, X, pair_count=2):
        """创建对比学习的正负样本对"""
        pairs = []
        labels = []
        
        n_samples = X.shape[0]
        
        for i in range(n_samples):
            anchor = X[i]
            
            # 创建正样本（对锚点进行增强）
            positive = self.augment_single_sample(anchor)
            
            # 创建负样本（随机选择其他样本）
            negative_indices = np.random.choice([j for j in range(n_samples) if j != i], 
                                            size=pair_count-1, replace=False)
            negatives = X[negative_indices]
            
            # 创建增强后的负样本
            augmented_negatives = [self.augment_single_sample(neg) for neg in negatives]
            
            # 构建样本对
            for p in [positive] + augmented_negatives:
                pairs.append((anchor, p))
                labels.append(1 if p is positive else 0)
        
        return pairs, labels
    
    def batch_augmentation(self, X, augmentation_prob=0.8):
        """批量数据增强"""
        X_augmented = np.zeros_like(X)
        
        for i in range(X.shape[0]):
            X_augmented[i] = self.augment_single_sample(X[i], augmentation_prob)
        
        return X_augmented
    
    def apply_feature_specific_augmentations(self, x):
        """应用特征特定的增强"""
        x_augmented = x.copy()
        
        # 对成绩相关特征应用噪声
        grade_features = ['avg_score', 'score_std', 'min_score', 'max_score', 
                        'failed_count', 'failure_rate']
        for feat in grade_features:
            if feat in self.feature_indices:
                idx = self.feature_indices[feat]
                x_augmented[idx] += np.random.normal(0, 0.05)
        
        # 对考勤相关特征应用缩放
        attendance_features = ['attendance_rate', 'late_rate', 'absent_rate']
        for feat in attendance_features:
            if feat in self.feature_indices:
                idx = self.feature_indices[feat]
                scale = np.random.uniform(0.95, 1.05)
                x_augmented[idx] *= scale
        
        # 对年龄应用轻微平移
        if 'age' in self.feature_indices:
            idx = self.feature_indices['age']
            x_augmented[idx] += np.random.uniform(-0.1, 0.1)
        
        return x_augmented
    
    def create_mixed_augmentations(self, X, mixup_alpha=0.2):
        """创建MixUp增强"""
        n_samples = X.shape[0]
        indices = np.random.permutation(n_samples)
        lam = np.random.beta(mixup_alpha, mixup_alpha, n_samples)
        
        X_mixed = np.zeros_like(X)
        for i in range(n_samples):
            j = indices[i]
            X_mixed[i] = lam[i] * X[i] + (1 - lam[i]) * X[j]
        
        return X_mixed
    
    def get_augmentation_summary(self):
        """获取增强方法的摘要"""
        summary = {
            'available_methods': [
                'add_gaussian_noise',
                'scale_features',
                'shift_features',
                'mask_features',
                'shuffle_features',
                'interpolate_features',
                'feature_specific_augmentations',
                'create_contrastive_pairs',
                'create_mixed_augmentations'
            ],
            'feature_names': self.feature_names
        }
        return summary
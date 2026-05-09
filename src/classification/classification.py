import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.combine import SMOTEENN

class AcademicRiskClassifier:
    def __init__(self):
        self.decision_tree_model = None
        self.logistic_regression_model = None
        self.scaler = StandardScaler()
    
    def load_data(self, features, target):
        """加载特征和目标变量"""
        self.features = features
        self.target = target
        return self
    
    def preprocess_data(self, test_size=0.2, random_state=42):
        """数据预处理和划分"""
        # 划分训练集和测试集
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.features, self.target, test_size=test_size, random_state=random_state
        )
        # 特征标准化
        self.X_train_scaled = self.scaler.fit_transform(self.X_train)
        self.X_test_scaled = self.scaler.transform(self.X_test)
        return self
    
    def handle_class_imbalance(self, method='smote', sampling_strategy='auto'):
        """处理类别不平衡问题"""
        if method == 'smote':
            sampler = SMOTE(sampling_strategy=sampling_strategy, random_state=42)
        elif method == 'undersample':
            sampler = RandomUnderSampler(sampling_strategy=sampling_strategy, random_state=42)
        elif method == 'smoteenn':
            sampler = SMOTEENN(sampling_strategy=sampling_strategy, random_state=42)
        else:
            raise ValueError("Invalid method. Use 'smote', 'undersample', or 'smoteenn'.")
        
        self.X_train_resampled, self.y_train_resampled = sampler.fit_resample(self.X_train_scaled, self.y_train)
        return self
    
    def train_decision_tree(self, params=None):
        """训练决策树模型"""
        if params is None:
            params = {}
        
        self.decision_tree_model = DecisionTreeClassifier(**params, random_state=42)
        self.decision_tree_model.fit(self.X_train_resampled, self.y_train_resampled)
        return self
    
    def train_logistic_regression(self, params=None):
        """训练逻辑回归模型"""
        if params is None:
            params = {}
        
        self.logistic_regression_model = LogisticRegression(**params, random_state=42, max_iter=1000)
        self.logistic_regression_model.fit(self.X_train_resampled, self.y_train_resampled)
        return self
    
    def hyperparameter_tuning(self, model_type, param_grid, cv=5):
        """参数调优"""
        if model_type == 'decision_tree':
            base_model = DecisionTreeClassifier(random_state=42)
        elif model_type == 'logistic_regression':
            base_model = LogisticRegression(random_state=42, max_iter=1000)
        else:
            raise ValueError("Invalid model type. Use 'decision_tree' or 'logistic_regression'.")
        
        grid_search = GridSearchCV(estimator=base_model, param_grid=param_grid, cv=cv, scoring='f1')
        grid_search.fit(self.X_train_resampled, self.y_train_resampled)
        
        best_params = grid_search.best_params_
        best_score = grid_search.best_score_
        
        if model_type == 'decision_tree':
            self.decision_tree_model = grid_search.best_estimator_
        else:
            self.logistic_regression_model = grid_search.best_estimator_
        
        return best_params, best_score
    
    def evaluate_model(self, model_type):
        """评估模型性能"""
        if model_type == 'decision_tree':
            if self.decision_tree_model is None:
                raise ValueError("Decision tree model not trained yet.")
            y_pred = self.decision_tree_model.predict(self.X_test_scaled)
        elif model_type == 'logistic_regression':
            if self.logistic_regression_model is None:
                raise ValueError("Logistic regression model not trained yet.")
            y_pred = self.logistic_regression_model.predict(self.X_test_scaled)
        else:
            raise ValueError("Invalid model type. Use 'decision_tree' or 'logistic_regression'.")
        
        # 计算评估指标
        accuracy = accuracy_score(self.y_test, y_pred)
        precision = precision_score(self.y_test, y_pred, average='weighted')
        recall = recall_score(self.y_test, y_pred, average='weighted')
        f1 = f1_score(self.y_test, y_pred, average='weighted')
        conf_matrix = confusion_matrix(self.y_test, y_pred)
        class_report = classification_report(self.y_test, y_pred)
        
        metrics = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'confusion_matrix': conf_matrix,
            'classification_report': class_report
        }
        
        return metrics
    
    def predict(self, model_type, X_new):
        """使用模型进行预测"""
        X_new_scaled = self.scaler.transform(X_new)
        
        if model_type == 'decision_tree':
            if self.decision_tree_model is None:
                raise ValueError("Decision tree model not trained yet.")
            return self.decision_tree_model.predict(X_new_scaled)
        elif model_type == 'logistic_regression':
            if self.logistic_regression_model is None:
                raise ValueError("Logistic regression model not trained yet.")
            return self.logistic_regression_model.predict(X_new_scaled)
        else:
            raise ValueError("Invalid model type. Use 'decision_tree' or 'logistic_regression'.")
    
    def get_feature_importance(self, model_type):
        """获取特征重要性"""
        if model_type == 'decision_tree':
            if self.decision_tree_model is None:
                raise ValueError("Decision tree model not trained yet.")
            return self.decision_tree_model.feature_importances_
        elif model_type == 'logistic_regression':
            if self.logistic_regression_model is None:
                raise ValueError("Logistic regression model not trained yet.")
            return self.logistic_regression_model.coef_[0]
        else:
            raise ValueError("Invalid model type. Use 'decision_tree' or 'logistic_regression'.")

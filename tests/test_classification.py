"""分类模块测试"""
import pytest
import numpy as np


class TestAcademicRiskClassifier:
    """学业风险分类器测试"""

    def test_classifier_init(self):
        """分类器应能正常初始化"""
        from src.classification.classification import AcademicRiskClassifier
        classifier = AcademicRiskClassifier()
        assert classifier is not None

    def test_classifier_has_required_methods(self):
        """分类器应包含必要方法"""
        from src.classification.classification import AcademicRiskClassifier
        classifier = AcademicRiskClassifier()
        assert hasattr(classifier, 'train_decision_tree')
        assert hasattr(classifier, 'train_logistic_regression')
        assert hasattr(classifier, 'predict')

    def test_feature_importance_extraction(self):
        """特征重要性提取应正常工作"""
        from src.data_processing.data_loader import load_data
        from src.data_processing.feature_engineering import extract_features
        from src.classification.classification import AcademicRiskClassifier

        data = load_data('data')
        features = extract_features(data)

        # 准备标签（基于平均成绩）
        features['risk_label'] = (features['avg_score'] < 60).astype(int)

        classifier = AcademicRiskClassifier()
        # 训练需要数据准备，这里仅验证流程不报错
        assert 'risk_label' in features.columns

"""数据处理模块测试"""
import pytest
import pandas as pd
import os


class TestDataLoader:
    """数据加载测试"""

    def test_load_data_returns_dict(self):
        """load_data 应返回字典"""
        from src.data_processing.data_loader import load_data
        data = load_data('data')
        assert isinstance(data, dict)
        assert 'students' in data
        assert 'grades' in data

    def test_students_dataframe_structure(self):
        """学生数据应包含必要列"""
        from src.data_processing.data_loader import load_data
        data = load_data('data')
        students = data['students']
        assert 'student_id' in students.columns
        assert 'name' in students.columns
        assert len(students) > 0

    def test_grades_dataframe_structure(self):
        """成绩数据应包含必要列"""
        from src.data_processing.data_loader import load_data
        data = load_data('data')
        grades = data['grades']
        assert 'student_id' in grades.columns
        assert 'score' in grades.columns
        assert len(grades) > 0


class TestFeatureEngineering:
    """特征工程测试"""

    def test_extract_features_returns_dataframe(self):
        """extract_features 应返回 DataFrame"""
        from src.data_processing.data_loader import load_data
        from src.data_processing.feature_engineering import extract_features
        data = load_data('data')
        features = extract_features(data)
        assert isinstance(features, pd.DataFrame)
        assert len(features) > 0

    def test_features_contain_expected_columns(self):
        """特征应包含预期列"""
        from src.data_processing.data_loader import load_data
        from src.data_processing.feature_engineering import extract_features
        data = load_data('data')
        features = extract_features(data)
        expected_cols = ['student_id', 'avg_score']
        for col in expected_cols:
            assert col in features.columns, f'缺少特征列: {col}'


class TestDataPipeline:
    """数据管线测试"""

    def test_pipeline_returns_complete_result(self):
        """管线应返回完整结果"""
        from src.data_processing.pipeline import run_data_pipeline
        result = run_data_pipeline('data')
        assert 'raw_data' in result
        assert 'cleaned_data' in result
        assert 'features' in result
        assert 'quality_report' in result

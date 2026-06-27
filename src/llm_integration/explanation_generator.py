import json
import os
import datetime
from typing import Dict, List, Optional
import pandas as pd

try:
    import pdfkit
except ImportError:
    pdfkit = None

from .openai_client import llm_client

class ExplanationGenerator:
    """LLM语义化解释生成器"""
    
    def __init__(self):
        self.llm_client = llm_client
    
    def generate_explanation(self, explanation_data: Dict, language: str = 'zh') -> Dict:
        """
        生成语义化解释
        
        Args:
            explanation_data: GNN解释数据，包含学生ID、关键子图、特征重要性等信息
            language: 输出语言，支持'zh'（中文）和'en'（英文）
            
        Returns:
            包含语义化解释的字典
        """
        try:
            # 构建提示词
            prompt = self._build_explanation_prompt(explanation_data, language)
            
            # 调用LLM生成解释
            explanation_text = self.llm_client.generate_student_analysis({
                '学生ID': explanation_data.get('student_id', '未知'),
                '风险等级': '需要分析',
                '风险因素': 'GNN解释数据',
                '行为模式': '需要解释',
                '风险概率': 0.5
            })
            
            # 解析生成的解释
            parsed_explanation = self._parse_explanation(explanation_text, language)
            
            # 添加元数据
            result = {
                'student_id': explanation_data.get('student_id'),
                'language': language,
                'timestamp': datetime.datetime.now().isoformat(),
                'raw_explanation': explanation_text,
                'parsed_explanation': parsed_explanation,
                'confidence_score': self._calculate_confidence_score(explanation_data)
            }
            
            return result
            
        except Exception as e:
            return {
                'error': f"生成解释时出错: {str(e)}",
                'student_id': explanation_data.get('student_id'),
                'language': language,
                'timestamp': datetime.datetime.now().isoformat()
            }
    
    def _build_explanation_prompt(self, explanation_data: Dict, language: str) -> str:
        """构建解释提示词"""
        student_id = explanation_data.get('student_id', '未知')
        key_nodes = explanation_data.get('key_nodes', [])
        key_edges = explanation_data.get('key_edges', [])
        top_features = explanation_data.get('top_features', [])
        feature_importance = explanation_data.get('feature_importance', [])
        
        if language == 'zh':
            prompt = f"""请作为教育数据分析专家，为学生 {student_id} 提供GNN模型预测结果的语义化解释。

GNN解释数据：
- 关键节点: {', '.join(map(str, key_nodes))}
- 关键边: {', '.join([f"{u}-{v}" for u, v in key_edges])}
- 重要特征索引: {', '.join(map(str, top_features))}
- 特征重要性: {', '.join([f"{i}: {v:.4f}" for i, v in enumerate(feature_importance)])}

请提供以下内容：
1. 关键影响因素分析：解释哪些行为特征对预测结果影响最大
2. 学生行为模式解读：分析学生的行为模式和潜在问题
3. 风险原因解释：解释为什么模型认为该学生存在风险
4. 改进建议：基于分析结果提供具体的改进建议
5. 监控重点：建议重点监控哪些行为指标

要求：
- 使用专业但易懂的语言
- 提供具体、可操作的建议
- 解释要准确、全面
- 不要包含技术术语的详细解释"""
        else:  # English
            prompt = f"""Please act as an educational data analysis expert and provide a semantic explanation of the GNN model prediction results for student {student_id}.

GNN explanation data:
- Key nodes: {', '.join(map(str, key_nodes))}
- Key edges: {', '.join([f"{u}-{v}" for u, v in key_edges])}
- Important feature indices: {', '.join(map(str, top_features))}
- Feature importance: {', '.join([f"{i}: {v:.4f}" for i, v in enumerate(feature_importance)])}

Please provide the following content:
1. Key influencing factors analysis: Explain which behavioral features have the greatest impact on the prediction result
2. Student behavior pattern interpretation: Analyze the student's behavior patterns and potential problems
3. Risk cause explanation: Explain why the model considers this student at risk
4. Improvement suggestions: Provide specific improvement suggestions based on the analysis results
5. Monitoring focus: Suggest which behavioral indicators to focus on monitoring

Requirements:
- Use professional but easy-to-understand language
- Provide specific, actionable recommendations
- Explanations should be accurate and comprehensive
- Do not include detailed explanations of technical terms"""
        
        return prompt
    
    def _parse_explanation(self, explanation_text: str, language: str) -> Dict:
        """解析生成的解释文本"""
        # 简单的解析逻辑，实际应用中可能需要更复杂的解析
        sections = {
            'zh': {
                'risk_analysis': '## 风险原因分析',
                'academic_suggestions': '## 学业建议',
                'counseling_strategy': '## 辅导策略',
                'monitoring_metrics': '## 监控指标',
                'long_term_planning': '## 长期规划'
            },
            'en': {
                'risk_analysis': '## Risk Cause Analysis',
                'academic_suggestions': '## Academic Suggestions',
                'counseling_strategy': '## Counseling Strategy',
                'monitoring_metrics': '## Monitoring Metrics',
                'long_term_planning': '## Long-term Planning'
            }
        }
        
        parsed = {}
        current_section = None
        
        for line in explanation_text.split('\n'):
            line = line.strip()
            
            # 检查是否是章节标题
            found_section = False
            for key, title in sections[language].items():
                if line == title:
                    current_section = key
                    parsed[key] = []
                    found_section = True
                    break
            
            # 如果是列表项，添加到当前章节
            if not found_section and current_section and line.startswith('-'):
                parsed[current_section].append(line[2:].strip())
        
        return parsed
    
    def _calculate_confidence_score(self, explanation_data: Dict) -> float:
        """计算解释的可信度评分"""
        feature_importance = explanation_data.get('feature_importance', [])
        edge_importance = explanation_data.get('edge_importance', [])
        
        if not feature_importance and not edge_importance:
            return 0.5
        
        # 计算平均重要性作为可信度的一部分
        feature_avg = sum(feature_importance) / len(feature_importance) if feature_importance else 0
        edge_avg = sum(edge_importance) / len(edge_importance) if edge_importance else 0
        
        # 可信度评分综合考虑特征重要性和边重要性
        confidence = (feature_avg * 0.6 + edge_avg * 0.4)
        
        return min(max(confidence, 0.3), 0.95)  # 限制在0.3-0.95之间
    
    def export_to_json(self, explanation: Dict, filename: Optional[str] = None) -> str:
        """导出解释结果为JSON格式"""
        if filename is None:
            student_id = explanation.get('student_id', 'unknown')
            filename = f'explanation_{student_id}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(explanation, f, ensure_ascii=False, indent=2)
        
        return filename
    
    def export_to_pdf(self, explanation: Dict, filename: Optional[str] = None) -> str:
        """导出解释结果为PDF格式"""
        if filename is None:
            student_id = explanation.get('student_id', 'unknown')
            filename = f'explanation_{student_id}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        
        # 生成HTML内容
        html_content = self._generate_html_content(explanation)
        
        # 使用pdfkit生成PDF
        try:
            pdfkit.from_string(html_content, filename)
            return filename
        except Exception as e:
            # 如果pdfkit不可用，生成HTML文件作为备选
            html_filename = filename.replace('.pdf', '.html')
            with open(html_filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return html_filename
    
    def _generate_html_content(self, explanation: Dict) -> str:
        """生成HTML内容用于PDF导出"""
        student_id = explanation.get('student_id', '未知')
        language = explanation.get('language', 'zh')
        timestamp = explanation.get('timestamp', datetime.datetime.now().isoformat())
        confidence = explanation.get('confidence_score', 0)
        parsed = explanation.get('parsed_explanation', {})
        
        if language == 'zh':
            title = f"学生 {student_id} 的行为分析解释报告"
            sections = {
                'risk_analysis': '风险原因分析',
                'academic_suggestions': '学业建议',
                'counseling_strategy': '辅导策略',
                'monitoring_metrics': '监控指标',
                'long_term_planning': '长期规划'
            }
        else:
            title = f"Behavior Analysis Explanation Report for Student {student_id}"
            sections = {
                'risk_analysis': 'Risk Cause Analysis',
                'academic_suggestions': 'Academic Suggestions',
                'counseling_strategy': 'Counseling Strategy',
                'monitoring_metrics': 'Monitoring Metrics',
                'long_term_planning': 'Long-term Planning'
            }
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            line-height: 1.6;
        }}
        h1 {{
            color: #333;
            text-align: center;
        }}
        .metadata {{
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 30px;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        h2 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 5px;
        }}
        ul {{
            list-style-type: disc;
            margin-left: 20px;
        }}
        li {{
            margin-bottom: 8px;
        }}
        .confidence {{
            background-color: #e8f4f8;
            padding: 10px;
            border-radius: 5px;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    
    <div class="metadata">
        <p><strong>学生ID:</strong> {student_id}</p>
        <p><strong>生成时间:</strong> {timestamp}</p>
        <p><strong>语言:</strong> {'中文' if language == 'zh' else 'English'}</p>
        <div class="confidence">
            <strong>解释可信度评分:</strong> {confidence:.2f}
        </div>
    </div>
"""

        for key, section_title in sections.items():
            if key in parsed and parsed[key]:
                html += f"""    <div class="section">
        <h2>{section_title}</h2>
        <ul>
"""
                for item in parsed[key]:
                    html += f"            <li>{item}</li>\n"
                html += """        </ul>
    </div>
"""

        html += """</body>
</html>"""

        return html
    
    def batch_generate_explanations(self, explanations_data: List[Dict], language: str = 'zh') -> List[Dict]:
        """批量生成解释"""
        results = []
        for data in explanations_data:
            result = self.generate_explanation(data, language)
            results.append(result)
        return results
    
    def get_supported_languages(self) -> List[str]:
        """获取支持的语言列表"""
        return ['zh', 'en']
    
    def validate_explanation_data(self, explanation_data: Dict) -> bool:
        """验证解释数据的有效性"""
        required_fields = ['student_id', 'key_nodes', 'key_edges', 'top_features', 'feature_importance']
        for field in required_fields:
            if field not in explanation_data:
                return False
        return True

# 创建全局实例
explanation_generator = ExplanationGenerator()
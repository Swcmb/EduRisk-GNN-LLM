import os
import json
import requests
from typing import Dict, Optional, List

class OpenAIClient:
    """
    OpenAI协议客户端，支持调用符合OpenAI API规范的LLM服务
    
    支持的功能：
    - 配置模型、API密钥、基础URL
    - 调用chat completions接口生成分析建议
    - 支持不同的LLM提供商（OpenAI、Azure OpenAI、本地部署的兼容服务）
    """
    
    def __init__(self):
        self.config_file = 'llm_config.json'
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """加载LLM配置"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'api_key': '',
            'base_url': 'https://api.openai.com/v1',
            'model': 'gpt-3.5-turbo',
            'temperature': 0.7,
            'max_tokens': 500
        }
    
    def save_config(self, config: Dict) -> None:
        """保存LLM配置"""
        # 处理字段名兼容性
        if 'api_base_url' in config:
            config['base_url'] = config.pop('api_base_url')
        self.config.update(config)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def get_config(self) -> Dict:
        """获取当前配置"""
        config_copy = self.config.copy()
        # 确保返回的配置包含api_base_url字段，以便前端正确显示
        if 'base_url' in config_copy and 'api_base_url' not in config_copy:
            config_copy['api_base_url'] = config_copy['base_url']
        return config_copy
    
    def generate_student_analysis(self, student_data: Dict) -> str:
        """
        生成学生分析建议
        
        Args:
            student_data: 学生数据字典，包含学生ID、姓名、风险等级、风险因素等信息
        
        Returns:
            生成的分析建议文本
        """
        try:
            # 构建提示词
            prompt = self._build_prompt(student_data)
            
            # 调用OpenAI API
            headers = {
                'Content-Type': 'application/json'
            }
            
            # 如果有API密钥，添加Authorization头
            if self.config['api_key']:
                headers['Authorization'] = f'Bearer {self.config["api_key"]}'
            
            data = {
                'model': self.config['model'],
                'messages': [
                    {
                        'role': 'system',
                        'content': '你是一位专业的教育分析师，擅长分析学生学业风险并提供针对性的改进建议。'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'temperature': self.config['temperature'],
                'max_tokens': self.config['max_tokens']
            }
            
            url = f"{self.config['base_url']}/chat/completions"
            # 设置10秒超时，本地LLM模型可能需要较长时间处理
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
            
        except Exception as e:
            return f"生成分析建议时出错: {str(e)}"
    
    def _build_prompt(self, student_data: Dict) -> str:
        """构建分析提示词"""
        student_id = student_data.get('学生ID', student_data.get('id', '未知'))
        name = student_data.get('姓名', student_data.get('name', '未知'))
        risk_level = student_data.get('风险等级', student_data.get('riskLevel', '未知'))
        risk_factors = student_data.get('风险因素', student_data.get('riskFactors', '无'))
        behavior_pattern = student_data.get('行为模式', student_data.get('behaviorPattern', '正常'))
        probability = student_data.get('风险概率', student_data.get('probability', 0))
        
        prompt = f"""请直接输出以下学生的学业风险分析和改进建议，不要包含任何思考过程或引言：

学生信息：
- 学生ID: {student_id}
- 姓名: {name}
- 风险等级: {risk_level}
- 风险概率: {(probability * 100):.1f}%
- 行为模式: {behavior_pattern}
- 风险因素: {risk_factors}

请按照以下格式直接输出结果：

## 风险原因分析
- 具体原因1
- 具体原因2
- 具体原因3

## 学业建议
- 建议1
- 建议2
- 建议3

## 辅导策略
- 策略1
- 策略2
- 策略3

## 监控指标
- 指标1
- 指标2
- 指标3

## 长期规划
- 阶段1：具体措施
- 阶段2：具体措施
- 阶段3：具体措施

要求：
1. 直接输出结构化结果，不要有任何开场白或思考过程
2. 使用简洁明了的语言，每条建议不超过20字
3. 确保每个部分至少包含3条具体内容
4. 建议要具有可操作性和针对性"""
        
        return prompt

# 创建全局实例
llm_client = OpenAIClient()

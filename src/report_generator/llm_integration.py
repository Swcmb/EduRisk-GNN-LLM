import os
import json
import requests
from typing import Dict, Any, Optional

class LLMIntegration:
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化LLM集成
        
        Args:
            api_key: API密钥，如OpenAI API密钥
        """
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        # 加载LLM配置
        self.config = self._load_llm_config()
        
    def _load_llm_config(self):
        """加载LLM配置"""
        config_file = 'llm_config.json'
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'base_url': 'http://localhost:11434',
            'model': 'qwen2.5:7b',
            'temperature': 0.7,
            'max_tokens': 1000
        }
        
    def generate_report(self, role: str, data: Dict[str, Any], template: str) -> str:
        """
        生成针对特定角色的分析报告
        
        Args:
            role: 角色，如'student', 'teacher', 'admin'
            data: 报告数据
            template: 报告模板
        
        Returns:
            生成的报告文本
        """
        # 构建提示词
        prompt = self._build_prompt(role, data, template)
        
        # 调用真实的LLM API
        return self._call_llm_api(prompt)
    
    def _build_prompt(self, role: str, data: Dict[str, Any], template: str) -> str:
        """
        构建LLM提示词
        """
        prompt = f"""你是一位专业的学业分析专家，擅长根据学生数据生成详细的分析报告。

请根据以下数据和模板，为{self._get_role_name(role)}生成一份专业、详细、个性化的分析报告：

【数据】
{json.dumps(data, ensure_ascii=False, indent=2)}

【模板】
{template}

要求：
1. 严格按照模板格式输出，填充所有占位符
2. 分析要基于提供的数据，保持客观准确
3. 建议要具体、可操作、有针对性
4. 使用专业但通俗易懂的语言
5. 突出关键信息，重点关注风险评估和改进建议
6. 直接输出报告内容，不要包含任何开场白或额外解释"""
        return prompt
    
    def _call_llm_api(self, prompt: str) -> str:
        """
        调用LLM API生成报告
        """
        headers = {
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': self.config['model'],
            'messages': [
                {
                    'role': 'system',
                    'content': '你是一位专业的教育数据分析专家，擅长生成详细、专业的学业分析报告。'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': self.config['temperature'],
            'max_tokens': self.config['max_tokens'],
            'stream': False
        }
        
        url = f"{self.config['base_url']}/api/chat"
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result['message']['content'].strip()
    
    def _get_role_name(self, role: str) -> str:
        """
        获取角色的中文名称
        """
        role_map = {
            'student': '学生',
            'teacher': '教师',
            'admin': '管理者'
        }
        return role_map.get(role, role)

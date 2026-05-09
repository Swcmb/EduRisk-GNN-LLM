"""LLM集成模块"""

from .openai_client import OpenAIClient, llm_client
from .explanation_generator import ExplanationGenerator, explanation_generator

__all__ = ['OpenAIClient', 'llm_client', 'ExplanationGenerator', 'explanation_generator']
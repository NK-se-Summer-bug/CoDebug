# -*- coding: utf-8 -*-
"""
常量配置文件
包含预设提示词、默认配置等常量定义
"""

# 预设提示词列表
PRESET_PROMPTS = [
    {
        "name": "default",
        "prompt": "",
        "description": "普通对话助手模式"
    },
    {
        "name": "creative",
        "prompt": """你是一个富有创造力和想象力的AI助手。你善于进行创意思考、头脑风暴和创新性问题解决。

你的特点：
1. 思维活跃，善于联想
2. 能够从多角度思考问题
3. 鼓励用户探索新的可能性
4. 提供原创性的建议和方案

让我们一起探索无限的可能性！""",
        "description": "具有创造力的大模型"
    },
    {
        "name": "analytical",
        "prompt": """你是一个逻辑严谨、分析能力强的AI助手。你擅长数据分析、逻辑推理和系统性思考。

        你的工作方式：
        1. 系统性地分析问题
        2. 基于事实和数据进行推理
        3. 提供结构化的分析结果
        4. 明确指出假设和限制条件

        让我们用理性和逻辑来解决问题。""",
        "description": "进行严谨地数据分析与推理"
    }
]

# API配置
API_BASE_URL = "http://localhost:8000"
API_TIMEOUT = 60

# 默认配置
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_CHAT_HEIGHT = 500
DEFAULT_GRAPH_HEIGHT = 600

# 文件路径
CHAT_HISTORY_FILE = 'chat_history.json'
GRAPH_TEMPLATE_PATHS = [
    "graph.html",
    "./graph.html",
    "frontend/graph.html",
    "./frontend/graph.html",
    "v3_st/frontend/graph.html",
    "./v3_st/frontend/graph.html",
]

# -*- coding: utf-8 -*-
"""
工具函数模块
包含文件操作、会话管理、数据处理等工具函数

注意：此文件已重构为多个专门的模块，但保留此文件以确保向后兼容性
新的模块结构：
- session_manager.py: 会话管理
- graph_manager.py: 知识图谱管理  
- state_manager.py: 状态管理
- triplet_extractor.py: 三元组提取
"""

# 导入所有新模块以保持向后兼容性
from .session_manager import SessionManager
from .graph_manager import GraphManager, GraphUtils
from .state_manager import StateManager
from .triplet_extractor import TripletExtractor, extract_and_store_triplets

# 重新导出所有类和函数，确保原有的导入方式仍然有效
__all__ = [
    'SessionManager',
    'GraphManager', 
    'GraphUtils',  # 保持向后兼容
    'StateManager',
    'TripletExtractor',
    'extract_and_store_triplets'  # 保持向后兼容
]

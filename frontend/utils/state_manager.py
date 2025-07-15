# -*- coding: utf-8 -*-
"""
状态管理模块
包含session state的初始化和各种状态切换功能
"""

import streamlit as st


class StateManager:
    """状态管理器"""
    
    @staticmethod
    def init_session_state():
        """初始化session state"""
        default_states = {
            'messages': [],
            'sessions': {},
            'current_session': None,
            'show_graph': True,
            'triplets': [],
            'session_triplets': {},  # 每个会话的三元组存储
            'available_models': [],
            'current_model': "gpt-4o-mini",
            'temperature': 0.7,
            'system_prompt': "",
            'prompt_mode': "预设",
            'selected_preset_prompt': "default",
            'show_model_settings': False,
            'show_prompt_settings': False,
            'show_agent_page': False,
            'selected_agent': None,
            'available_agents': [],
            'agent_session_id': None,
            'agent_messages': []
        }
        
        for key, default_value in default_states.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    @staticmethod
    def toggle_knowledge_graph():
        """切换知识图谱显示状态"""
        st.session_state.show_graph = not st.session_state.show_graph
    
    @staticmethod
    def change_model(new_model: str):
        """切换当前使用的模型"""
        st.session_state.current_model = new_model
        st.toast(f"已切换到模型: {new_model}", icon="🤖")
    
    @staticmethod
    def change_temperature(new_temperature: float):
        """更改模型温度参数"""
        st.session_state.temperature = new_temperature
    
    @staticmethod
    def toggle_agent_page():
        """切换Agent页面显示状态"""
        st.session_state.show_agent_page = not st.session_state.show_agent_page
        
        # 如果关闭Agent页面，清理Agent相关状态
        if not st.session_state.show_agent_page:
            st.session_state.selected_agent = None
            st.session_state.agent_session_id = None
            st.session_state.agent_messages = []
    
    @staticmethod
    def reset_agent_state():
        """重置Agent相关状态"""
        st.session_state.selected_agent = None
        st.session_state.agent_session_id = None
        st.session_state.agent_messages = []
    
    @staticmethod
    def toggle_model_settings():
        """切换模型设置对话框显示状态"""
        st.session_state.show_model_settings = not st.session_state.show_model_settings
    
    @staticmethod
    def toggle_prompt_settings():
        """切换提示词设置对话框显示状态"""
        st.session_state.show_prompt_settings = not st.session_state.show_prompt_settings

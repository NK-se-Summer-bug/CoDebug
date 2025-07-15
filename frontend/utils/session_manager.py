# -*- coding: utf-8 -*-
"""
会话管理模块
包含会话的创建、切换、删除、保存和加载功能
"""

import json
import streamlit as st
from config.constants import CHAT_HISTORY_FILE


class SessionManager:
    """会话管理器"""
    
    @staticmethod
    def save_chat_history():
        """保存聊天历史"""
        try:
            chat_history = {}
            for session_id, messages in st.session_state.sessions.items():
                chat_history[session_id] = messages
                
            with open(CHAT_HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(chat_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            st.error(f"保存聊天历史失败：{str(e)}")
    
    @staticmethod
    def load_chat_history():
        """加载聊天历史"""
        try:
            with open(CHAT_HISTORY_FILE, 'r', encoding='utf-8') as f:
                chat_history = json.load(f)
                
                # 检查是否是嵌套结构（包含sessions键）
                if isinstance(chat_history, dict) and 'sessions' in chat_history:
                    st.session_state.sessions = chat_history['sessions']
                elif isinstance(chat_history, dict):
                    st.session_state.sessions = chat_history
                else:
                    st.session_state.sessions = {}
                
                # 如果是当前会话，更新messages
                if st.session_state.current_session in st.session_state.sessions:
                    st.session_state.messages = st.session_state.sessions[st.session_state.current_session].copy()
        except FileNotFoundError:
            st.session_state.sessions = {}
        except Exception as e:
            st.error(f"加载聊天历史失败：{str(e)}")
            st.session_state.sessions = {}
    
    @staticmethod
    def create_new_session():
        """创建新会话"""
        # 保存当前会话的三元组（如果有的话）
        if st.session_state.current_session and st.session_state.current_session in st.session_state.sessions:
            if not hasattr(st.session_state, 'session_triplets'):
                st.session_state.session_triplets = {}
            st.session_state.session_triplets[st.session_state.current_session] = st.session_state.get('triplets', [])
        
        # 生成新的会话ID，确保唯一性
        base_id = len(st.session_state.sessions) + 1
        session_id = f"会话{base_id}"
        
        # 如果会话ID已存在，增加数字直到找到唯一的ID
        while session_id in st.session_state.sessions:
            base_id += 1
            session_id = f"会话{base_id}"
        
        # 创建新会话
        st.session_state.sessions[session_id] = []
        st.session_state.current_session = session_id
        st.session_state.messages = []
        
        # 为新会话创建空的三元组列表
        if not hasattr(st.session_state, 'session_triplets'):
            st.session_state.session_triplets = {}
        st.session_state.session_triplets[session_id] = []
        st.session_state.triplets = []
        
        SessionManager.save_chat_history()
    
    @staticmethod
    def switch_session(session_id: str):
        """切换会话"""
        from services.api_service import api_service
        
        # 保存当前会话的三元组（如果有的话）
        if st.session_state.current_session and st.session_state.current_session in st.session_state.sessions:
            if not hasattr(st.session_state, 'session_triplets'):
                st.session_state.session_triplets = {}
            st.session_state.session_triplets[st.session_state.current_session] = st.session_state.get('triplets', [])
        
        st.session_state.current_session = session_id
        # 从后端加载会话历史
        messages, current_model = api_service.get_conversation_history(session_id)
        if messages:
            st.session_state.messages = messages
            st.session_state.sessions[session_id] = messages
            if current_model:
                st.session_state.current_model = current_model
        else:
            st.session_state.messages = st.session_state.sessions.get(session_id, [])
        
        # 加载该会话的三元组
        if not hasattr(st.session_state, 'session_triplets'):
            st.session_state.session_triplets = {}
        st.session_state.triplets = st.session_state.session_triplets.get(session_id, [])
        
        # 如果当前在Agent界面，自动关闭Agent界面
        if st.session_state.show_agent_page:
            st.session_state.show_agent_page = False
            st.session_state.selected_agent = None
            st.session_state.agent_session_id = None
            st.session_state.agent_messages = []
    
    @staticmethod
    def clear_session():
        """清空当前会话"""
        from services.api_service import api_service
        
        if st.session_state.current_session:
            # 从后端清除会话历史
            success = api_service.clear_conversation_history(st.session_state.current_session)
            if success:
                st.session_state.messages = []
                st.session_state.sessions[st.session_state.current_session] = []
                
                # 清空该会话的三元组
                if hasattr(st.session_state, 'session_triplets'):
                    st.session_state.session_triplets[st.session_state.current_session] = []
                st.session_state.triplets = []
                
                SessionManager.save_chat_history()
                st.success("会话已清空")
    
    @staticmethod
    def delete_session(session_id: str):
        """删除会话"""
        if st.session_state.current_session == session_id:
            st.session_state.current_session = None
            st.session_state.messages = []
            st.session_state.triplets = []  # 清空三元组
        
        # 删除会话
        st.session_state.sessions.pop(session_id, None)
        
        # 删除该会话的三元组
        if hasattr(st.session_state, 'session_triplets'):
            st.session_state.session_triplets.pop(session_id, None)
        
        SessionManager.save_chat_history()

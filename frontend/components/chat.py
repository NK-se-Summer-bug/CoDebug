# -*- coding: utf-8 -*-
"""
聊天界面组件
包含聊天消息显示和输入处理
"""

import streamlit as st
from datetime import datetime
from services.api_service import api_service
from utils.helpers import SessionManager, StateManager, extract_and_store_triplets


def show_chat_interface():
    """显示聊天界面"""
    # 创建一个固定高度的容器来显示聊天历史 - 与原始文件保持一致
    chat_container = st.container()
    with chat_container:
        # 根据是否显示图谱决定容器高度
        container_height = 700 if st.session_state.show_graph else 600
        
        with st.container(height=container_height, border=True):
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            
            # 消息容器
            st.markdown('<div class="messages-container">', unsafe_allow_html=True)
            # 显示聊天历史
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # 聊天输入（在容器外部）
    if prompt := st.chat_input("在这里输入您的问题"):
        # 显示用户消息（在输入框下方）
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 显示AI思考状态（在输入框下方）
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("🤔 思考中...")
            
            # 调用后端API（流式聊天）
            try:
                # 确保有session_id
                if not st.session_state.current_session:
                    st.session_state.current_session = f"session_{int(datetime.now().timestamp())}"
                
                full_response = ""
                
                # 流式获取回复
                for chunk in api_service.stream_chat_response(
                    user_message=prompt,
                    session_id=st.session_state.current_session,
                    model_name=st.session_state.current_model,
                    temperature=st.session_state.temperature,
                    system_prompt=st.session_state.system_prompt
                ):
                    full_response += chunk
                    message_placeholder.markdown(full_response + "▌")
                
                # 显示最终响应
                message_placeholder.markdown(full_response)
                
                # 添加用户消息和AI回复到消息列表
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
                # 同步到当前会话
                if st.session_state.current_session:
                    st.session_state.sessions[st.session_state.current_session] = st.session_state.messages.copy()
                    SessionManager.save_chat_history()
                
                # 提取三元组并在有新三元组时重新加载页面
                if full_response and len(full_response) > 50:
                    try:
                        if extract_and_store_triplets(full_response) and st.session_state.show_graph:
                            st.rerun()
                    except Exception:
                        # 静默处理提取错误，不影响聊天体验
                        pass
                
            except Exception as e:
                message_placeholder.error(f"😔 获取回复失败: {e}")


def show_sidebar():
    """显示侧边栏"""
    with st.sidebar:
        # 导入侧边栏样式
        from styles.css import SIDEBAR_CSS
        st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)
        
        # 使用HTML来创建居中的标题 - 与原始文件保持一致
        st.markdown('<h1 class="chat-manager-title">对话管理</h1>', unsafe_allow_html=True)
        
        # 创建按钮容器 - 按照原始文件的结构
        with st.container():
            # 新建会话按钮
            col1, col2, col3 = st.columns([1, 8, 1])
            with col2:
                if st.button("➕ 新建会话", 
                           help="创建一个新的对话", 
                           type="primary",
                           use_container_width=True):
                    SessionManager.create_new_session()
                    st.rerun()
                    
            # 智能Agent按钮
            col1, col2, col3 = st.columns([1, 8, 1])
            with col2:
                if st.button("智能Agent", 
                           help="使用专业AI智能体", 
                           type="primary",
                           use_container_width=True):
                    st.session_state.show_agent_page = True
                    st.rerun()
        
        st.divider()
        
        # 使用HTML来创建子标题
        st.markdown('<h3 class="history-title">历史会话</h3>', unsafe_allow_html=True)
        
        # 创建一个固定高度的容器来显示会话列表
        with st.container(height=250, border=True):
            # 添加session-list类用于样式控制
            st.markdown('<div class="session-list">', unsafe_allow_html=True)
            
            # 对会话进行排序
            def sort_key(session_item):
                session_id = session_item[0]
                # 尝试提取会话ID中的数字
                if session_id.startswith("会话"):
                    try:
                        return int(session_id.replace("会话", ""))
                    except ValueError:
                        return 0
                # 对于其他格式的会话ID，使用字符串排序
                return hash(session_id)
            
            sorted_sessions = sorted(st.session_state.sessions.items(), key=sort_key)
            
            # 显示会话列表
            for session_id, _ in sorted_sessions:
                col1, col2 = st.columns([4, 1])
                with col1:
                    is_current = session_id == st.session_state.current_session
                    if st.button(
                        f"{'🤖 ' if is_current else ''}{session_id}",
                        help="切换到此会话",
                        disabled=is_current,
                        use_container_width=True,
                        key=f"session_{session_id}",
                        type="secondary" if not is_current else "primary"
                    ):
                        SessionManager.switch_session(session_id)
                        st.rerun()
                with col2:
                    if st.button(
                        "🗑",
                        help=f"删除{session_id}",
                        key=f"delete_{session_id}",
                        use_container_width=True
                    ):
                        SessionManager.delete_session(session_id)
                        st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

        # 使用HTML来创建居中的标题
        st.markdown('<h1 class="chat-manager-title">    </h1>', unsafe_allow_html=True)
        st.divider()
        
        # 管理按钮容器
        with st.container():
            col1, col2, col3 = st.columns([1, 8, 1])
            with col2:
                # 清空当前会话按钮
                if st.button("🗑 清空当前会话", 
                           help="清空当前对话的所有消息",
                           disabled=not st.session_state.current_session,
                           type="secondary",
                           use_container_width=True):
                    SessionManager.clear_session()
                    st.rerun()
                
                # 模型设置按钮
                if st.button("模型设置", 
                           help="点击打开模型设置", 
                           key="model_settings_btn",
                           use_container_width=True):
                    st.session_state.show_model_settings = True
                    st.rerun()
                
                # 提示词设置按钮
                if st.button("提示词设置", 
                           help="点击打开提示词设置", 
                           key="prompt_settings_btn",
                           use_container_width=True):
                    st.session_state.show_prompt_settings = True
                    st.rerun()
                
                # 知识图谱切换按钮
                graph_btn_text = "🔍 隐藏图谱" if st.session_state.show_graph else "🔍 显示图谱"
                if st.button(graph_btn_text, 
                           help="切换知识图谱显示",
                           use_container_width=True,
                           key="knowledge_graph_btn"):
                    StateManager.toggle_knowledge_graph()
                    st.rerun()

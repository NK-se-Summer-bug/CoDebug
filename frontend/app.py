# -*- coding: utf-8 -*-
"""
Gridseek - 智能对话系统
主应用入口文件

重构说明：
- 将原来的单体文件拆分为多个模块
- 使用组件化设计，提高代码复用性和维护性
- 分离配置、服务、工具和UI组件
"""

# 在文件最开头添加这些行
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st

# 可选：如果后端模块可用，导入提示词管理器  
prompt_manager = None  # 简化处理，如需要可后续添加

# 导入服务
from services.api_service import api_service

# 导入工具
from utils.helpers import SessionManager, StateManager

# 导入组件
from components.chat import show_chat_interface, show_sidebar
from components.agent import show_agent_interface
from components.knowledge_graph import render_knowledge_graph, show_triplet_management
from components.settings import show_model_settings, show_prompt_settings

# 导入样式
from styles.css import MAIN_CSS

# 设置页面配置
st.set_page_config(
    page_title="Gridseek - 智能对话系统",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 应用CSS样式
st.markdown(MAIN_CSS, unsafe_allow_html=True)


def initialize_app():
    """初始化应用"""
    # 初始化session state
    StateManager.init_session_state()
    
    # 加载聊天历史
    SessionManager.load_chat_history()
    
    # 如果没有会话，创建一个默认会话
    if not st.session_state.sessions:
        st.session_state.sessions = {"会话1": []}
    
    # 如果没有当前会话，设置为第一个会话
    if not st.session_state.current_session or st.session_state.current_session not in st.session_state.sessions:
        st.session_state.current_session = list(st.session_state.sessions.keys())[0]
        st.session_state.messages = st.session_state.sessions[st.session_state.current_session]
    
    # 加载可用模型
    if not st.session_state.available_models:
        st.session_state.available_models = api_service.get_available_models()
    
    # 加载可用Agent
    if not st.session_state.available_agents:
        st.session_state.available_agents = api_service.get_available_agents()
    
    # 加载系统提示词（如果还没有加载）
    if not st.session_state.system_prompt:
        st.session_state.system_prompt = api_service.load_system_prompt()


def main():
    """主函数"""
    # 初始化应用
    initialize_app()
    
    # 显示设置对话框
    if st.session_state.get('show_model_settings', False):
        show_model_settings()
        st.session_state.show_model_settings = False
    
    if st.session_state.get('show_prompt_settings', False):
        show_prompt_settings()
        st.session_state.show_prompt_settings = False

    # 显示侧边栏
    show_sidebar()
    
    # 主内容区域
    # 根据状态显示不同界面
    if st.session_state.get('show_agent_page', False):
        # 显示Agent界面
        show_agent_interface()
    else:
        # 显示正常聊天界面
        # 主标题 - 与原始文件保持一致
        st.markdown("<h3 style='text-align: center;'>GridSeek Chat</h3>", unsafe_allow_html=True)
        
        # 显示当前模型信息 - 与原始文件保持一致
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(
                f"<div style='text-align: center; padding: 8px; background-color: #f0f2f6; border-radius: 8px; margin-bottom: 15px;'>"
                f"🤖 <strong>{st.session_state.current_model}</strong> | "
                f"🌡️ <strong>{st.session_state.temperature}</strong>"
                f"</div>", 
                unsafe_allow_html=True
            )
            
            # 显示当前提示词信息
            if st.session_state.system_prompt:
                prompt_display = st.session_state.selected_preset_prompt if st.session_state.prompt_mode == '预设' else '自定义'
                st.markdown(
                    f"<div style='text-align: center; padding: 5px; background-color: #e8f4ea; border-radius: 6px; margin-bottom: 15px; font-size: 14px;'>"
                    f"💭 <strong>{prompt_display}</strong>"
                    f"</div>",
                    unsafe_allow_html=True
                )
            
        if st.session_state.show_graph:
            # 双栏布局：聊天 + 知识图谱
            chat_col, graph_col = st.columns([1, 1])
            
            with chat_col:
                st.subheader("聊天界面")
                st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
                st.markdown('<div class="chat-column">', unsafe_allow_html=True)
                show_chat_interface()
                st.markdown('</div>', unsafe_allow_html=True)
                        
            with graph_col:
                st.subheader("知识图谱可视化")
                st.markdown('<div class="graph-column">', unsafe_allow_html=True)
                
                # 知识图谱标签页
                tab1, tab2 = st.tabs(["📊 图谱可视化", "🔧 图谱管理"])
                
                with tab1:
                    render_knowledge_graph()
                
                with tab2:
                    show_triplet_management()
                
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            # 单栏布局：仅聊天
            st.subheader("聊天界面")
            st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
            show_chat_interface()


if __name__ == "__main__":
    main()

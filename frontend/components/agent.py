# -*- coding: utf-8 -*-
"""
智能Agent组件
包含Agent选择界面和Agent聊天界面
"""

import streamlit as st
import requests
from datetime import datetime
from services.api_service import api_service
from styles.css import AGENT_CSS


def show_agent_interface():
    """显示Agent界面"""
    st.markdown(AGENT_CSS, unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>智能Agent</h2>", unsafe_allow_html=True)
    
    st.divider()
    
    # 如果还没有选择Agent，显示Agent选择界面
    if not st.session_state.selected_agent:
        _show_agent_selection()
    else:
        # 显示Agent聊天界面
        _show_agent_chat()


def _show_agent_selection():
    """显示Agent选择界面"""
    st.markdown("<h3 style='text-align: center; color: #4a5568; margin-bottom: 30px;'>选择专业AI智能体</h3>", unsafe_allow_html=True)
    
    # 创建Agent选择网格
    if st.session_state.available_agents:
        # 每行显示一个Agent
        for agent in st.session_state.available_agents:
            with st.container():
                col1, col2, col3 = st.columns([1, 6, 1])
                with col2:
                    # 判断Agent状态
                    agent_tools = agent.get('tools', [])
                    needs_api_key = any(tool in ['OpenWeatherMapTool', 'SerpApiSearch'] for tool in agent_tools)
                    is_available = 'PythonREPLTool' in agent_tools or not needs_api_key
                    
                    status_text = "✅ 可用" if is_available else "⚙️ 需配置API"
                    status_class = "status-available" if is_available else "status-needs-config"
                    
                    # Agent卡片
                    st.markdown(f"""
                        <div class='agent-card'>
                            <h4 style='color: #2d3748; margin-bottom: 12px;'>
                                🤖 {agent['description']}
                                <span class='agent-status {status_class}'>{status_text}</span>
                            </h4>
                            <p style='color: #4a5568; margin-bottom: 8px;'><strong>Agent名称:</strong> {agent['name']}</p>
                            <p style='color: #4a5568; margin-bottom: 16px;'><strong>专业工具:</strong> {', '.join(agent['tools'])}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # 选择按钮（恢复原来的渐变样式）
                    st.markdown('<div class="agent-select-button">', unsafe_allow_html=True)
                    if st.button(f"🚀 选择 {agent['description']}", 
                               key=f"select_agent_{agent['name']}", 
                               use_container_width=True):
                        st.session_state.selected_agent = agent
                        st.session_state.agent_session_id = f"agent_{agent['name']}_{int(datetime.now().timestamp())}"
                        st.session_state.agent_messages = []
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.error("暂时无法加载Agent列表，请稍后重试。")
        col1, col2, col3 = st.columns([2, 3, 2])
        with col2:
            if st.button("🔄 重新加载Agent列表", 
                       use_container_width=True,
                       type="primary"):
                st.session_state.available_agents = api_service.get_available_agents()
                st.rerun()


def _show_agent_chat():
    """显示Agent聊天界面"""
    agent = st.session_state.selected_agent
    
    # 显示当前Agent信息
    st.markdown(f"""
        <div style='text-align: center; padding: 10px; background-color: #e8f4ea; border-radius: 8px; margin-bottom: 15px;'>
            <h4>🤖 {agent['description']}</h4>
            <p><strong>专业工具:</strong> {', '.join(agent['tools'])}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # 更换Agent按钮（样式类似新建会话，但更宽）
    col1, col2, col3 = st.columns([1, 8, 1])
    with col2:
        st.markdown("""
        <style>
        .wide-agent-button > button {
            background-color: #ff4b4b !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.6rem 1.5rem !important;
            font-weight: 600 !important;
            width: 100% !important;
            transition: all 0.3s ease !important;
        }
        .wide-agent-button > button:hover {
            background-color: #ff6b6b !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px rgba(255, 75, 75, 0.3) !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="wide-agent-button">', unsafe_allow_html=True)
        if st.button("🔄 更换Agent", 
                   key="change_agent_btn",
                   help="选择其他Agent",
                   use_container_width=True):
            st.session_state.selected_agent = None
            st.session_state.agent_session_id = None
            st.session_state.agent_messages = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # 创建聊天容器
    with st.container(height=500, border=True):
        # 显示Agent聊天历史
        for message in st.session_state.agent_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Agent输入框
    user_input = st.chat_input("向Agent提问...")
    
    if user_input:
        # 添加用户消息到session state
        st.session_state.agent_messages.append({"role": "user", "content": user_input})
        
        # 添加思考状态的临时消息
        st.session_state.agent_messages.append({"role": "assistant", "content": "🤔 AI思考中..."})
        
        # 立即重新运行以显示用户消息和思考状态
        st.rerun()
    
    # 处理Agent响应（只在有新消息且最后一条是思考状态时执行）
    if (len(st.session_state.agent_messages) >= 2 and 
        st.session_state.agent_messages[-1]["content"] == "🤔 AI思考中..." and
        st.session_state.agent_messages[-2]["role"] == "user"):
        
        # 获取用户的最新消息
        latest_user_message = st.session_state.agent_messages[-2]["content"]
        
        try:
            # 根据当前使用的Agent来选择提示词
            curr_agent_prompt = 'default'
            if agent['name'] == "weather_reporter_agent":
                curr_agent_prompt = "weather_query"

            # 调用Agent API
            response = requests.post(
                'http://localhost:8000/api/agent/agent/run',
                json={
                    'agent_name': agent['name'],
                    'user_input': latest_user_message,
                    'session_id': st.session_state.agent_session_id,
                    'llm_model_name': st.session_state.current_model,
                    'system_prompt_name': curr_agent_prompt,
                    'memory_window': 10
                },
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                if result['status'] == 'success':
                    full_response = result['result']
                else:
                    full_response = f"❌ Agent执行失败: {result.get('error', '未知错误')}"
            else:
                full_response = f"❌ API请求失败: {response.status_code}"
            
        except Exception as e:
            full_response = f"❌ 请求失败: {str(e)}"
        
        # 替换思考状态为实际响应
        st.session_state.agent_messages[-1] = {"role": "assistant", "content": full_response}
        
        # 重新运行以显示最终响应
        st.rerun()

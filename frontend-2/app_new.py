# 在文件最开头添加这些行
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
import streamlit.components.v1 as components
import json
from datetime import datetime
import requests
import os
import re # Added for graph template handling
from streamlit_modal import Modal
from backend.core.prompt_manager import PromptManager

prompt_manager = PromptManager()
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
#     {
#         "name": "weather_query",
#         "prompt": """你是一个辅助查询天气的AI助手。你擅长数据分析、信息搜集和信息总结。
#
# 你的工作方式：
# 1. 把我的天气查询翻译为英文，然后调用工具进行查询，最终将查询结果翻译成中文返回给我。
# 2. 基于信息和数据进行搜集汇总
# 3. 提供清晰的天气查询结果
#
# 一定要牢记上述中英文的转换流程。""",
#         "description": "学术风格的专业解答"
#     }
]

# 模型设置对话框
@st.dialog("模型设置")
def show_model_settings():
    # 添加一些上边距
    st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
    
    
    # 使用容器来添加内边距
    with st.container():
        st.markdown('<div style="padding: 0 20px;">', unsafe_allow_html=True)
        
        # 显示连接状态
        is_connected, status_msg = check_model_connectivity()
        if is_connected:
            st.success(f"✅ {status_msg}")
        else:
            st.error(f"❌ {status_msg}")
        
        # 添加一些间距
        st.markdown('<div style="height: 25px;"></div>', unsafe_allow_html=True)
        
        # 模型选择器
        if st.session_state.available_models:
            model_options = [model["model_name"] for model in st.session_state.available_models]
            model_descriptions = {model["model_name"]: model["description"] 
                                for model in st.session_state.available_models}
            
            # 确保当前模型在可用模型列表中
            if st.session_state.current_model not in model_options:
                st.session_state.current_model = model_options[0] if model_options else "gpt-4o-mini"
            
            # 使用容器来组织模型选择相关的元素
            with st.container():
                selected_model = st.selectbox(
                    "选择 AI 模型",
                    options=model_options,
                    index=model_options.index(st.session_state.current_model) if st.session_state.current_model in model_options else 0,
                    format_func=lambda x: f"{x} ({model_descriptions.get(x, '').split(',')[0]})",
                    help="选择用于对话的 AI 模型"
                )
                
                # 当模型选择发生变化时
                if selected_model != st.session_state.current_model:
                    change_model(selected_model)
                
                # 显示当前模型的详细描述
                if selected_model in model_descriptions:
                    st.markdown('<div style="margin: 15px 0;">', unsafe_allow_html=True)
                    st.info(f"📝 {model_descriptions[selected_model]}")
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # 添加一些间距
            st.markdown('<div style="height: 25px;"></div>', unsafe_allow_html=True)
            
            # 温度调节器
            with st.container():
                st.markdown('<div style="margin: 20px 0;">', unsafe_allow_html=True)
                new_temperature = st.slider(
                    "创造性 (Temperature)",
                    min_value=0.0,
                    max_value=1.0,
                    value=st.session_state.temperature,
                    step=0.1,
                    help="较低的值让回答更确定，较高的值让回答更具创造性"
                )
                st.markdown('</div>', unsafe_allow_html=True)
                
                # 当温度发生变化时
                if new_temperature != st.session_state.temperature:
                    change_temperature(new_temperature)
            
            # 添加一些间距
            st.markdown('<div style="height: 25px;"></div>', unsafe_allow_html=True)
            
            # 刷新模型列表按钮
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown('<div style="margin: 20px 0;">', unsafe_allow_html=True)
                if st.button("🔄 刷新模型列表", 
                           help="重新从后端获取可用模型",
                           use_container_width=True):
                    with st.spinner("正在加载模型列表..."):
                        load_available_models()
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("无法加载模型列表，请检查后端连接。")
            st.markdown('<div style="margin: 20px 0;">', unsafe_allow_html=True)
            if st.button("🔄 重试加载", 
                       help="重新尝试加载模型列表",
                       use_container_width=True):
                load_available_models()
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# 提示词设置对话框
@st.dialog("提示词设置")
def show_prompt_settings():
    # 添加一些上边距
    st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
    
    
    # 使用容器来添加内边距
    with st.container():
        st.markdown('<div style="padding: 0 20px;">', unsafe_allow_html=True)
        
        # 提示词模式选择
        st.markdown('<div style="margin: 20px 0;">', unsafe_allow_html=True)
        prompt_mode = st.radio(
            "选择提示词模式",
            ["预设", "自定义"],
            key="prompt_mode_radio",
            help="选择使用预设提示词或自定义提示词",
            horizontal=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 更新session state中的prompt_mode
        if prompt_mode != st.session_state.prompt_mode:
            st.session_state.prompt_mode = prompt_mode
            
        # 添加一些间距
        st.markdown('<div style="height: 25px;"></div>', unsafe_allow_html=True)
            
        if prompt_mode == "预设":
            # 预设提示词选择
            with st.container():
                preset_options = {prompt["name"]: prompt for prompt in PRESET_PROMPTS}
                selected_preset = st.selectbox(
                    "选择预设提示词",
                    options=list(preset_options.keys()),
                    index=list(preset_options.keys()).index(st.session_state.selected_preset_prompt),
                    format_func=lambda x: f"{x} - {preset_options[x]['description']}"
                )
                
                # 更新选中的预设提示词
                if selected_preset != st.session_state.selected_preset_prompt:
                    st.session_state.selected_preset_prompt = selected_preset
                    st.session_state.system_prompt = preset_options[selected_preset]["prompt"]
                    # 自动保存到后端
                    with st.spinner("正在保存提示词..."):
                        success, message = update_system_prompt(st.session_state.system_prompt)
                        if success:
                            st.success("✅ 提示词已自动保存", icon="✅")
                        else:
                            st.error(f"❌ 自动保存失败: {message}", icon="❌")
                
                # 显示当前预设提示词的内容
                if st.session_state.system_prompt:
                    st.markdown('<div style="margin: 25px 0;">', unsafe_allow_html=True)
                    with st.expander("查看当前提示词", expanded=False):
                        st.text_area(
                            "当前生效的系统提示词",
                            value=st.session_state.system_prompt,
                            disabled=True,
                            height=150
                        )
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            # 自定义提示词输入
            with st.container():
                st.markdown('<div style="margin: 20px 0;">', unsafe_allow_html=True)
                custom_prompt = st.text_area(
                    "输入自定义提示词",
                    value=st.session_state.system_prompt,
                    height=200,
                    help="输入自定义的系统提示词，用于指导AI的回答方式",
                    placeholder="在这里输入自定义提示词..."
                )
                st.markdown('</div>', unsafe_allow_html=True)
                
                # 更新自定义提示词
                if custom_prompt != st.session_state.system_prompt:
                    st.session_state.system_prompt = custom_prompt
                    # 自动保存到后端
                    if custom_prompt.strip():  # 只有当提示词不为空时才保存
                        with st.spinner("正在保存提示词..."):
                            success, message = update_system_prompt(st.session_state.system_prompt)
                            if success:
                                st.success("✅ 提示词已自动保存", icon="✅")
                            else:
                                st.error(f"❌ 自动保存失败: {message}", icon="❌")
        
        # 添加一些间距
        st.markdown('<div style="height: 25px;"></div>', unsafe_allow_html=True)
        
        # 提示词操作按钮
        st.markdown('<div style="margin: 20px 0;">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑 清空", 
                       help="清除当前的系统提示词",
                       use_container_width=True):
                st.session_state.system_prompt = ""
                st.session_state.selected_preset_prompt = "default"
                # 清空后也要同步到后端
                with st.spinner("正在清空提示词..."):
                    success, message = update_system_prompt("")
                    if success:
                        st.success("✅ 提示词已清空并同步到后端！")
                    else:
                        st.warning("提示词已清空，但同步到后端失败")
                st.rerun()
        with col2:
            if st.button("🧪 测试", 
                       help="测试当前提示词是否生效",
                       use_container_width=True):
                with st.spinner("正在测试提示词..."):
                    test_prompt = "你是谁？请介绍一下你自己的角色。"
                    try:
                        # 使用临时会话ID进行测试
                        test_session_id = f"test_session_{int(datetime.now().timestamp())}"
                        
                        test_response = ""
                        for chunk in stream_chat_response(
                            user_message=test_prompt,
                            session_id=test_session_id,
                            model_name=st.session_state.current_model,
                            temperature=st.session_state.temperature,
                            system_prompt=st.session_state.system_prompt
                        ):
                            test_response += chunk
                        
                        if test_response:
                            st.success("提示词测试成功！")
                            with st.expander("查看测试结果", expanded=True):
                                st.markdown("**测试问题：**\n" + test_prompt)
                                st.markdown("**AI回答：**\n" + test_response)
                        else:
                            st.error("测试失败: 未获得有效响应")
                    except Exception as e:
                        st.error(f"测试出错: {str(e)}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# 设置页面配置
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded"
)

# 添加自定义CSS样式
st.markdown("""
<style>
/* 主内容区域样式 */
.main .block-container {
    padding-top: 1rem;
}

/* 自定义按钮样式 */
.stButton > button {
    border-radius: 8px;
    border: 1px solid #ddd;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    background-color: #f0f2f5;
    border-color: #ff4b4b;
}



/* 右侧边栏收起按钮样式 */
div[data-testid="column"]:nth-child(2) .stButton > button[data-testid*="collapse"] {
    width: 30px;
    height: 30px;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 6px;
}

div[data-testid="column"]:nth-child(2) .stButton > button[data-testid*="collapse"]:hover {
    background-color: #e9ecef;
    border-color: #adb5bd;
}

/* 输入框样式优化 */
.stTextInput > div > div > input {
    border-radius: 8px;
    border: 1px solid #ddd;
    padding: 10px 12px;
    font-size: 14px;
}

.stTextInput > div > div > input:focus {
    border-color: #ff4b4b;
    box-shadow: 0 0 0 1px #ff4b4b;
}

/* 确保标题和按钮在同一行对齐 */
div[data-testid="column"]:nth-child(2) h3 {
    margin-bottom: 0;
    line-height: 1.2;
}

/* 分割线样式 */
hr {
    margin: 1rem 0;
    border: none;
    height: 1px;
    background-color: #e9ecef;
}

/* 响应式设计 */
@media (max-width: 1200px) {
    .main .block-container {
        padding-right: 1rem !important;
    }
}

@media (max-width: 768px) {
    .main .block-container {
        padding-right: 1rem !important;
    }
}

/* 固定按钮样式 */
.fixed-button {
    position: fixed;
    right: 0;
    top: 50%;
    transform: translateY(-50%);
    background: white;
    border: 1px solid #ddd;
    border-right: none;
    border-radius: 4px 0 0 4px;
    padding: 10px;
    cursor: pointer;
    writing-mode: vertical-lr;
    box-shadow: -2px 0 5px rgba(0,0,0,0.1);
    z-index: 1000;
    transition: all 0.3s ease;
}

.fixed-button:hover {
    background: #f0f2f5;
    box-shadow: -3px 0 8px rgba(0,0,0,0.15);
}

/* 侧边栏样式 */
[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    padding-top: 0.5rem !important;
}

/* 隐藏侧边栏滚动条 */
[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    overflow-y: hidden !important;
}

[data-testid="stSidebarNav"] {
    background-color: #FFFFFF !important;
}

[data-testid="stSidebar"]::before {
    display: none;
}

[data-testid="stSidebar"] [data-testid="stMarkdown"] {
    padding: 0.3rem !important;
    margin-top: 0 !important;
}

/* 侧边栏标题样式 */
.chat-manager-title {
    margin: 0.2rem 0 0.8rem 0 !important;
    padding: 0.5rem 0 !important;
    text-align: center;
    color: #0d8299;
    font-size: 1.5rem !important;
    font-weight: 600;
}

/* 会话列表容器样式 */
[data-testid="stVerticalBlock"] {
    gap: 0.3rem !important;
    padding-top: 0.2rem !important;
}

/* 会话按钮样式 */
.stButton > button {
    width: 100%;
    margin: 3px 0;
    border: 1px solid #e0e0e0;
    background-color: white;
    transition: all 0.2s;
    padding: 0.4rem !important;
    height: auto !important;
}

.stButton > button:hover {
    background-color: #f0f2f5;
    border-color: #0d8299;
}

/* 历史会话标题 */
.history-title {
    margin: 0.8rem 0;
    font-size: 1.2rem;
    color: #333;
}

/* 分隔线样式 */
hr {
    margin: 0.8rem 0 !important;
}

/* 当前选中的会话按钮样式 */
.current-session > button {
    border-color: #0d8299 !important;
    background-color: #e8f4f8 !important;
}

/* 删除按钮样式 */
.delete-btn > button {
    background-color: transparent;
    border: none;
    color: #ff4b4b;
    padding: 0.3rem !important;
}

.delete-btn > button:hover {
    background-color: #ffe5e5;
    color: #ff0000;
}

/* 管理按钮容器样式 */
.manage-buttons-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.4rem;
    padding: 0.4rem;
}

/* 管理按钮样式 */
.manage-button {
    width: 90% !important;
    margin: 0.2rem 0 !important;
    height: 2.3rem !important;
    border-radius: 0.5rem !important;
}

/* 会话列表中的按钮样式 */
.session-list .stButton > button {
    margin-bottom: 0.6rem !important;
}

/* Logo样式 */
[data-testid="stImage"] {
    margin-top: 0.2rem !important;
    padding-top: 0.2rem !important;
}

[data-testid="stImage"] img {
    margin: 0.5rem !important;
}

/* 知识图谱按钮样式 */
.knowledge-graph-btn {
    margin-top: 1rem;
    margin-bottom: 1rem;
    text-align: center;
}

/* 知识图谱容器样式 */
.knowledge-graph-container {
    width: 100%;
    height: 500px;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    margin-top: 1rem;
    overflow: hidden;
}

/* 分栏样式 */
.chat-column {
    padding-right: 10px;
}

.graph-column {
    border-left: 1px solid #e0e0e0;
    padding-left: 10px;
}

/* 知识图谱按钮组样式 */
[data-testid="stSidebar"] div:has(> #knowledge_graph_btn) {
    margin-bottom: 0.3rem !important;
}

[data-testid="stSidebar"] div:has(> #test_triplet_btn) {
    margin-top: 0 !important;
}

/* 聊天容器样式 */
[data-testid="stVerticalBlock"] > div:has(> [data-testid="chat-message-container"]) {
    overflow-y: auto !important;
    padding-right: 1rem !important;
}

/* 聊天消息容器样式 */
[data-testid="chat-message-container"] {
    margin-bottom: 1rem !important;
    background-color: #ffffff;
    border-radius: 8px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    transition: all 0.2s ease;
}

[data-testid="chat-message-container"]:hover {
    box-shadow: 0 2px 4px rgba(0,0,0,0.15);
}

/* 滚动条样式 */
[data-testid="stVerticalBlock"] > div:has(> [data-testid="chat-message-container"])::-webkit-scrollbar {
    width: 6px;
}

[data-testid="stVerticalBlock"] > div:has(> [data-testid="chat-message-container"])::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 3px;
}

[data-testid="stVerticalBlock"] > div:has(> [data-testid="chat-message-container"])::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 3px;
}

[data-testid="stVerticalBlock"] > div:has(> [data-testid="chat-message-container"])::-webkit-scrollbar-thumb:hover {
    background: #a8a8a8;
}

/* 聊天输入框样式优化 */
.stChatInputContainer {
    position: sticky !important;
    bottom: 0 !important;
    background-color: #ffffff !important;
    padding: 1rem 0 !important;
    margin-top: 1rem !important;
    border-top: 1px solid #e0e0e0 !important;
}

/* 聊天容器边框样式 */
[data-testid="stVerticalBlock"] > div:has(> [data-testid="chat-message-container"]) {
    border: 1px solid #e0e0e0 !important;
    border-radius: 8px !important;
    padding: 1rem !important;
    background-color: #f8f9fa !important;
}

/* 聊天界面容器样式 */
.chat-container {
    display: flex !important;
    flex-direction: column !important;
    height: 600px !important;
    position: relative !important;
}

.messages-container {
    flex-grow: 1 !important;
    overflow-y: auto !important;
    padding: 1rem !important;
    margin-bottom: 60px !important; /* 为输入框留出空间 */
}

/* 输入框容器样式 */
.input-container {
    position: absolute !important;
    bottom: 0 !important;
    left: 0 !important;
    right: 0 !important;
    padding: 10px !important;
    background-color: white !important;
    border-top: 1px solid #e0e0e0 !important;
}

.stChatInputContainer {
    margin: 0 !important;
    padding: 0 !important;
}

</style>
""", unsafe_allow_html=True)

st.title("Gridseek")

# 初始化session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'sessions' not in st.session_state:
    st.session_state.sessions = {}  # 使用字典而不是列表
if 'current_session' not in st.session_state:
    st.session_state.current_session = None
if 'show_graph' not in st.session_state:
    st.session_state.show_graph = True  # 默认显示知识图谱
if 'triplets' not in st.session_state:
    st.session_state.triplets = []
if 'available_models' not in st.session_state:
    st.session_state.available_models = []
if 'current_model' not in st.session_state:
    st.session_state.current_model = "gpt-4o-mini"  # 默认模型
if 'temperature' not in st.session_state:
    st.session_state.temperature = 0.7
if 'system_prompt' not in st.session_state:
    # 初始化为空字符串，稍后在main函数中加载
    st.session_state.system_prompt = ""
if 'prompt_mode' not in st.session_state:
    st.session_state.prompt_mode = "预设"  # 默认使用预设提示词
if 'selected_preset_prompt' not in st.session_state:
    st.session_state.selected_preset_prompt = "default"  # 默认使用default
if 'show_model_settings' not in st.session_state:
    st.session_state.show_model_settings = False
if 'show_prompt_settings' not in st.session_state:
    st.session_state.show_prompt_settings = False

# Agent相关状态
if 'show_agent_page' not in st.session_state:
    st.session_state.show_agent_page = False
if 'selected_agent' not in st.session_state:
    st.session_state.selected_agent = None
if 'available_agents' not in st.session_state:
    st.session_state.available_agents = []
if 'agent_session_id' not in st.session_state:
    st.session_state.agent_session_id = None
if 'agent_messages' not in st.session_state:
    st.session_state.agent_messages = []

# 初始化Modal对象
# model_settings_modal = Modal("模型设置", key="model_settings_modal")
# prompt_settings_modal = Modal("提示词设置", key="prompt_settings_modal")

def toggle_knowledge_graph():
    """切换知识图谱显示状态"""
    st.session_state.show_graph = not st.session_state.show_graph

def load_available_models():
    """从后端加载可用模型列表"""
    try:
        response = requests.get('http://localhost:8000/models', timeout=10)
        response.raise_for_status()
        data = response.json()
        st.session_state.available_models = data.get('models', [])
        return True
    except requests.RequestException as e:
        st.error(f"加载模型列表失败: {e}")
        # 设置默认模型列表作为备选
        st.session_state.available_models = [
            {"model_name": "gpt-4o-mini", "description": "OpenAI GPT-4o-mini, 性能优秀，成本较低。", "provider": "GPT"},
            {"model_name": "deepseek-chat", "description": "DeepSeek Chat, 中文表现优秀的开源模型。", "provider": "DeepSeek"}
        ]
        return False
    except Exception as e:
        st.error(f"处理模型列表时出错: {e}")
        return False

def change_model(new_model):
    """切换当前使用的模型"""
    st.session_state.current_model = new_model
    st.toast(f"已切换到模型: {new_model}", icon="🤖")

def change_temperature(new_temperature):
    """更改模型温度参数"""
    st.session_state.temperature = new_temperature

def check_model_connectivity():
    """检查模型连接状态"""
    try:
        response = requests.get('http://localhost:8000/models', timeout=5)
        response.raise_for_status()
        return True, "后端连接正常"
    except requests.RequestException as e:
        return False, f"后端连接失败: {e}"

def stream_chat_response(user_message, session_id, model_name, temperature, system_prompt):
    """流式聊天响应"""
    try:
        response = requests.post(
            'http://localhost:8000/qa/chat',
            json={
                'user_message': user_message,
                'session_id': session_id,
                'model_name': model_name,
                'temperature': temperature,
                'system_prompt_name': 'current'  # 使用当前设置的系统提示词
            },
            stream=True,
            timeout=60
        )
        response.raise_for_status()
        
        full_response = ""
        for line in response.iter_lines(decode_unicode=True):
            if line.strip():
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])
                        if data.get('type') == 'content':  # 修复：后端返回的是'content'而不是'chunk'
                            chunk = data.get('content', '')
                            if chunk:
                                full_response += chunk
                                yield chunk
                        elif data.get('type') == 'end':  # 修复：后端返回的是'end'而不是'final'
                            break
                        elif data.get('type') == 'error':
                            raise Exception(data.get('error', '未知错误'))  # 修复：错误信息在'error'字段
                    except json.JSONDecodeError:
                        continue
        
        return full_response
        
    except requests.RequestException as e:
        raise Exception(f"请求失败: {e}")
    except Exception as e:
        raise Exception(f"处理响应时出错: {e}")

def get_conversation_history(session_id):
    """获取会话历史"""
    try:
        response = requests.get(f'http://localhost:8000/qa/memory/{session_id}', timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') == 'success':
            return data.get('messages', []), data.get('current_model')
        else:
            return [], None
    except requests.RequestException as e:
        st.error(f"获取会话历史失败: {e}")
        return [], None

def clear_conversation_history(session_id):
    """清空会话历史"""
    try:
        response = requests.delete(f'http://localhost:8000/qa/memory/{session_id}', timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') == 'success':
            return True
        else:
            st.error(f"清空历史失败: {data.get('error', '未知错误')}")
            return False
    except requests.RequestException as e:
        st.error(f"清空会话历史失败: {e}")
        return False

def load_system_prompt():
    """加载系统提示词"""
    try:
        response = requests.get('http://localhost:8000/api/prompt/', timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('system_prompt', '')
    except requests.RequestException as e:
        # 静默处理，不显示错误，防止影响应用启动
        return ''
    except Exception as e:
        # 处理其他异常
        return ''

def update_system_prompt(prompt):
    """更新系统提示词"""
    try:
        response = requests.post(
            'http://localhost:8000/api/prompt/',
            json={'prompt': prompt},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get('msg'):
            return True, data.get('msg')
        else:
            return False, "更新失败"
    except requests.RequestException as e:
        return False, f"更新失败: {e}"

def load_available_agents():
    """加载可用的Agent列表"""
    try:
        response = requests.get('http://localhost:8000/api/agent/agents', timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('agents', [])
    except requests.RequestException as e:
        st.error(f"加载Agent列表失败: {e}")
        return []

def run_agent_task(agent_name, user_input, session_id):
    """运行Agent任务 - 非流式版本"""
    try:
        response = requests.post(
            'http://localhost:8000/api/agent/agent/run',
            json={
                'agent_name': agent_name,
                'user_input': user_input,
                'session_id': session_id,
                'llm_model_name': st.session_state.current_model,
                'system_prompt_name': 'default',
                'memory_window': 10
            },
            timeout=60
        )
        response.raise_for_status()
        
        result = response.json()
        if result['status'] == 'success':
            return result['result']
        else:
            raise Exception(result.get('error', '未知错误'))
        
    except requests.RequestException as e:
        raise Exception(f"Agent任务执行失败: {e}")
    except Exception as e:
        raise Exception(f"处理Agent响应时出错: {e}")

def save_chat_history():
    """保存聊天历史"""
    try:
        chat_history = {}
        for session_id, messages in st.session_state.sessions.items():
            chat_history[session_id] = messages
            
        with open('chat_history.json', 'w', encoding='utf-8') as f:
            json.dump(chat_history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"保存聊天历史失败：{str(e)}")

def load_chat_history():
    """加载聊天历史"""
    try:
        with open('chat_history.json', 'r', encoding='utf-8') as f:
            chat_history = json.load(f)
            
            # 检查是否是嵌套结构（包含sessions键）
            if isinstance(chat_history, dict) and 'sessions' in chat_history:
                # 使用嵌套结构中的sessions部分
                st.session_state.sessions = chat_history['sessions']
            elif isinstance(chat_history, dict):
                # 直接使用字典格式
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

def create_new_session():
    """创建新会话"""
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
    save_chat_history()

def switch_session(session_id):
    """切换会话"""
    st.session_state.current_session = session_id
    # 从后端加载会话历史
    messages, current_model = get_conversation_history(session_id)
    if messages:
        st.session_state.messages = messages
        st.session_state.sessions[session_id] = messages
        if current_model:
            st.session_state.current_model = current_model
    else:
        st.session_state.messages = st.session_state.sessions.get(session_id, [])
    
    # 如果当前在Agent界面，自动关闭Agent界面
    if st.session_state.show_agent_page:
        st.session_state.show_agent_page = False
        st.session_state.selected_agent = None
        st.session_state.agent_session_id = None
        st.session_state.agent_messages = []

def clear_session():
    """清空当前会话"""
    if st.session_state.current_session:
        # 从后端清除会话历史
        success = clear_conversation_history(st.session_state.current_session)
        if success:
            st.session_state.messages = []
            st.session_state.sessions[st.session_state.current_session] = []
            save_chat_history()
            st.success("会话已清空")

def delete_session(session_id):
    """删除当前会话"""
    if st.session_state.current_session == session_id:
        st.session_state.current_session = None
        st.session_state.messages = []
    st.session_state.sessions.pop(session_id, None)
    save_chat_history()

def extract_and_store_triplets(text: str):
    """从文本中提取三元组并存储到session_state"""
    try:
        # 打印调试信息
        st.write(f"正在从文本中提取三元组，文本长度: {len(text)}")
        
        # 确保text不为空
        if not text or len(text.strip()) < 10:
            st.warning("文本内容过短，无法提取有效的三元组")
            return False
            
        # 显示正在处理的状态
        with st.spinner("正在提取知识三元组..."):
            # 确保使用正确的API端点
            api_url = 'http://localhost:8000/api/kg/extract'
            st.write(f"调用API: {api_url}")
            
            # 准备请求数据并打印
            request_data = {'text': text}
            st.write(f"请求数据示例: {{'text': '{text[:50]}...'}}")
            
            # 发送请求
            response = requests.post(
                api_url,
                json=request_data,
                timeout=30  # 增加超时时间
            )
            
            # 检查响应状态
            response.raise_for_status()
            st.write(f"API响应状态码: {response.status_code}")
            
            # 解析响应数据
            data = response.json()
            st.write(f"API响应数据: {data}")
            
            # 提取三元组
            new_triplets = data.get("triples", [])
            st.write(f"提取到的三元组数量: {len(new_triplets)}")
            
            if new_triplets:
                # 获取现有三元组
                existing_triplets = st.session_state.get('triplets', [])
                st.write(f"现有三元组数量: {len(existing_triplets)}")
                
                # 将新的三元组添加进去，同时去重
                added_count = 0
                for triplet in new_triplets:
                    if triplet not in existing_triplets:
                        existing_triplets.append(triplet)
                        added_count += 1
                
                st.write(f"新增三元组数量: {added_count}")
                st.session_state.triplets = existing_triplets
                st.toast(f"提取到 {len(new_triplets)} 个知识三元组，新增 {added_count} 个！", icon="✨")
                return True  # 表示有新的三元组被添加
            else:
                st.warning("未能从文本中提取到任何三元组")
                return False  # 表示没有新的三元组

    except requests.RequestException as e:
        st.error(f"提取知识三元组失败：{e}")
        st.write(f"请求异常详情: {str(e)}")
        return False
    except Exception as e:
        st.error(f"处理三元组时出错: {e}")
        st.write(f"异常详情: {str(e)}")
        import traceback
        st.write(f"异常堆栈: {traceback.format_exc()}")
        return False
    finally:
        # 移除调试信息（生产环境中应该注释掉这些调试输出）
        # 这里我们暂时保留，便于排查问题
        pass

# 添加一个测试函数，用于直接测试三元组提取功能
def test_triplet_extraction():
    """测试三元组提取功能"""
    st.subheader("三元组提取测试")
    test_text = st.text_area(
        "输入测试文本", 
        value="人工智能是计算机科学的一个分支，它致力于创造能够模拟人类智能的机器。",
        height=150
    )
    
    if st.button("测试提取三元组"):
        if test_text:
            extract_and_store_triplets(test_text)
        else:
            st.error("请输入测试文本")

def test_model_switching():
    """测试模型切换功能"""
    st.subheader("🤖 模型切换测试")
    
    # 显示当前模型信息
    st.info(f"当前模型: {st.session_state.current_model}")
    st.info(f"当前温度: {st.session_state.temperature}")
    
    # 测试问题
    test_question = st.text_input(
        "测试问题:",
        value="请简单介绍一下你自己",
        help="输入一个测试问题来验证模型切换是否生效"
    )
    
    if st.button("测试当前模型", key="test_current_model"):
        if test_question:
            with st.spinner(f"正在使用 {st.session_state.current_model} 回答..."):
                try:
                    # 使用临时会话ID进行测试
                    test_session_id = f"test_session_{int(datetime.now().timestamp())}"
                    
                    test_response = ""
                    for chunk in stream_chat_response(
                        user_message=test_question,
                        session_id=test_session_id,
                        model_name=st.session_state.current_model,
                        temperature=st.session_state.temperature,
                        system_prompt=st.session_state.system_prompt
                    ):
                        test_response += chunk
                    
                    if test_response:
                        st.success(f"✅ 模型 {st.session_state.current_model} 响应成功!")
                        st.markdown(f"**回答:** {test_response}")
                    else:
                        st.error("❌ 模型响应失败: 未获得有效响应")
                        
                except Exception as e:
                    st.error(f"❌ 测试失败: {e}")
        else:
            st.warning("请输入测试问题")
    
    # 快速切换测试
    st.subheader("快速模型切换测试")
    if st.session_state.available_models:
        cols = st.columns(len(st.session_state.available_models))
        for i, model in enumerate(st.session_state.available_models):
            with cols[i]:
                model_name = model["model_name"]
                is_current = model_name == st.session_state.current_model
                if st.button(
                    f"{'✅' if is_current else '🔄'} {model_name}",
                    key=f"quick_switch_{model_name}",
                    help=f"切换到 {model_name}",
                    type="primary" if is_current else "secondary"
                ):
                    if not is_current:
                        change_model(model_name)
                        st.rerun()

def generate_dynamic_graph_html(triplets: list) -> str:
    """根据三元组动态生成graph.html内容"""
    if not triplets:
        return "<h3>当前还没有可显示的知识三元组。</h3>"
        
    # 为节点和边生成随机颜色
    import random
    def get_random_color():
        # 生成柔和的颜色
        r = random.randint(100, 200)
        g = random.randint(100, 200)
        b = random.randint(100, 200)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    # 为实体类型分配固定颜色
    entity_colors = {}
    
    nodes_set = set()
    nodes_js = []
    edges_js = []
    
    # 首先收集所有唯一的实体
    for triplet in triplets:
        h, r, t = triplet.get('h'), triplet.get('r'), triplet.get('t')
        if not all([h, r, t]):
            continue
            
        nodes_set.add(h)
        nodes_set.add(t)
    
    # 为每个实体分配颜色
    for entity in nodes_set:
        if entity not in entity_colors:
            entity_colors[entity] = get_random_color()
    
    # 生成节点数据
    for i, entity in enumerate(nodes_set):
        color = entity_colors.get(entity, "#7DCEA0")  # 默认颜色
        border_color = color  # 边框颜色稍深
        
        # 使用实体名作为ID，避免重复
        node_id = f'"{entity}"'  # 确保ID是字符串
        nodes_js.append(f'{{id: {node_id}, label: "{entity}", title: "{entity}", ' +
                      f'color: {{ background: "{color}", border: "{border_color}" }}}}')
    
    # 生成边数据
    for i, triplet in enumerate(triplets):
        h, r, t = triplet.get('h'), triplet.get('r'), triplet.get('t')
        if not all([h, r, t]):
            continue
            
        # 使用实体名作为ID
        from_id = f'"{h}"'
        to_id = f'"{t}"'
        
        edges_js.append(f'{{from: {from_id}, to: {to_id}, arrows: "to", label: "{r}"}}')
    
    nodes_str = ",\n        ".join(nodes_js)
    edges_str = ",\n        ".join(edges_js)
    
    # 读取HTML模板文件
    try:
        # 尝试多种可能的路径
        possible_paths = [
            "graph_template.html",  # 当前目录
            "./graph_template.html",  # 显式当前目录
            "frontend-2/graph_template.html",  # 相对于项目根目录
            "./frontend-2/graph_template.html",  # 显式相对于项目根目录
            "v3_st/frontend-2/graph_template.html",  # 完整相对路径
            "./v3_st/frontend-2/graph_template.html",  # 显式完整相对路径
        ]
        
        template_content = None
        used_path = None
        
        for path in possible_paths:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                    used_path = path
                    break
            except FileNotFoundError:
                continue
        
        if not template_content:
            # 如果所有路径都失败，尝试使用graph.html作为备用
            backup_paths = [
                "graph.html",
                "./graph.html",
                "frontend-2/graph.html",
                "./frontend-2/graph.html",
                "v3_st/frontend-2/graph.html",
                "./v3_st/frontend-2/graph.html",
            ]
            
            for path in backup_paths:
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        template_content = f.read()
                        used_path = path
                        st.warning(f"使用备用模板文件: {path}")
                        break
                except FileNotFoundError:
                    continue
        
        if not template_content:
            raise FileNotFoundError("无法找到任何可用的图谱模板文件")
            
        st.success(f"成功加载模板文件: {used_path}")
            
        # 替换占位符
        # 首先检查模板中是否包含占位符
        if "{{NODES_PLACEHOLDER}}" in template_content and "{{EDGES_PLACEHOLDER}}" in template_content:
            html_content = template_content.replace("{{NODES_PLACEHOLDER}}", nodes_str)
            html_content = html_content.replace("{{EDGES_PLACEHOLDER}}", edges_str)
        else:
            # 如果没有找到占位符，尝试在适当位置插入数据
            # 这是一个备用方案，用于处理没有占位符的模板
            html_content = template_content
            
            # 寻找nodes定义的位置
            nodes_pattern = r"var\s+nodes\s*=\s*new\s+vis\.DataSet\(\s*\[\s*"
            if re.search(nodes_pattern, html_content):
                html_content = re.sub(
                    nodes_pattern + r".*?\]\s*\);",
                    f"var nodes = new vis.DataSet([{nodes_str}]);",
                    html_content,
                    flags=re.DOTALL
                )
                
            # 寻找edges定义的位置
            edges_pattern = r"var\s+edges\s*=\s*new\s+vis\.DataSet\(\s*\[\s*"
            if re.search(edges_pattern, html_content):
                html_content = re.sub(
                    edges_pattern + r".*?\]\s*\);",
                    f"var edges = new vis.DataSet([{edges_str}]);",
                    html_content,
                    flags=re.DOTALL
                )
        
        return html_content
    except FileNotFoundError as e:
        st.error(f"找不到模板文件: {str(e)}")
        return f"<h3>错误：找不到图谱模板文件。请确保图谱模板文件存在。</h3><p>尝试过的路径: {', '.join(possible_paths)}</p>"
    except Exception as e:
        st.error(f"生成图谱时出错: {e}")
        import traceback
        st.write(f"异常堆栈: {traceback.format_exc()}")
        return f"<h3>生成图谱时出错: {e}</h3>"

def render_knowledge_graph():
    """渲染知识图谱"""
    triplets = st.session_state.get('triplets', [])
    if not triplets:
        st.info("当前还没有可显示的知识三元组。")
        return
    
    st.subheader("知识图谱可视化")    
    dynamic_html = generate_dynamic_graph_html(triplets)
    components.html(dynamic_html, height=600, scrolling=True)

def show_agent_interface():
    """显示Agent界面"""
    st.markdown("<h2 style='text-align: center;'>🤖 智能Agent</h2>", unsafe_allow_html=True)
    
    # 添加Agent选择按钮的自定义样式
    st.markdown("""
        <style>
        .agent-select-button > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 12px 24px !important;
            font-weight: 600 !important;
            font-size: 16px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
        }
        
        .agent-select-button > button:hover {
            background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
        }
        
        .agent-select-button > button:active {
            transform: translateY(0px) !important;
        }
        
        .agent-card {
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            padding: 24px;
            margin: 15px 0;
            background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }
        
        .agent-card:hover {
            border-color: #667eea;
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
        }
        
        .agent-status {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            margin-left: 8px;
        }
        
        .status-available {
            background-color: #c6f6d5;
            color: #22543d;
        }
        
        .status-needs-config {
            background-color: #fed7d7;
            color: #c53030;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # 如果还没有选择Agent，显示Agent选择界面
    if not st.session_state.selected_agent:
        st.markdown("<h3 style='text-align: center; color: #4a5568; margin-bottom: 30px;'>选择专业AI智能体</h3>", unsafe_allow_html=True)
        
        # 创建Agent选择网格
        if st.session_state.available_agents:
            # 每行显示一个Agent
            for i, agent in enumerate(st.session_state.available_agents):
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
                        
                        # 选择按钮（使用自定义样式）
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
                st.markdown('<div class="agent-select-button">', unsafe_allow_html=True)
                if st.button("🔄 重新加载Agent列表", use_container_width=True):
                    st.session_state.available_agents = load_available_agents()
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        # 显示Agent聊天界面
        show_agent_chat()

def show_agent_chat():
    """显示Agent聊天界面"""
    agent = st.session_state.selected_agent
    
    # 显示当前Agent信息
    st.markdown(f"""
        <div style='text-align: center; padding: 10px; background-color: #e8f4ea; border-radius: 8px; margin-bottom: 15px;'>
            <h4>🤖 {agent['description']}</h4>
            <p><strong>专业工具:</strong> {', '.join(agent['tools'])}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # 更换Agent按钮
    col1, col2, col3 = st.columns([1, 6, 1])
    with col2:
        if st.button("更换Agent", 
                   help="选择其他Agent",
                   type="secondary",
                   use_container_width=True):
            st.session_state.selected_agent = None
            st.session_state.agent_session_id = None
            st.session_state.agent_messages = []
            st.rerun()
    
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
        # 添加用户消息
        st.session_state.agent_messages.append({"role": "user", "content": user_input})
        
        # 显示用户消息
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # 显示Agent响应
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            try:
                full_response = ""

                # # 根据当前使用的Agent来选择提示词
                # prompt_manager.set_current_system_prompt("default")
                # if agent['name'] == "weather_reporter_agent":
                #     prompt_manager.set_current_system_prompt("weather_query")
                curr_agent_prompt = 'default'
                if agent['name'] == "weather_reporter_agent":
                    curr_agent_prompt = "weather_query"

                # 调用Agent API
                response = requests.post(
                    'http://localhost:8000/api/agent/agent/run',
                    json={
                        'agent_name': agent['name'],
                        'user_input': user_input,
                        'session_id': st.session_state.agent_session_id,
                        'llm_model_name': st.session_state.current_model,
                        'system_prompt_name': curr_agent_prompt,
                        'memory_window': 10
                    },
                    timeout=60
                )
                # prompt_manager.set_current_system_prompt("default")

                if response.status_code == 200:
                    result = response.json()
                    if result['status'] == 'success':
                        full_response = result['result']
                    else:
                        full_response = f"❌ Agent执行失败: {result.get('error', '未知错误')}"
                else:
                    full_response = f"❌ API请求失败: {response.status_code}"
                
                message_placeholder.markdown(full_response)
                
                # 添加Agent响应到历史
                st.session_state.agent_messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                error_message = f"❌ 请求失败: {str(e)}"
                message_placeholder.error(error_message)
                st.session_state.agent_messages.append({"role": "assistant", "content": error_message})

def show_settings_modal():
    """显示统一的设置界面"""
    # 添加一些自定义CSS样式
    st.markdown("""
        <style>
        .settings-title {
            color: #1f1f1f;
            font-size: 1.5rem;
            font-weight: 600;
            margin: 2rem 0 1.5rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #f0f2f6;
        }
        
        .settings-section {
            background-color: #f8f9fa;
            padding: 1.2rem;
            border-radius: 8px;
            margin-bottom: 1rem;
        }
        
        .settings-divider {
            margin: 1.5rem 0;
            border: none;
            height: 1px;
            background: linear-gradient(to right, transparent, #e0e0e0, transparent);
        }
        
        /* 调整选择器样式 */
        .stSelectbox > div > div {
            background-color: white;
            border-radius: 6px;
            border: 1px solid #e0e0e0;
        }
        
        /* 按钮样式 */
        .stButton > button {
            border-radius: 6px;
            padding: 0.5rem 1rem;
            border: 1px solid #e0e0e0;
            background-color: white;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            border-color: #0d8299;
            background-color: #f0f8fa;
            transform: translateY(-1px);
        }
        </style>
    """, unsafe_allow_html=True)
    
    # 创建两列布局，使用比例控制间距，并添加间隔
    left_col, spacing, right_col = st.columns([47, 6, 47])
    
    # 左侧列：模型设置
    with left_col:
        st.markdown('<div class="settings-title">🤖 模型设置</div>', unsafe_allow_html=True)
        
        # 显示连接状态
        with st.container():
            is_connected, status_msg = check_model_connectivity()
            if is_connected:
                st.success(f"✅ {status_msg}")
            else:
                st.error(f"❌ {status_msg}")
        
        st.markdown('<div class="settings-divider"></div>', unsafe_allow_html=True)
        
        # 模型选择器
        if st.session_state.available_models:
            with st.container():
                st.markdown('<div class="settings-section">', unsafe_allow_html=True)
                model_options = [model["model_name"] for model in st.session_state.available_models]
                model_descriptions = {model["model_name"]: model["description"] 
                                    for model in st.session_state.available_models}
                
                # 确保当前模型在可用模型列表中
                if st.session_state.current_model not in model_options:
                    st.session_state.current_model = model_options[0] if model_options else "gpt-4o-mini"
                
                selected_model = st.selectbox(
                    "选择 AI 模型",
                    options=model_options,
                    index=model_options.index(st.session_state.current_model) if st.session_state.current_model in model_options else 0,
                    format_func=lambda x: f"{x} ({model_descriptions.get(x, '').split(',')[0]})",
                    help="选择用于对话的 AI 模型",
                    key="settings_model_selector"
                )
                
                # 当模型选择发生变化时
                if selected_model != st.session_state.current_model:
                    change_model(selected_model)
                
                # 显示当前模型的详细描述
                if selected_model in model_descriptions:
                    st.info(f"📝 {model_descriptions[selected_model]}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="settings-divider"></div>', unsafe_allow_html=True)
            
            # 温度调节器
            new_temperature = st.slider(
                "创造性 (Temperature)",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.temperature,
                step=0.1,
                help="较低的值让回答更确定，较高的值让回答更具创造性",
                key="settings_temperature_slider"
            )
            
            # 当温度发生变化时
            if new_temperature != st.session_state.temperature:
                change_temperature(new_temperature)
            
            st.markdown('<div class="settings-divider"></div>', unsafe_allow_html=True)
            
            # 刷新模型列表按钮
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔄 刷新模型列表", 
                           help="重新从后端获取可用模型", 
                           key="settings_refresh_models"):
                    with st.spinner("正在加载模型列表..."):
                        load_available_models()
                    st.rerun()
        else:
            st.warning("无法加载模型列表，请检查后端连接。")
            if st.button("🔄 重试加载", 
                       help="重新尝试加载模型列表", 
                       key="settings_retry_load"):
                load_available_models()
                st.rerun()
    
    # 右侧列：提示词设置
    with right_col:
        st.markdown('<div class="settings-title">💭 提示词设置</div>', unsafe_allow_html=True)
        
        # 提示词模式选择
        with st.container():
            st.markdown('<div class="settings-section">', unsafe_allow_html=True)
            prompt_mode = st.radio(
                "选择提示词模式",
                ["预设", "自定义"],
                key="settings_prompt_mode_radio",
                help="选择使用预设提示词或自定义提示词",
                horizontal=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 更新session state中的prompt_mode
        if prompt_mode != st.session_state.prompt_mode:
            st.session_state.prompt_mode = prompt_mode
            
        st.markdown('<div class="settings-divider"></div>', unsafe_allow_html=True)
            
        if prompt_mode == "预设":
            with st.container():
                st.markdown('<div class="settings-section">', unsafe_allow_html=True)
                # 预设提示词选择
                preset_options = {prompt["name"]: prompt for prompt in PRESET_PROMPTS}
                selected_preset = st.selectbox(
                    "选择预设提示词",
                    options=list(preset_options.keys()),
                    index=list(preset_options.keys()).index(st.session_state.selected_preset_prompt),
                    format_func=lambda x: f"{x} - {preset_options[x]['description']}",
                    key="settings_preset_prompt_selector"
                )
                
                # 更新选中的预设提示词
                if selected_preset != st.session_state.selected_preset_prompt:
                    st.session_state.selected_preset_prompt = selected_preset
                    st.session_state.system_prompt = preset_options[selected_preset]["prompt"]
                    # 自动保存到后端
                    with st.spinner("正在保存提示词..."):
                        success, message = update_system_prompt(st.session_state.system_prompt)
                        if success:
                            st.success("✅ 提示词已自动保存", icon="✅")
                        else:
                            st.error(f"❌ 自动保存失败: {message}", icon="❌")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # 显示当前预设提示词的内容
                if st.session_state.system_prompt:
                    with st.expander("查看当前提示词", expanded=False):
                        st.text_area(
                            "当前生效的系统提示词",
                            value=st.session_state.system_prompt,
                            disabled=True,
                            height=150,
                            key="settings_preview_prompt"
                        )
        else:
            with st.container():
                st.markdown('<div class="settings-section">', unsafe_allow_html=True)
                # 自定义提示词输入
                custom_prompt = st.text_area(
                    "输入自定义提示词",
                    value=st.session_state.system_prompt,
                    height=200,
                    help="输入自定义的系统提示词，用于指导AI的回答方式",
                    key="settings_custom_prompt_input",
                    placeholder="在这里输入自定义提示词..."
                )
                st.markdown('</div>', unsafe_allow_html=True)
                
                # 更新自定义提示词
                if custom_prompt != st.session_state.system_prompt:
                    st.session_state.system_prompt = custom_prompt
                    # 自动保存到后端
                    if custom_prompt.strip():  # 只有当提示词不为空时才保存
                        with st.spinner("正在保存提示词..."):
                            success, message = update_system_prompt(st.session_state.system_prompt)
                            if success:
                                st.success("✅ 提示词已自动保存", icon="✅")
                            else:
                                st.error(f"❌ 自动保存失败: {message}", icon="❌")
        
        st.markdown('<div class="settings-divider"></div>', unsafe_allow_html=True)
        
        # 提示词操作按钮
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑 清空",
                       help="清除当前的系统提示词", 
                       key="settings_clear_prompt",
                       use_container_width=True):
                st.session_state.system_prompt = ""
                st.session_state.selected_preset_prompt = "default"
                # 清空后也要同步到后端
                with st.spinner("正在清空提示词..."):
                    success, message = update_system_prompt("")
                    if success:
                        st.success("✅ 提示词已清空并同步到后端！")
                    else:
                        st.warning("提示词已清空，但同步到后端失败")
                st.rerun()
        with col2:
            if st.button("🧪 测试", 
                       help="测试当前提示词是否生效", 
                       key="settings_test_prompt",
                       use_container_width=True):
                with st.spinner("正在测试提示词..."):
                    test_prompt = "你是谁？请介绍一下你自己的角色。"
                    try:
                        # 使用临时会话ID进行测试
                        test_session_id = f"test_session_{int(datetime.now().timestamp())}"
                        
                        test_response = ""
                        for chunk in stream_chat_response(
                            user_message=test_prompt,
                            session_id=test_session_id,
                            model_name=st.session_state.current_model,
                            temperature=st.session_state.temperature,
                            system_prompt=st.session_state.system_prompt
                        ):
                            test_response += chunk
                        
                        if test_response:
                            st.success("提示词测试成功！")
                            with st.expander("查看测试结果", expanded=True):
                                st.markdown("**测试问题：**\n" + test_prompt)
                                st.markdown("**AI回答：**\n" + test_response)
                        else:
                            st.error("测试失败: 未获得有效响应")
                    except Exception as e:
                        st.error(f"测试出错: {str(e)}")

# 主函数
def main():
    # 加载聊天历史
    load_chat_history()
    
    # 如果没有会话，创建一个默认会话
    if not st.session_state.sessions:
        st.session_state.sessions = {"会话1": []}
        st.session_state.current_session = "会话1"
        st.session_state.messages = []
        save_chat_history()
    
    # 如果没有当前会话，设置为第一个会话
    if not st.session_state.current_session or st.session_state.current_session not in st.session_state.sessions:
        st.session_state.current_session = list(st.session_state.sessions.keys())[0]
        st.session_state.messages = st.session_state.sessions[st.session_state.current_session].copy()
    
    # 加载可用模型
    if not st.session_state.available_models:
        load_available_models()
    
    # 加载可用Agent
    if not st.session_state.available_agents:
        st.session_state.available_agents = load_available_agents()
    
    # 加载系统提示词（如果还没有加载）
    if not st.session_state.system_prompt:
        backend_prompt = load_system_prompt()
        if backend_prompt:
            st.session_state.system_prompt = backend_prompt
        else:
            # 如果后端没有提示词，使用默认提示词
            st.session_state.system_prompt = PRESET_PROMPTS[0]["prompt"]
    
    # 侧边栏：会话管理
    with st.sidebar:
        # 添加自定义CSS样式
        st.markdown("""
            <style>
                /* 移除默认的上边距和内边距 */
                .block-container {
                    padding-top: 0 !important;
                }
                [data-testid="stSidebar"] {
                    padding-top: 0.5rem;
                }
                
                /* 标题样式 */
                .chat-manager-title {
                    margin: 0.2rem 0 0.8rem 0;
                    padding: 0.5rem 0;
                    text-align: center;
                    color: #0d8299;
                    font-size: 2rem !important;
                    font-weight: 600;
                }
                
                /* 子标题样式 */
                .history-title {
                    margin: 0.8rem 0;
                    font-size: 1.2rem;
                    color: #333;
                }
                
                /* 分隔线样式 */
                hr {
                    margin: 0.8rem 0 !important;
                }
                
                /* 会话按钮样式 */
                .stButton > button {
                    width: 100%;
                    margin: 3px 0;
                    border: 1px solid #e0e0e0;
                    background-color: white;
                    transition: all 0.2s;
                    padding: 0.4rem !important;
                    height: auto !important;
                }
                .stButton > button:hover {
                    background-color: #f0f2f6;
                    border-color: #0d8299;
                }
                /* 当前选中的会话按钮样式 */
                .current-session > button {
                    border-color: #0d8299 !important;
                    background-color: #e8f4f8 !important;
                }
                /* 删除按钮样式 */
                .delete-btn > button {
                    background-color: transparent;
                    border: none;
                    color: #ff4b4b;
                    padding: 0.3rem !important;
                }
                .delete-btn > button:hover {
                    background-color: #ffe5e5;
                    color: #ff0000;
                }
                
                /* 管理按钮容器样式 */
                .manage-buttons-container {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    gap: 0.4rem;
                    padding: 0.4rem;
                }
                
                /* 管理按钮样式 */
                .manage-button {
                    width: 90% !important;
                    margin: 0.2rem 0 !important;
                    height: 2.3rem !important;
                    border-radius: 0.5rem !important;
                }
                
                /* 会话列表容器样式 */
                [data-testid="stVerticalBlock"] {
                    gap: 0.3rem !important;
                }
                
                /* 会话按钮之间的间距 */
                .stButton {
                    margin-bottom: 0.6rem !important;
                }
                
                /* 会话列表中的按钮样式 */
                .session-list .stButton > button {
                    margin-bottom: 0.6rem !important;
                }
            </style>
        """, unsafe_allow_html=True)
        
        # 使用HTML来创建居中的标题
        st.markdown('<h1 class="chat-manager-title">对话管理</h1>', unsafe_allow_html=True)
        
        # 创建按钮容器
        with st.container():
            # 新建会话按钮
            col1, col2, col3 = st.columns([1, 8, 1])
            with col2:
                if st.button("➕ 新建会话", 
                           help="创建一个新的对话", 
                           type="primary",
                           use_container_width=True):
                    create_new_session()
                    st.rerun()
                    
            # 智能Agent按钮
            col1, col2, col3 = st.columns([1, 8, 1])
            with col2:
                if st.button("🤖 智能Agent", 
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
                        f"{'📍 ' if is_current else ''}{session_id}",
                        help="切换到此会话",
                        disabled=is_current,
                        use_container_width=True,
                        key=f"session_{session_id}",
                        type="secondary" if not is_current else "primary"
                    ):
                        switch_session(session_id)
                        st.rerun()
                with col2:
                    if st.button(
                        "🗑",
                        help=f"删除{session_id}",
                        key=f"delete_{session_id}",
                        use_container_width=True
                    ):
                        delete_session(session_id)
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
                    clear_session()
                    st.rerun()
                
                # 模型设置按钮
                if st.button("🤖 模型设置", 
                           help="点击打开模型设置", 
                           key="model_settings_btn",
                           use_container_width=True):
                    st.session_state.show_model_settings = True
                    st.rerun()
                
                # 提示词设置按钮
                if st.button("💭 提示词设置", 
                           help="点击打开提示词设置", 
                           key="prompt_settings_btn",
                           use_container_width=True):
                    st.session_state.show_prompt_settings = True
                    st.rerun()
        
        # st.divider()

        # st.subheader("知识图谱")
        # # 添加测试按钮
        # if st.button("🧪 测试三元组提取", 
        #             help="测试三元组提取功能",
        #             key="test_triplet_btn"):
        #     st.session_state.show_test = True
        #     st.rerun()

    # 主界面：根据状态显示系统设置或聊天界面
    # 模型设置对话框
    if st.session_state.show_model_settings:
        show_model_settings()
        st.session_state.show_model_settings = False # 关闭状态
    
    # 提示词设置对话框
    if st.session_state.show_prompt_settings:
        show_prompt_settings()
        st.session_state.show_prompt_settings = False # 关闭状态

    # 根据状态显示不同界面
    if st.session_state.show_agent_page:
        # 显示Agent界面
        show_agent_interface()
        return
        
    # 显示聊天界面
    st.markdown("<h3 style='text-align: center;'>GridSeek Chat</h3>", unsafe_allow_html=True)
    
    # 显示当前模型信息
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
    
    # 根据是否显示图谱决定布局
    if st.session_state.show_graph:
        # 创建两栏布局
        chat_col, graph_col = st.columns([1, 1])
        
        # 左侧栏：聊天内容
        with chat_col:
            st.subheader("聊天界面")
            st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
            
            # 创建一个固定高度的容器来显示聊天历史
            chat_container = st.container()
            with chat_container:
                with st.container(height=700, border=True):
                    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
                    
                    # 消息容器
                    st.markdown('<div class="messages-container">', unsafe_allow_html=True)
                    # 显示聊天历史
                    for message in st.session_state.messages:
                        with st.chat_message(message["role"]):
                            st.markdown(message["content"])
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # 输入框容器
                    st.markdown('<div class="input-container">', unsafe_allow_html=True)
                    # 获取用户输入
                    if prompt := st.chat_input("在这里输入您的问题"):
                        # 显示用户消息
                        with st.chat_message("user"):
                            st.markdown(prompt)
                        
                        # 显示AI思考状态
                        with st.chat_message("assistant"):
                            message_placeholder = st.empty()
                            message_placeholder.markdown("🤔 思考中...")
                            
                            # 调用后端API（流式聊天）
                            try:
                                # 确保有session_id
                                if not st.session_state.current_session:
                                    st.session_state.current_session = f"session_{int(datetime.now().timestamp())}"
                                
                                full_response = ""
                                
                                # 使用流式聊天
                                for chunk in stream_chat_response(
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
                                    save_chat_history()
                                
                                # 提取三元组并在有新三元组时重新加载页面
                                if extract_and_store_triplets(full_response) and st.session_state.show_graph:
                                    st.rerun()
                                
                            except Exception as e:
                                message_placeholder.error(f"😔 获取回复失败: {e}")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)

        # 右侧栏：知识图谱
        with graph_col:
            st.subheader("知识图谱可视化")
            # 直接渲染图谱
            dynamic_html = generate_dynamic_graph_html(st.session_state.get('triplets', []))
            components.html(dynamic_html, height=600, scrolling=True)
    else:
        # 标准布局：只显示聊天
        st.subheader("聊天界面")
        st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
        
        # 创建一个固定高度的容器来显示聊天历史
        chat_container = st.container()
        with chat_container:
            with st.container(height=600, border=True):
                st.markdown('<div class="chat-container">', unsafe_allow_html=True)
                
                # 消息容器
                st.markdown('<div class="messages-container">', unsafe_allow_html=True)
                # 显示聊天历史
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
                st.markdown('</div>', unsafe_allow_html=True)
                
                # 输入框容器
                st.markdown('<div class="input-container">', unsafe_allow_html=True)
                # 获取用户输入
                if prompt := st.chat_input("在这里输入您的问题"):
                    # 显示用户消息
                    with st.chat_message("user"):
                        st.markdown(prompt)
                    
                    # 显示AI思考状态
                    with st.chat_message("assistant"):
                        message_placeholder = st.empty()
                        message_placeholder.markdown("🤔 思考中...")
                        
                        # 调用后端API（流式聊天）
                        try:
                            # 确保有session_id
                            if not st.session_state.current_session:
                                st.session_state.current_session = f"session_{int(datetime.now().timestamp())}"
                            
                            full_response = ""
                            
                            # 使用流式聊天
                            for chunk in stream_chat_response(
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
                                save_chat_history()
                            
                            # 提取三元组并在有新三元组时重新加载页面
                            if extract_and_store_triplets(full_response) and st.session_state.show_graph:
                                st.rerun()
                            
                        except Exception as e:
                            message_placeholder.error(f"😔 获取回复失败: {e}")
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    # 初始化测试标志
    if 'show_test' not in st.session_state:
        st.session_state.show_test = False
    main()

# 页面底部
st.markdown("---")
st.caption("© 2024 Gridseek | Powered by Streamlit")
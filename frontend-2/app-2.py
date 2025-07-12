import streamlit as st
import streamlit.components.v1 as components
import json
from datetime import datetime
import requests
import os

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
}

[data-testid="stSidebarNav"] {
    background-color: #FFFFFF !important;
}

[data-testid="stSidebar"]::before {
    display: none;
}

[data-testid="stSidebar"] [data-testid="stMarkdown"] {
    padding-top: 0;
}

[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    border-radius: 5px !important;
    margin-bottom: 0.5rem;
    background: rgba(255, 255, 255, 0.8) !important;
    border: 1px solid rgba(181, 230, 216, 0.3) !important;
    transition: all 0.3s ease !important;
    backdrop-filter: blur(5px);
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255, 255, 255, 0.95) !important;
    border-color: #B5E6D8 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
}

[data-testid="stSidebar"] hr {
    margin: 1rem 0 !important;
    border: none !important;
    height: 1px !important;
    background-color: rgba(224, 224, 224, 0.3) !important;
}

[data-testid="stSidebar"] h1 {
    color: #2C3E50;
    font-size: 1.5rem;
    margin-bottom: 1rem;
    text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.8);
}

[data-testid="stSidebar"] h2 {
    color: #34495E;
    font-size: 1.2rem;
    margin: 1rem 0;
    text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.8);
}

/* Logo样式 */
[data-testid="stImage"] {
    position: relative !important;
    left: 0 !important;
    top: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    background-color: #FFFFFF !important;
    width: 100% !important;
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
    height: 600px;
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
    st.session_state.show_graph = False
if 'triplets' not in st.session_state:
    st.session_state.triplets = []

def toggle_knowledge_graph():
    """切换知识图谱显示状态"""
    st.session_state.show_graph = not st.session_state.show_graph

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
            st.session_state.sessions = chat_history
            
            # 如果是当前会话，更新messages
            if st.session_state.current_session in chat_history:
                st.session_state.messages = chat_history[st.session_state.current_session].copy()
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
    st.session_state.messages = st.session_state.sessions[session_id]

def clear_session():
    """清空当前会话"""
    if st.session_state.current_session:
        st.session_state.messages = []
        st.session_state.sessions[st.session_state.current_session] = []
        save_chat_history()

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
        response = requests.post(
            'http://localhost:8000/api/kg/extract',
            json={'text': text},
            timeout=20
        )
        response.raise_for_status()
        data = response.json()
        new_triplets = data.get("triples", [])

        if new_triplets:
            # 获取现有三元组
            existing_triplets = st.session_state.get('triplets', [])
            # 将新的三元组添加进去，同时去重
            for triplet in new_triplets:
                if triplet not in existing_triplets:
                    existing_triplets.append(triplet)
            
            st.session_state.triplets = existing_triplets
            st.toast(f"提取到 {len(new_triplets)} 个新的知识三元组！", icon="✨")

    except requests.RequestException as e:
        st.error(f"提取知识三元组失败：{e}")
    except Exception as e:
        st.error(f"处理三元组时出错: {e}")

def generate_dynamic_graph_html(triplets: list) -> str:
    """根据三元组动态生成graph.html内容"""
    nodes_set = set()
    nodes_js = []
    edges_js = []

    for triplet in triplets:
        h, r, t = triplet.get('h'), triplet.get('r'), triplet.get('t')
        if not all([h, r, t]):
            continue

        # 添加节点，使用集合去重
        if h not in nodes_set:
            nodes_set.add(h)
            nodes_js.append(f"{{id: '{h}', label: '{h}'}}")
        if t not in nodes_set:
            nodes_set.add(t)
            nodes_js.append(f"{{id: '{t}', label: '{t}'}}")

        # 添加边
        edges_js.append(f"{{from: '{h}', to: '{t}', label: '{r}', arrows: 'to'}}")

    nodes_str = ",\n".join(nodes_js)
    edges_str = ",\n".join(edges_js)

    # 读取HTML模板文件
    try:
        with open("graph_template.html", 'r', encoding='utf-8') as f:
            template = f.read()
            
        # 替换占位符
        html_content = template.replace("{{NODES_PLACEHOLDER}}", nodes_str)
        html_content = html_content.replace("{{EDGES_PLACEHOLDER}}", edges_str)
        
        return html_content
    except FileNotFoundError:
        return "<h3>错误：找不到 graph_template.html 文件。</h3>"
    except Exception as e:
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

# 主函数
def main():
    # 加载聊天历史
    load_chat_history()
    
    # 侧边栏：会话管理
    with st.sidebar:
        st.image("logo/logo.png", use_container_width=True)
        st.title("对话管理")
        
        if st.button("新建会话", help="创建一个新的对话"):
            create_new_session()
        st.divider()
        
        st.subheader("历史会话")
        sorted_sessions = sorted(st.session_state.sessions.items(), 
                               key=lambda x: int(x[0].replace("会话", "")))
        
        for session_id, _ in sorted_sessions:
            col1, col2 = st.columns([4, 1])
            with col1:
                is_current = session_id == st.session_state.current_session
                button_text = f"📝 {session_id}" + (" ✓" if is_current else "")
                if st.button(button_text, key=f"session_{session_id}", 
                           help="点击切换到此对话",
                           type="primary" if is_current else "secondary"):
                    switch_session(session_id)
            with col2:
                if st.button("🗑", key=f"delete_{session_id}", help="删除此对话"):
                    delete_session(session_id)
        
        st.divider()
        
        if st.button("清空当前会话", 
                    help="清空当前对话的所有消息",
                    disabled=not st.session_state.current_session):
            clear_session()
        st.divider()
        
        st.subheader("知识图谱")
        if st.button("📊 显示知识图谱" if not st.session_state.show_graph else "📊 隐藏知识图谱", 
                    help="点击显示或隐藏知识图谱",
                    key="knowledge_graph_btn"):
            toggle_knowledge_graph()
            st.rerun()  # 强制重新加载页面以应用布局变化

    # 主聊天区域
    st.markdown("<h3 style='text-align: center;'>GridSeek Chat</h3>", unsafe_allow_html=True)
    
    # 根据是否显示图谱决定布局
    if st.session_state.show_graph:
        # 创建两栏布局
        chat_col, graph_col = st.columns([1, 1])
        
        # 左侧栏：聊天内容
        with chat_col:
            # 显示聊天历史
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            
            # 获取用户输入
            if prompt := st.chat_input("在这里输入您的问题"):
                # 添加用户消息
                st.session_state.messages.append({"role": "user", "content": prompt})
                
                # 将消息同步到当前会话
                if st.session_state.current_session:
                    st.session_state.sessions[st.session_state.current_session] = st.session_state.messages.copy()
                
                # 显示用户消息
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                # 显示AI思考状态
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    message_placeholder.markdown("🤔 思考中...")
                    
                    # 调用后端API
                    try:
                        response = requests.post(
                            'http://localhost:8000/api/qa',
                            json={'question': prompt},
                            stream=True,
                            timeout=30
                        )
                        response.raise_for_status()
                        
                        # 流式处理响应
                        full_response = ""
                        for line in response.iter_lines():
                            if line:
                                try:
                                    data = json.loads(line.decode('utf-8'))
                                    chunk = data.get('answer', '')
                                    if chunk:
                                        full_response += chunk
                                        message_placeholder.markdown(full_response + "▌")
                                except json.JSONDecodeError:
                                    continue
                        
                        # 显示最终响应
                        message_placeholder.markdown(full_response)
                        
                        # 添加AI回复到消息列表
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
                        
                        # 同步到当前会话
                        if st.session_state.current_session:
                            st.session_state.sessions[st.session_state.current_session] = st.session_state.messages.copy()
                            save_chat_history()
                        
                        # 提取三元组
                        extract_and_store_triplets(full_response)
                        
                        # 重新加载页面以更新图谱
                        st.rerun()
                        
                    except Exception as e:
                        message_placeholder.error(f"😔 获取回复失败: {e}")
        
        # 右侧栏：知识图谱
        with graph_col:
            # 创建一个占位容器，让图谱显示在底部
            st.markdown('<div style="height: 50vh;"></div>', unsafe_allow_html=True)
            
            # 显示知识图谱
            st.markdown('<div class="graph-column">', unsafe_allow_html=True)
            st.subheader("知识图谱可视化")
            render_knowledge_graph()
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        # 标准布局：只显示聊天
        # 显示聊天历史
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # 获取用户输入
        if prompt := st.chat_input("在这里输入您的问题"):
            # 添加用户消息
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # 将消息同步到当前会话
            if st.session_state.current_session:
                st.session_state.sessions[st.session_state.current_session] = st.session_state.messages.copy()
            
            # 显示用户消息
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # 显示AI思考状态
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_placeholder.markdown("🤔 思考中...")
                
                # 调用后端API
                try:
                    response = requests.post(
                        'http://localhost:8000/api/qa',
                        json={'question': prompt},
                        stream=True,
                        timeout=30
                    )
                    response.raise_for_status()
                    
                    # 流式处理响应
                    full_response = ""
                    for line in response.iter_lines():
                        if line:
                            try:
                                data = json.loads(line.decode('utf-8'))
                                chunk = data.get('answer', '')
                                if chunk:
                                    full_response += chunk
                                    message_placeholder.markdown(full_response + "▌")
                            except json.JSONDecodeError:
                                continue
                    
                    # 显示最终响应
                    message_placeholder.markdown(full_response)
                    
                    # 添加AI回复到消息列表
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    
                    # 同步到当前会话
                    if st.session_state.current_session:
                        st.session_state.sessions[st.session_state.current_session] = st.session_state.messages.copy()
                        save_chat_history()
                    
                    # 提取三元组
                    extract_and_store_triplets(full_response)
                    
                except Exception as e:
                    message_placeholder.error(f"😔 获取回复失败: {e}")

if __name__ == "__main__":
    main()

# 页面底部
st.markdown("---")
st.caption("© 2024 Gridseek | Powered by Streamlit")
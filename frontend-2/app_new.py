import streamlit as st
import streamlit.components.v1 as components
import json
from datetime import datetime
import requests
import os
import re # Added for graph template handling

# 预设提示词列表
PRESET_PROMPTS = [
    {
        "name": "默认助手",
        "prompt": "",
        "description": "普通对话助手模式"
    },
    {
        "name": "创意写作",
        "prompt": "你是一个富有创意的写作助手。请发挥想象力，用生动有趣的语言来创作内容。你可以写故事、诗歌、剧本或者任何形式的创意文本。注重文采和创新，让文字充满生命力。",
        "description": "创意文学创作和写作辅助"
    },
    {
        "name": "代码专家",
        "prompt": "你是一个经验丰富的编程专家。请用清晰的代码和详细的注释来回答问题。优先考虑代码的可读性和最佳实践。",
        "description": "提供代码示例和技术解答"
    },
    {
        "name": "学术顾问",
        "prompt": "你是一个严谨的学术顾问。请用专业的学术语言回答问题，必要时提供相关的研究依据和参考文献。",
        "description": "学术风格的专业解答"
    },
    {
        "name": "教学助手",
        "prompt": "你是一个耐心的教学助手。请用通俗易懂的语言解释复杂的概念，适当使用类比和例子来帮助理解。",
        "description": "通俗易懂的知识讲解"
    }
]

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
if 'available_models' not in st.session_state:
    st.session_state.available_models = []
if 'current_model' not in st.session_state:
    st.session_state.current_model = "gpt-4o-mini"  # 默认模型
if 'temperature' not in st.session_state:
    st.session_state.temperature = 0.7
if 'system_prompt' not in st.session_state:
    st.session_state.system_prompt = ""  # 默认空提示词
if 'prompt_mode' not in st.session_state:
    st.session_state.prompt_mode = "预设"  # 默认使用预设提示词
if 'selected_preset_prompt' not in st.session_state:
    st.session_state.selected_preset_prompt = "默认助手"  # 默认使用默认助手

def toggle_knowledge_graph():
    """切换知识图谱显示状态"""
    st.session_state.show_graph = not st.session_state.show_graph

def load_available_models():
    """从后端加载可用模型列表"""
    try:
        response = requests.get('http://localhost:8000/api/qa/models', timeout=10)
        response.raise_for_status()
        models = response.json()
        st.session_state.available_models = models
        return True
    except requests.RequestException as e:
        st.error(f"加载模型列表失败: {e}")
        # 设置默认模型列表作为备选
        st.session_state.available_models = [
            {"model_name": "gpt-4o-mini", "description": "OpenAI GPT-4o-mini, 性能优秀，成本较低。"},
            {"model_name": "deepseek-chat", "description": "DeepSeek Chat, 中文表现优秀的开源模型。"}
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
        response = requests.get('http://localhost:8000/api/qa/models', timeout=5)
        response.raise_for_status()
        return True, "后端连接正常"
    except requests.RequestException as e:
        return False, f"后端连接失败: {e}"

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
                    # 直接调用后端API测试
                    response = requests.post(
                        'http://localhost:8000/api/qa',
                        json={
                            'question': test_question,
                            'model_name': st.session_state.current_model,
                            'temperature': st.session_state.temperature,
                            'system_prompt': st.session_state.system_prompt
                        },
                        timeout=30
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    if data.get('status') == 'success':
                        st.success(f"✅ 模型 {data.get('model_name')} 响应成功!")
                        st.markdown(f"**回答:** {data.get('response_message')}")
                    else:
                        st.error(f"❌ 模型响应失败: {data.get('error')}")
                        
                except requests.RequestException as e:
                    st.error(f"❌ 请求失败: {e}")
                except Exception as e:
                    st.error(f"❌ 处理响应时出错: {e}")
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

# 主函数
def main():
    # 加载聊天历史
    load_chat_history()
    
    # 加载可用模型列表（如果还没有加载）
    if not st.session_state.available_models:
        load_available_models()
    
    # 侧边栏：会话管理
    with st.sidebar:
        st.image("logo/logo.png", use_container_width=True)
        st.title("对话管理")
        
        if st.button("新建会话", help="创建一个新的对话"):
            create_new_session()
            st.rerun()
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
                    st.rerun()
            with col2:
                if st.button("🗑", key=f"delete_{session_id}", help="删除此对话"):
                    delete_session(session_id)
                    st.rerun()
        
        st.divider()
        
        if st.button("清空当前会话", 
                    help="清空当前对话的所有消息",
                    disabled=not st.session_state.current_session):
            clear_session()
            st.rerun()
        st.divider()
        
        # 模型设置部分
        st.subheader("🤖 模型设置")
        
        # 显示连接状态
        is_connected, status_msg = check_model_connectivity()
        if is_connected:
            st.success(f"✅ {status_msg}")
        else:
            st.error(f"❌ {status_msg}")
        
        # 加载可用模型（如果还没有加载）
        if not st.session_state.available_models:
            load_available_models()
        
        # 模型选择器
        if st.session_state.available_models:
            model_options = [model["model_name"] for model in st.session_state.available_models]
            model_descriptions = {model["model_name"]: model["description"] 
                                for model in st.session_state.available_models}
            
            # 确保当前模型在可用模型列表中
            if st.session_state.current_model not in model_options:
                st.session_state.current_model = model_options[0] if model_options else "gpt-4o-mini"
            
            selected_model = st.selectbox(
                "选择 AI 模型:",
                options=model_options,
                index=model_options.index(st.session_state.current_model) if st.session_state.current_model in model_options else 0,
                format_func=lambda x: f"{x} ({model_descriptions.get(x, '').split(',')[0]})",
                help="选择用于对话的 AI 模型",
                key="model_selector"
            )
            
            # 当模型选择发生变化时
            if selected_model != st.session_state.current_model:
                change_model(selected_model)
                st.rerun()
            
            # 显示当前模型的详细描述
            if selected_model in model_descriptions:
                st.caption(f"📝 {model_descriptions[selected_model]}")
            
            # 温度调节器
            new_temperature = st.slider(
                "创造性 (Temperature):",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.temperature,
                step=0.1,
                help="较低的值让回答更确定，较高的值让回答更具创造性",
                key="temperature_slider"
            )
            
            # 当温度发生变化时
            if new_temperature != st.session_state.temperature:
                change_temperature(new_temperature)
            
            # 刷新模型列表按钮
            if st.button("🔄 刷新模型列表", help="重新从后端获取可用模型"):
                with st.spinner("正在加载模型列表..."):
                    load_available_models()
                st.rerun()
        else:
            st.warning("无法加载模型列表，请检查后端连接。")
            if st.button("🔄 重试加载", help="重新尝试加载模型列表"):
                load_available_models()
                st.rerun()
        
        st.divider()

        # 提示词设置部分
        st.subheader("💭 提示词设置")
        
        # 提示词模式选择
        prompt_mode = st.radio(
            "选择提示词模式",
            ["预设", "自定义"],
            key="prompt_mode_radio",
            help="选择使用预设提示词或自定义提示词"
        )
        
        # 更新session state中的prompt_mode
        if prompt_mode != st.session_state.prompt_mode:
            st.session_state.prompt_mode = prompt_mode
            
        if prompt_mode == "预设":
            # 预设提示词选择
            preset_options = {prompt["name"]: prompt for prompt in PRESET_PROMPTS}
            selected_preset = st.selectbox(
                "选择预设提示词",
                options=list(preset_options.keys()),
                index=list(preset_options.keys()).index(st.session_state.selected_preset_prompt),
                format_func=lambda x: f"{x} - {preset_options[x]['description']}",
                key="preset_prompt_selector"
            )
            
            # 更新选中的预设提示词
            if selected_preset != st.session_state.selected_preset_prompt:
                st.session_state.selected_preset_prompt = selected_preset
                st.session_state.system_prompt = preset_options[selected_preset]["prompt"]
                
            # 显示当前预设提示词的内容
            if st.session_state.system_prompt:
                with st.expander("查看当前提示词"):
                    st.text_area(
                        "当前生效的系统提示词",
                        value=st.session_state.system_prompt,
                        disabled=True,
                        height=100
                    )
        else:
            # 自定义提示词输入
            custom_prompt = st.text_area(
                "输入自定义提示词",
                value=st.session_state.system_prompt,
                height=150,
                help="输入自定义的系统提示词，用于指导AI的回答方式",
                key="custom_prompt_input"
            )
            
            # 更新自定义提示词
            if custom_prompt != st.session_state.system_prompt:
                st.session_state.system_prompt = custom_prompt
        
        # 清空提示词按钮
        if st.button("🗑 清空提示词", help="清除当前的系统提示词"):
            st.session_state.system_prompt = ""
            st.session_state.selected_preset_prompt = "默认助手"
            st.rerun()
            
        # 添加测试按钮
        if st.button("🧪 测试提示词", help="测试当前提示词是否生效"):
            with st.spinner("正在测试提示词..."):
                test_prompt = "你是谁？请介绍一下你自己的角色。"
                try:
                    response = requests.post(
                        'http://localhost:8000/api/qa',
                        json={
                            'question': test_prompt,
                            'model_name': st.session_state.current_model,
                            'temperature': st.session_state.temperature,
                            'system_prompt': st.session_state.system_prompt
                        },
                        timeout=30
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    if data.get('status') == 'success':
                        st.success("提示词测试成功！")
                        st.markdown("**测试问题：**\n" + test_prompt)
                        st.markdown("**AI回答：**\n" + data.get('response_message', ''))
                    else:
                        st.error(f"测试失败: {data.get('error', '未知错误')}")
                except Exception as e:
                    st.error(f"测试出错: {str(e)}")

        st.divider()

        st.subheader("知识图谱")
        if st.button("📊 显示知识图谱" if not st.session_state.show_graph else "📊 隐藏知识图谱", 
                    help="点击显示或隐藏知识图谱",
                    key="knowledge_graph_btn"):
            toggle_knowledge_graph()
            st.rerun()  # 强制重新加载页面以应用布局变化
            
        # 添加测试按钮
        st.divider()
        if st.button("🧪 测试三元组提取", help="测试三元组提取功能"):
            st.session_state.show_test = True
            st.rerun()

    # 主聊天区域
    st.markdown("<h3 style='text-align: center;'>GridSeek Chat</h3>", unsafe_allow_html=True)
    
    # 显示当前模型信息
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            f"<div style='text-align: center; padding: 5px; background-color: #f0f2f6; border-radius: 5px; margin-bottom: 10px;'>"
            f"🤖 当前模型: <strong>{st.session_state.current_model}</strong> | "
            f"🌡️ 温度: <strong>{st.session_state.temperature}</strong>"
            f"</div>", 
            unsafe_allow_html=True
        )
        
        # 显示当前提示词信息
        if st.session_state.system_prompt:
            st.markdown(
                f"<div style='text-align: center; padding: 5px; background-color: #e8f4ea; border-radius: 5px; margin-bottom: 10px;'>"
                f"💭 当前提示词: <strong>{st.session_state.selected_preset_prompt if st.session_state.prompt_mode == '预设' else '自定义提示词'}</strong>"
                f"</div>",
                unsafe_allow_html=True
            )
    
    # 如果需要显示测试界面
    if st.session_state.get('show_test', False):
        # 创建两个标签页
        tab1, tab2 = st.tabs(["🧪 三元组提取测试", "🤖 模型切换测试"])
        
        with tab1:
            test_triplet_extraction()
        
        with tab2:
            test_model_switching()
            
        if st.button("返回聊天"):
            st.session_state.show_test = False
            st.rerun()
        return

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
                        # 准备请求数据
                        request_data = {
                            'question': prompt,
                            'model_name': st.session_state.current_model,
                            'temperature': st.session_state.temperature,
                            'system_prompt': st.session_state.system_prompt
                        }
                        
                        # 打印调试信息
                        print(f"发送请求到后端，参数：{request_data}")
                        
                        response = requests.post(
                            'http://localhost:8000/api/qa',
                            json=request_data,
                            timeout=30
                        )
                        response.raise_for_status()
                        
                        # 解析响应
                        data = response.json()
                        print(f"后端响应数据：{data}")
                        
                        if data.get('status') == 'success':
                            full_response = data.get('response_message', '')
                            message_placeholder.markdown(full_response)
                            
                            # 添加AI回复到消息列表
                            st.session_state.messages.append({"role": "assistant", "content": full_response})
                            
                            # 同步到当前会话
                            if st.session_state.current_session:
                                st.session_state.sessions[st.session_state.current_session] = st.session_state.messages.copy()
                                save_chat_history()
                            
                            # 提取三元组并在有新三元组时重新加载页面
                            if extract_and_store_triplets(full_response) and st.session_state.show_graph:
                                st.rerun()
                        else:
                            error_msg = data.get('error', '未知错误')
                            message_placeholder.error(f"😔 获取回复失败: {error_msg}")
                            return
                            
                    except Exception as e:
                        message_placeholder.error(f"😔 获取回复失败: {e}")
                        print(f"API调用异常：{str(e)}")  # 打印异常信息
        
        # 右侧栏：知识图谱
        with graph_col:
            # 创建一个容器来包含所有内容
            graph_container = st.container()
            
            # 首先计算左侧栏的大致高度
            # 假设每条消息平均高度为100px，这个值可以根据实际情况调整
            message_count = len(st.session_state.messages)
            estimated_height = max(50, min(message_count * 100, 400))  # 至少50px，最多400px
            
            # 创建一个占位容器，让图谱显示在底部
            # 使用CSS的flex布局来实现底部对齐
            graph_container.markdown(f"""
            <div style="display: flex; flex-direction: column; height: calc(100vh - 100px);">
                <div style="flex-grow: 1; min-height: {estimated_height}px;"></div>
                <div class="graph-column">
                    <h3>知识图谱可视化</h3>
                    <div id="knowledge-graph-container" style="height: 600px; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden;">
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 在HTML容器内渲染图谱
            with graph_container:
                # 使用st.components.html将图谱内容注入到预定义的容器中
                dynamic_html = generate_dynamic_graph_html(st.session_state.get('triplets', []))
                components.html(dynamic_html, height=600, scrolling=True)
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
                        json={
                            'question': prompt,
                            'model_name': st.session_state.current_model,
                            'temperature': st.session_state.temperature,
                            'system_prompt': st.session_state.system_prompt
                        },
                        timeout=30
                    )
                    response.raise_for_status()
                    
                    # 解析响应
                    data = response.json()
                    
                    if data.get('status') == 'success':
                        full_response = data.get('response_message', '')
                        message_placeholder.markdown(full_response)
                    else:
                        error_msg = data.get('error', '未知错误')
                        message_placeholder.error(f"😔 获取回复失败: {error_msg}")
                        return
                    
                    # 添加AI回复到消息列表
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

if __name__ == "__main__":
    # 初始化测试标志
    if 'show_test' not in st.session_state:
        st.session_state.show_test = False
    main()

# 页面底部
st.markdown("---")
st.caption("© 2024 Gridseek | Powered by Streamlit")
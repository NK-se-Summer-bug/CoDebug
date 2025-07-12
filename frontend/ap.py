import streamlit as st
import json
from datetime import datetime
import requests

# 设置页面配置
st.set_page_config(
    page_title="Gridseek",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Gridseek")

# 初始化session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'sessions' not in st.session_state:
    st.session_state.sessions = {}
if 'current_session' not in st.session_state:
    st.session_state.current_session = None
if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = 'expanded'

def toggle_sidebar():
    """切换侧边栏状态"""
    if st.session_state.sidebar_state == 'expanded':
        st.session_state.sidebar_state = 'collapsed'
    else:
        st.session_state.sidebar_state = 'expanded'

def save_chat_history():
    """保存聊天历史"""
    try:
        history = {}
        for session_id, messages in st.session_state.sessions.items():
            history[session_id] = {
                'messages': messages,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        with open('chat_history.json', 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"保存聊天历史失败：{str(e)}")

def load_chat_history():
    """加载聊天历史"""
    try:
        with open('chat_history.json', 'r', encoding='utf-8') as f:
            history = json.load(f)
            st.session_state.sessions = {}
            for session_id, data in history.items():
                if isinstance(data, dict) and 'messages' in data:
                    # 新格式
                    st.session_state.sessions[session_id] = data['messages']
                else:
                    # 兼容旧格式
                    messages = []
                    past = data.get('past', [])
                    generated = data.get('generated', [])
                    for user_msg, ai_msg in zip(past, generated):
                        messages.append({'role': 'user', 'content': user_msg})
                        messages.append({'role': 'assistant', 'content': ai_msg})
                    st.session_state.sessions[session_id] = messages
    except FileNotFoundError:
        st.session_state.sessions = {}
    except Exception as e:
        st.error(f"加载聊天历史失败：{str(e)}")
        st.session_state.sessions = {}

def create_new_session():
    """创建新会话"""
    session_id = f"新会话_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    st.session_state.sessions[session_id] = []
    st.session_state.current_session = session_id
    st.session_state.messages = []
    save_chat_history()

def switch_session(session_id):
    """切换会话"""
    if session_id in st.session_state.sessions:
        st.session_state.current_session = session_id
        st.session_state.messages = st.session_state.sessions[session_id]
        st.rerun()

def clear_session():
    """清空当前会话"""
    if st.session_state.current_session:
        st.session_state.messages = []
        st.session_state.sessions[st.session_state.current_session] = []
        save_chat_history()
        st.rerun()

def render_chat():
    """渲染聊天界面"""
    try:
        # 从chat.html读取模板
        with open('chat.html', 'r', encoding='utf-8') as f:
            chat_template = f.read()
            
        # 构建消息HTML
        messages_html = ""
        if st.session_state.messages:
            for msg in st.session_state.messages:
                if msg['role'] == 'user':
                    messages_html += f'''
                        <div class="message-row user-message">
                            <div class="avatar user-avatar"></div>
                            <div class="message-content">
                                <div class="message-bubble user-bubble">
                                    {msg['content']}
                                </div>
                            </div>
                        </div>
                    '''
                else:  # role == 'assistant'
                    messages_html += f'''
                        <div class="message-row ai-message">
                            <div class="avatar ai-avatar"></div>
                            <div class="message-content">
                                <div class="message-bubble ai-bubble">
                                    {msg['content']}
                                </div>
                            </div>
                        </div>
                    '''
        
        # 将消息插入到模板中
        chat_html = chat_template.replace(
            '<div class="chat-container" id="chatContainer">',
            f'<div class="chat-container" id="chatContainer">{messages_html}'
        )
        
        # 渲染HTML
        st.components.v1.html(chat_html, height=600, scrolling=True)
    except Exception as e:
        st.error(f"渲染聊天界面失败：{str(e)}")

def handle_input():
    """处理用户输入"""
    if st.session_state.user_input and st.session_state.current_session:
        user_message = st.session_state.user_input
        st.session_state.user_input = ''  # 清空输入

        # 添加用户消息
        user_msg = {'role': 'user', 'content': user_message}
        st.session_state.messages.append(user_msg)
        st.session_state.sessions[st.session_state.current_session].append(user_msg)

        try:
            # 获取AI回复
            response = requests.post(
                'http://localhost:8000/api/qa',
                json={'question': user_message}#添加model name
            )
            response.raise_for_status()
            ai_message = response.json()['answer']
        except Exception as e:
            st.error(f"获取回复失败：{str(e)}")
            ai_message = "抱歉，我现在无法回复。"

        # 添加AI回复
        ai_msg = {'role': 'assistant', 'content': ai_message}
        st.session_state.messages.append(ai_msg)
        st.session_state.sessions[st.session_state.current_session].append(ai_msg)
        
        # 保存聊天历史
        save_chat_history()
        st.rerun()

def main():
    """主函数"""
    # 加载聊天历史
    load_chat_history()
    
    # 主界面分为左右两栏
    col1, col2 = st.columns([1, 1])
    
    # 左侧：对话界面
    with col1:
        st.markdown("### 💬 聊天对话")
        
        if not st.session_state.current_session:
            st.info("👈 请在侧边栏创建或选择一个会话")
        else:
            # 渲染聊天界面
            render_chat()
            # 输入框
            st.text_input(
                "发送消息",
                key="user_input",
                on_change=handle_input,
                label_visibility="collapsed"
            )
    
    # 右侧：知识图谱
    with col2:
        st.markdown("### 🕸️ 知识图谱")
        
        graph_container = st.container()
        with graph_container:
            try:
                with open("graph.html", "r", encoding="utf-8") as f:
                    graph_html = f.read()
                st.components.v1.html(graph_html, height=600, scrolling=False)
            except FileNotFoundError:
                st.error("❌ 找不到知识图谱文件")
                st.info("请确保 graph.html 文件存在于当前目录中")
            except Exception as e:
                st.error(f"❌ 加载图表时出错: {str(e)}")
    
    # 侧边栏：会话管理
    with st.sidebar:
        st.title("💬 会话管理")
        
        # 新建会话按钮
        if st.button("➕ 新建会话"):
            create_new_session()
        
        st.divider()
        
        # 显示所有会话
        st.subheader("历史会话")
        for session_id in st.session_state.sessions:
            if st.button(
                f"📝 {session_id}",
                key=f"session_{session_id}",
                help="点击切换到此会话"
            ):
                switch_session(session_id)
        
        st.divider()
        
        # 清空会话按钮
        if st.button(
            "🗑️ 清空当前会话",
            disabled=not st.session_state.current_session
        ):
            clear_session()
        # 删除当前会话功能
        if st.button("🗑️ 删除当前会话"):
            if st.session_state.current_session:
                # 删除当前会话的消息
                st.session_state.messages = []
                # 从会话字典中删除当前会话
                st.session_state.sessions.pop(st.session_state.current_session, None)
                # 重置当前会话为None
                st.session_state.current_session = None
                # 保存更新后的聊天历史
                save_chat_history()


if __name__ == "__main__":
    main()

# 页面底部
st.markdown("---")
st.caption("© 2024 Gridseek | Powered by Streamlit") 
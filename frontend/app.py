import streamlit as st
import json
import requests
from datetime import datetime
from typing import Generator

# 初始化session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'sessions' not in st.session_state:
    st.session_state.sessions = {}
if 'current_session' not in st.session_state:
    st.session_state.current_session = None

def process_chunk(chunk: bytes) -> str:
    """处理单个数据块"""
    try:
        chunk_data = json.loads(chunk.decode())
        return chunk_data.get('answer', '')
    except json.JSONDecodeError:
        return ''

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
                st.session_state.messages = chat_history[st.session_state.current_session]
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

def clear_session():
    """清空当前会话"""
    if st.session_state.current_session:
        st.session_state.messages = []
        st.session_state.sessions[st.session_state.current_session] = []
        save_chat_history()

def handle_input(user_message: str):
    """处理用户输入"""
    if user_message and st.session_state.current_session:
        try:
            # 显示用户消息
            with st.chat_message('user'):
                st.markdown(user_message)
            
            # 添加用户消息到历史
            user_msg = {'role': 'user', 'content': user_message}
            st.session_state.messages.append(user_msg)
            st.session_state.sessions[st.session_state.current_session].append(user_msg)
            save_chat_history()  # 立即保存用户消息

            # 创建AI消息占位
            with st.chat_message('assistant'):
                message_placeholder = st.empty()
                thinking_placeholder = st.empty()
                
                # 显示思考状态
                thinking_placeholder.markdown("思考中...")
                
                # 发送请求并获取流式响应
                response = requests.post(
                    'http://localhost:8000/api/qa',
                    json={'question': user_message},
                    stream=True
                )
                response.raise_for_status()
                
                # 处理流式响应
                full_response = ""
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        chunk_text = process_chunk(chunk)
                        if chunk_text:
                            # 累积响应文本
                            full_response += chunk_text
                            # 清除思考提示
                            thinking_placeholder.empty()
                            # 显示带光标的文本
                            message_placeholder.markdown(full_response + "▌")
                
                # 显示最终完整响应（不带光标）
                if full_response:
                    message_placeholder.markdown(full_response)
                    # 保存到历史记录
                    ai_msg = {'role': 'assistant', 'content': full_response}
                    st.session_state.messages.append(ai_msg)
                    st.session_state.sessions[st.session_state.current_session].append(ai_msg)
                    save_chat_history()

        except Exception as e:
            st.error(f"获取回复失败：{str(e)}")
            ai_message = "抱歉，我现在无法回复。"
            
            # 添加错误消息
            ai_msg = {'role': 'assistant', 'content': ai_message}
            st.session_state.messages.append(ai_msg)
            st.session_state.sessions[st.session_state.current_session].append(ai_msg)
            save_chat_history()

def main():
    """主函数"""
    # 加载聊天历史
    load_chat_history()
    
    # 对话界面
    #st.markdown("### 💬 聊天对话")
    st.title("Gridseek")

    # 侧边栏：会话管理
    with st.sidebar:
        st.title("对话管理")
        
        # 新建会话按钮
        if st.button("新建对话"):
            create_new_session()
        
        st.divider()
        
        # 显示所有会话
        st.subheader("历史对话")
        for session_id in st.session_state.sessions:
            if st.button(
                f"📝 {session_id}",
                key=f"session_{session_id}",
                help="点击切换到此对话"
            ):
                switch_session(session_id)
        
        st.divider()
        
        # 清空会话按钮
        if st.button(
            "清空当前对话",
            disabled=not st.session_state.current_session
        ):
            clear_session()
        
        # 删除当前会话功能
        if st.button("删除当前对话"):
            if st.session_state.current_session:
                st.session_state.messages = []
                st.session_state.sessions.pop(st.session_state.current_session, None)
                st.session_state.current_session = None
                save_chat_history()
    
    # 主界面
    if not st.session_state.current_session:
        st.info("👈 请在侧边栏创建或选择一个会话")
    else:
        # 创建消息容器
        chat_container = st.container()
        
        # 在容器中显示历史消息
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message(msg['role']):
                    st.markdown(msg['content'])
        
        # 输入框
        if prompt := st.chat_input("发送消息"):
            handle_input(prompt)

if __name__ == "__main__":
    main()

# 页面底部
st.markdown("---")
st.caption("© 2024 Gridseek | Powered by Streamlit") 
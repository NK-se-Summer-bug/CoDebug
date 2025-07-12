import streamlit as st
import requests
import json
from typing import Dict, Any
import time
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title="LLM API 测试工具",
    page_icon="🤖",
    layout="wide"
)

# 全局配置
if "api_base_url" not in st.session_state:
    st.session_state.api_base_url = "http://localhost:8501"

if "session_id" not in st.session_state:
    st.session_state.session_id = f"test_session_{int(time.time())}"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


def make_api_request(endpoint: str, method: str = "GET", data: Dict[Any, Any] = None) -> Dict[Any, Any]:
    """发送API请求"""
    url = f"{st.session_state.api_base_url}{endpoint}"

    try:
        headers = {"Content-Type": "application/json"}

        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            return {"error": f"Unsupported method: {method}"}

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        return {"error": f"请求失败: {str(e)}"}
    except json.JSONDecodeError:
        return {"error": "响应不是有效的JSON格式"}


def display_json_response(response: Dict[Any, Any], title: str = "API响应"):
    """显示JSON响应"""
    st.subheader(title)

    if "error" in response:
        st.error(f"错误: {response['error']}")
    else:
        st.success("请求成功")

    with st.expander("查看完整响应", expanded=True):
        st.json(response)


def main():
    st.title("🤖 LLM API 测试工具")

    # 侧边栏配置
    with st.sidebar:
        st.header("⚙️ 配置")

        # API基础URL配置
        new_base_url = st.text_input(
            "API基础URL",
            value=st.session_state.api_base_url,
            placeholder="http://localhost:8000"
        )

        if new_base_url != st.session_state.api_base_url:
            st.session_state.api_base_url = new_base_url
            st.rerun()

        # 会话ID配置
        st.session_state.session_id = st.text_input(
            "会话ID",
            value=st.session_state.session_id,
            placeholder="test_session_xxx"
        )

        # 连接测试
        st.subheader("🔗 连接测试")
        if st.button("测试连接"):
            try:
                response = requests.get(f"{st.session_state.api_base_url}/models", timeout=5)
                if response.status_code == 200:
                    st.success("✅ 连接成功")
                else:
                    st.error(f"❌ 连接失败: {response.status_code}")
            except Exception as e:
                st.error(f"❌ 连接失败: {str(e)}")

    # 主要功能标签页
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 获取模型列表",
        "💬 对话测试",
        "📚 对话历史",
        "🗑️ 清除历史",
        "📊 会话实例"
    ])

    # 标签页1: 获取模型列表
    with tab1:
        st.header("📋 获取可用模型列表")

        if st.button("获取模型列表", key="get_models"):
            response = make_api_request("/models")
            display_json_response(response)

            # 如果成功获取模型，展示模型信息
            if "models" in response:
                st.subheader("🎯 可用模型")
                for model in response["models"]:
                    with st.expander(f"🤖 {model['model_name']} ({model['provider']})"):
                        st.write(f"**提供商:** {model['provider']}")
                        st.write(f"**描述:** {model['description']}")

    # 标签页2: 对话测试
    with tab2:
        st.header("💬 LLM对话测试")

        col1, col2 = st.columns([2, 1])

        with col1:
            # 对话参数配置
            st.subheader("🎛️ 对话参数")

            user_message = st.text_area(
                "用户消息",
                height=100,
                placeholder="输入你想要发送的消息..."
            )

            model_name = st.text_input(
                "模型名称",
                value="deepseek-chat",
                placeholder="deepseek-chat"
            )

            col_temp, col_max_msg, col_max_tokens = st.columns(3)

            with col_temp:
                temperature = st.slider("温度", 0.0, 2.0, 0.7, 0.1)

            with col_max_msg:
                max_messages = st.number_input("最大消息数", 1, 100, 50)

            with col_max_tokens:
                max_tokens = st.number_input("最大令牌数", 100, 8000, 4000)

            system_prompt_name = st.text_input(
                "系统提示名称",
                value="default",
                placeholder="default"
            )

        with col2:
            st.subheader("📝 操作")

            if st.button("🚀 发送消息", key="send_message", type="primary"):
                if not user_message.strip():
                    st.error("请输入消息内容")
                else:
                    chat_data = {
                        "user_message": user_message,
                        "session_id": st.session_state.session_id,
                        "model_name": model_name,
                        "system_prompt_name": system_prompt_name,
                        "temperature": temperature,
                        "max_messages": max_messages,
                        "max_tokens": max_tokens
                    }

                    with st.spinner("正在发送消息..."):
                        response = make_api_request("/qa/chat", "POST", chat_data)

                    # 保存到聊天历史
                    st.session_state.chat_history.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "user_message": user_message,
                        "response": response,
                        "model_name": model_name
                    })

                    display_json_response(response, "💬 对话响应")

                    # 显示模型切换信息
                    if response.get("model_switched"):
                        st.info(f"🔄 模型已从 {response.get('previous_model')} 切换到 {response.get('model_name')}")

        # 显示本地聊天历史
        if st.session_state.chat_history:
            st.subheader("💭 本次会话历史")
            for i, chat in enumerate(reversed(st.session_state.chat_history[-5:])):  # 只显示最近5条
                with st.expander(
                        f"#{len(st.session_state.chat_history) - i} - {chat['timestamp']} ({chat['model_name']})"):
                    st.write(f"**用户:** {chat['user_message']}")
                    if chat['response'].get('status') == 'success':
                        st.write(f"**AI:** {chat['response']['response_message']}")
                    else:
                        st.error(f"**错误:** {chat['response'].get('error', '未知错误')}")

    # 标签页3: 对话历史
    with tab3:
        st.header("📚 对话历史管理")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("📖 获取对话历史")

            if st.button("获取历史记录", key="get_history"):
                response = make_api_request(f"/qa/memory/{st.session_state.session_id}")
                display_json_response(response)

                # 如果成功获取历史，展示对话内容
                if response.get("status") == "success" and response.get("messages"):
                    st.subheader("🗨️ 对话内容")

                    current_model = response.get("current_model")
                    if current_model:
                        st.info(f"当前使用模型: {current_model}")

                    for i, msg in enumerate(response["messages"]):
                        role_icon = "👤" if msg["role"] == "user" else "🤖"
                        with st.expander(f"{role_icon} {msg['role'].title()} - 消息 #{i + 1}"):
                            st.write(msg["content"])
                elif response.get("status") == "success":
                    st.info("该会话暂无对话历史")

        with col2:
            st.subheader("📊 历史统计")

            if st.button("刷新统计", key="refresh_stats"):
                response = make_api_request(f"/qa/memory/{st.session_state.session_id}")

                if response.get("status") == "success":
                    messages = response.get("messages", [])
                    user_messages = [m for m in messages if m["role"] == "user"]
                    ai_messages = [m for m in messages if m["role"] == "assistant"]

                    st.metric("总消息数", len(messages))
                    st.metric("用户消息", len(user_messages))
                    st.metric("AI回复", len(ai_messages))

                    if response.get("current_model"):
                        st.metric("当前模型", response["current_model"])

    # 标签页4: 清除历史
    with tab4:
        st.header("🗑️ 清除对话历史")

        st.warning("⚠️ 此操作将永久删除指定会话的所有对话历史记录")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("🎯 清除操作")

            session_to_clear = st.text_input(
                "要清除的会话ID",
                value=st.session_state.session_id,
                placeholder="输入会话ID"
            )

            if st.button("🗑️ 清除历史记录", key="clear_history", type="secondary"):
                if session_to_clear.strip():
                    response = make_api_request(f"/qa/memory/{session_to_clear}", "DELETE")
                    display_json_response(response)

                    if response.get("status") == "success":
                        st.success("✅ 历史记录已清除")
                        # 如果清除的是当前会话，也清除本地历史
                        if session_to_clear == st.session_state.session_id:
                            st.session_state.chat_history = []
                else:
                    st.error("请输入有效的会话ID")

        with col2:
            st.subheader("💡 操作说明")
            st.info("""
            **清除历史记录将会:**
            - 删除指定会话的所有对话消息
            - 清除该会话所有模型实例的记忆
            - 保留实例配置，但重置对话状态

            **注意:**
            - 此操作不可逆
            - 会影响该会话的所有模型实例
            """)

    # 标签页5: 会话实例
    with tab5:
        st.header("📊 会话实例管理")

        if st.button("获取会话实例", key="get_instances"):
            response = make_api_request(f"/qa/session/{st.session_state.session_id}/instances")
            display_json_response(response)

            if response.get("status") == "success":
                st.subheader("🎯 实例详情")

                # 显示基本信息
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("总实例数", response.get("total_instances", 0))

                with col2:
                    active_instance = response.get("active_instance")
                    if active_instance:
                        st.metric("活跃实例", active_instance.split("_")[-1])
                    else:
                        st.metric("活跃实例", "无")

                with col3:
                    st.metric("会话ID", response.get("session_id", "未知"))

                # 显示实例列表
                instances = response.get("instances", {})
                if instances:
                    st.subheader("📋 实例列表")

                    for instance_id, instance_info in instances.items():
                        model_name = instance_id.split("_")[-1]
                        is_active = instance_id == active_instance

                        status_icon = "🟢" if is_active else "⚪"
                        status_text = "活跃" if is_active else "非活跃"

                        with st.expander(f"{status_icon} {model_name} - {status_text}"):
                            st.write(f"**实例ID:** {instance_id}")
                            st.write(f"**模型名称:** {instance_info.get('model_name', '未知')}")
                            st.write(f"**创建时间:** {instance_info.get('created_at', '未知')}")
                            st.write(f"**更新时间:** {instance_info.get('updated_at', '未知')}")
                            st.write(f"**消息数量:** {instance_info.get('message_count', 0)}")

                            # 显示配置信息
                            if 'config' in instance_info:
                                config = instance_info['config']
                                st.write(f"**温度:** {config.get('temperature', 'N/A')}")
                                st.write(f"**最大消息数:** {config.get('max_messages', 'N/A')}")
                                st.write(f"**最大令牌数:** {config.get('max_tokens', 'N/A')}")
                else:
                    st.info("该会话暂无实例")

    # 页面底部信息
    st.markdown("---")
    st.markdown("🔧 **当前配置**")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**API URL:** {st.session_state.api_base_url}")
    with col2:
        st.write(f"**会话ID:** {st.session_state.session_id}")


if __name__ == "__main__":
    main()
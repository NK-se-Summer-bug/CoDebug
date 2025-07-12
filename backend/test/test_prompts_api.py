import streamlit as st
import requests
import json
from typing import Optional

# 页面配置
st.set_page_config(
    page_title="Prompt Management API 测试工具",
    page_icon="🔧",
    layout="wide"
)

# 标题
st.title("🔧 Prompt Management API 测试工具")
st.markdown("---")

# 配置部分
st.sidebar.header("⚙️ API 配置")
base_url = st.sidebar.text_input(
    "API Base URL",
    value="http://localhost:8502/api/prompt",
    help="输入您的API基础地址"
)

# 添加连接测试
if st.sidebar.button("测试连接"):
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            st.sidebar.success("✅ 连接成功!")
        else:
            st.sidebar.error(f"❌ 连接失败: {response.status_code}")
    except requests.exceptions.RequestException as e:
        st.sidebar.error(f"❌ 连接错误: {str(e)}")

# 主界面选项卡
tab1, tab2 = st.tabs(["📖 获取系统提示词", "✏️ 更新系统提示词"])

# Tab 1: 获取系统提示词
with tab1:
    st.header("📖 获取当前系统提示词")
    st.markdown("点击按钮获取当前系统提示词内容")

    col1, col2 = st.columns([1, 3])

    with col1:
        if st.button("🔍 获取提示词", type="primary"):
            try:
                with st.spinner("正在获取..."):
                    response = requests.get(f"{base_url}/")

                if response.status_code == 200:
                    data = response.json()
                    st.success("✅ 获取成功!")

                    # 存储到session state供显示
                    st.session_state.current_prompt = data.get("system_prompt", "")

                else:
                    st.error(f"❌ 获取失败: HTTP {response.status_code}")
                    st.json(response.json() if response.content else {})

            except requests.exceptions.RequestException as e:
                st.error(f"❌ 请求错误: {str(e)}")
            except json.JSONDecodeError:
                st.error("❌ 响应格式错误")

    with col2:
        # 显示响应信息
        if hasattr(st.session_state, 'current_prompt') and st.session_state.current_prompt:
            st.info("📄 当前系统提示词:")
            st.text_area(
                "系统提示词内容",
                value=st.session_state.current_prompt,
                height=200,
                disabled=True
            )

# Tab 2: 更新系统提示词
with tab2:
    st.header("✏️ 更新系统提示词")
    st.markdown("输入新的系统提示词内容并更新")

    # 输入区域
    new_prompt = st.text_area(
        "新的系统提示词",
        height=200,
        placeholder="请输入新的系统提示词内容...",
        help="输入您要设置的新系统提示词"
    )

    col1, col2 = st.columns([1, 3])

    with col1:
        if st.button("📝 更新提示词", type="primary", disabled=not new_prompt.strip()):
            try:
                with st.spinner("正在更新..."):
                    payload = {"prompt": new_prompt.strip()}
                    response = requests.post(
                        f"{base_url}/",
                        json=payload,
                        headers={"Content-Type": "application/json"}
                    )

                if response.status_code == 200:
                    data = response.json()
                    st.success("✅ 更新成功!")

                    # 存储响应数据
                    st.session_state.update_response = data

                    # 自动刷新当前提示词
                    st.session_state.current_prompt = data.get("system_prompt", "")

                else:
                    st.error(f"❌ 更新失败: HTTP {response.status_code}")
                    st.json(response.json() if response.content else {})

            except requests.exceptions.RequestException as e:
                st.error(f"❌ 请求错误: {str(e)}")
            except json.JSONDecodeError:
                st.error("❌ 响应格式错误")

    with col2:
        # 显示更新结果
        if hasattr(st.session_state, 'update_response') and st.session_state.update_response:
            st.info("📋 更新结果:")
            response_data = st.session_state.update_response

            st.write(f"**消息**: {response_data.get('msg', 'N/A')}")

            with st.expander("查看更新后的提示词"):
                st.text_area(
                    "更新后的系统提示词",
                    value=response_data.get('system_prompt', ''),
                    height=150,
                    disabled=True
                )

# 底部信息
st.markdown("---")
st.markdown("### 📊 API 接口信息")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **GET /** - 获取系统提示词
    - 方法: GET
    - 响应: `{"system_prompt": "..."}`
    - 用途: 获取当前系统提示词内容
    """)

with col2:
    st.markdown("""
    **POST /** - 更新系统提示词  
    - 方法: POST
    - 请求体: `{"prompt": "..."}`
    - 响应: `{"msg": "...", "system_prompt": "..."}`
    - 用途: 更新系统提示词内容
    """)

# 调试信息
if st.sidebar.checkbox("显示调试信息"):
    st.sidebar.markdown("### 🐛 调试信息")
    st.sidebar.write("Session State:")
    st.sidebar.json(dict(st.session_state))

# 帮助信息
with st.sidebar.expander("ℹ️ 使用帮助"):
    st.markdown("""
    **使用步骤:**
    1. 配置正确的API地址
    2. 点击"测试连接"确认API可用
    3. 使用"获取系统提示词"查看当前内容
    4. 使用"更新系统提示词"修改内容

    **注意事项:**
    - 确保API服务正在运行
    - 检查网络连接和防火墙设置
    - 更新操作会覆盖现有提示词
    """)

# 样式优化
st.markdown("""
<style>
.stButton > button {
    width: 100%;
}
.stTextArea > div > div > textarea {
    font-family: 'Courier New', monospace;
}
</style>
""", unsafe_allow_html=True)
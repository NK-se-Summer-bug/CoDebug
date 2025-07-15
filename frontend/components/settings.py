# -*- coding: utf-8 -*-
"""
设置对话框组件
包含模型设置和提示词设置的UI组件
"""

import streamlit as st
from datetime import datetime
from config.constants import PRESET_PROMPTS
from services.api_service import api_service
from utils.helpers import StateManager


@st.dialog("模型设置")
def show_model_settings():
    """模型设置对话框"""
    # 添加一些上边距
    st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
    
    # 使用容器来添加内边距
    with st.container():
        st.markdown('<div style="padding: 0 20px;">', unsafe_allow_html=True)
        
        # 显示连接状态
        is_connected, status_msg = api_service.check_connectivity()
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
                    StateManager.change_model(selected_model)
                
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
                    StateManager.change_temperature(new_temperature)
            
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
                        st.session_state.available_models = api_service.get_available_models()
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("无法加载模型列表，请检查后端连接。")
            st.markdown('<div style="margin: 20px 0;">', unsafe_allow_html=True)
            if st.button("🔄 重试加载", 
                       help="重新尝试加载模型列表",
                       use_container_width=True):
                st.session_state.available_models = api_service.get_available_models()
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)


@st.dialog("提示词设置")
def show_prompt_settings():
    """提示词设置对话框"""
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
                        success, message = api_service.update_system_prompt(st.session_state.system_prompt)
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
                            success, message = api_service.update_system_prompt(st.session_state.system_prompt)
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
                    success, message = api_service.update_system_prompt("")
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
                        for chunk in api_service.stream_chat_response(
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
                    for chunk in api_service.stream_chat_response(
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
                        StateManager.change_model(model_name)
                        st.rerun()


def test_triplet_extraction():
    """测试三元组提取功能"""
    from utils.helpers import extract_and_store_triplets
    
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

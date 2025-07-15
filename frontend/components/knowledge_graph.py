# -*- coding: utf-8 -*-
"""
知识图谱组件
包含知识图谱的渲染和三元组管理功能
"""

import streamlit as st
import streamlit.components.v1 as components
from utils.helpers import GraphUtils, extract_and_store_triplets
from config.constants import DEFAULT_GRAPH_HEIGHT


def render_knowledge_graph():
    """渲染知识图谱"""
    triplets = st.session_state.get('triplets', [])
    if not triplets:
        st.info("当前还没有可显示的知识三元组。")
        return
    
    # 直接渲染图谱 - 与原始文件保持一致
    dynamic_html = GraphUtils.generate_dynamic_graph_html(triplets)
    components.html(dynamic_html, height=600, scrolling=True)


def show_triplet_management():
    """显示三元组管理界面"""
    st.subheader("📊 知识三元组管理")
    
    # 显示当前三元组统计
    triplets = st.session_state.get('triplets', [])
    st.info(f"当前共有 {len(triplets)} 个知识三元组")
    
    # 三元组操作按钮
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 查看所有三元组", use_container_width=True):
            if triplets:
                with st.expander("所有知识三元组", expanded=True):
                    for i, triplet in enumerate(triplets, 1):
                        st.write(f"{i}. **{triplet.get('h', '')}** --[{triplet.get('r', '')}]--> **{triplet.get('t', '')}**")
            else:
                st.warning("暂无三元组数据")
    
    with col2:
        if st.button("🗑 清空三元组", use_container_width=True, type="secondary"):
            if triplets:
                st.session_state.triplets = []
                st.success("已清空所有三元组")
                st.rerun()
            else:
                st.warning("暂无三元组可清空")
    
    with col3:
        if st.button("🔄 重新渲染图谱", use_container_width=True):
            st.rerun()
    
    # 手动添加三元组
    st.subheader("✏️ 手动添加三元组")
    
    with st.form("add_triplet_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            head_entity = st.text_input("头实体", placeholder="例如：人工智能")
        
        with col2:
            relation = st.text_input("关系", placeholder="例如：是")
        
        with col3:
            tail_entity = st.text_input("尾实体", placeholder="例如：计算机科学的分支")
        
        submitted = st.form_submit_button("添加三元组", use_container_width=True)
        
        if submitted:
            if head_entity and relation and tail_entity:
                new_triplet = {
                    'h': head_entity.strip(),
                    'r': relation.strip(),
                    't': tail_entity.strip()
                }
                
                existing_triplets = st.session_state.get('triplets', [])
                if new_triplet not in existing_triplets:
                    existing_triplets.append(new_triplet)
                    st.session_state.triplets = existing_triplets
                    st.success(f"已添加三元组: **{head_entity}** --[{relation}]--> **{tail_entity}**")
                    st.rerun()
                else:
                    st.warning("该三元组已存在")
            else:
                st.error("请填写完整的三元组信息")
    
    # 从文本提取三元组
    st.subheader("🔍 从文本提取三元组")
    
    extract_text = st.text_area(
        "输入文本内容",
        placeholder="在这里输入要提取知识三元组的文本...",
        height=120
    )
    
    # 添加自定义CSS样式来修复按钮颜色问题
    st.markdown("""
    <style>
    /* 修复提取三元组按钮的颜色问题 */
    div.stButton > button[kind="primary"] {
        background-color: #ff4b4b !important;
        color: white !important;
        border-color: #ff4b4b !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #ff6b6b !important;
        color: white !important;
        border-color: #ff6b6b !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    if st.button("🔍 提取三元组", use_container_width=True, type="primary"):
        if extract_text:
            extract_and_store_triplets(extract_text)
            st.rerun()
        else:
            st.error("请输入文本内容")

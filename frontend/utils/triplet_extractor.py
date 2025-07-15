# -*- coding: utf-8 -*-
"""
三元组提取模块
包含从文本中提取知识三元组的功能
"""

import streamlit as st


class TripletExtractor:
    """三元组提取器"""
    
    @staticmethod
    def extract_and_store_triplets(text: str) -> bool:
        """从文本中提取三元组并存储到session_state"""
        from services.api_service import api_service
        
        try:
            if not text or len(text.strip()) < 10:
                st.warning("文本内容过短，无法提取有效的三元组")
                return False
                
            with st.spinner("正在提取知识三元组..."):
                success, new_triplets = api_service.extract_triplets(text)
                
                if success and new_triplets:
                    # 获取现有三元组
                    existing_triplets = st.session_state.get('triplets', [])
                    
                    # 将新的三元组添加进去，同时去重
                    added_count = 0
                    for triplet in new_triplets:
                        if triplet not in existing_triplets:
                            existing_triplets.append(triplet)
                            added_count += 1
                    
                    st.session_state.triplets = existing_triplets
                    
                    # 同时更新当前会话的三元组存储
                    if st.session_state.current_session:
                        if not hasattr(st.session_state, 'session_triplets'):
                            st.session_state.session_triplets = {}
                        st.session_state.session_triplets[st.session_state.current_session] = existing_triplets
                    
                    st.toast(f"提取到 {len(new_triplets)} 个知识三元组，新增 {added_count} 个！", icon="✨")
                    return True
                else:
                    st.warning("未能从文本中提取到任何三元组")
                    return False
                    
        except Exception as e:
            st.error(f"处理三元组时出错: {e}")
            return False
    
    @staticmethod
    def clear_triplets():
        """清空当前所有三元组"""
        st.session_state.triplets = []
        
        # 同时清空当前会话的三元组存储
        if st.session_state.current_session:
            if not hasattr(st.session_state, 'session_triplets'):
                st.session_state.session_triplets = {}
            st.session_state.session_triplets[st.session_state.current_session] = []
        
        st.success("已清空所有知识三元组")
    
    @staticmethod
    def get_triplets_count() -> int:
        """获取当前三元组数量"""
        return len(st.session_state.get('triplets', []))
    
    @staticmethod
    def export_triplets() -> dict:
        """导出当前所有三元组"""
        return {
            'triplets': st.session_state.get('triplets', []),
            'count': TripletExtractor.get_triplets_count(),
            'export_time': st.session_state.get('export_time', None)
        }


# 为了保持向后兼容性，保留原来的函数名
def extract_and_store_triplets(text: str) -> bool:
    """从文本中提取三元组并存储到session_state（保持向后兼容性）"""
    return TripletExtractor.extract_and_store_triplets(text)

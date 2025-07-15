# -*- coding: utf-8 -*-
"""
样式配置模块
包含所有CSS样式定义
"""

# 主要CSS样式 - 完全复制自原始app.py文件
MAIN_CSS = """
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

/* 修复提取三元组按钮的颜色问题 */
.stButton[data-testid="baseButton-primary"] > button {
    background-color: #ff4b4b !important;
    color: white !important;
}

.stButton[data-testid="baseButton-primary"] > button:hover {
    background-color: #ff6b6b !important;
    color: white !important;
}

/* 确保emoji正确显示 */
.stMarkdown, .stText, .stChatMessage, .chat-message {
    font-family: "Segoe UI", "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", sans-serif !important;
}

/* 改善emoji渲染 */
.emoji {
    font-family: "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", "Android Emoji", "EmojiSymbols", sans-serif;
    font-size: 1.2em;
}

/* 确保思考状态的emoji正确显示 */
.thinking-status {
    font-family: "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", sans-serif;
    color: #666;
    font-style: italic;
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
"""

# Agent界面特殊样式 - 复制自原始app.py
AGENT_CSS = """
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
"""

# 侧边栏特殊样式 - 复制自原始app.py侧边栏部分
SIDEBAR_CSS = """
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
"""

# 设置界面样式
SETTINGS_CSS = """
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
"""

# 获取所有CSS样式的统一函数
def get_all_css():
    """获取所有CSS样式"""
    return MAIN_CSS + AGENT_CSS + SIDEBAR_CSS + SETTINGS_CSS

def get_css():
    """保持兼容性的获取CSS函数"""
    return get_all_css()

# Gridseek 前端系统

## 项目简介

Gridseek 是一个智能对话系统的前端界面，提供多模型AI对话、智能Agent、知识图谱可视化等功能。本项目采用模块化架构设计，便于维护和扩展。

## 项目结构

```
frontend/
├── app.py                      # 重构后的主应用入口
├── graph.html                  # 知识图谱可视化模板
├── requirements.txt            # 项目依赖
├── README.md                  # 项目说明文档
├── chat_history.json          # 聊天历史数据（运行时生成）
│
├── config/                     # 配置模块
│   ├── __init__.py
│   └── constants.py           # 常量配置（API地址、预设提示词等）
│
├── services/                   # 服务模块
│   ├── __init__.py
│   └── api_service.py         # API服务（后端通信、模型调用等）
│
├── utils/                      # 工具模块
│   ├── __init__.py
│   └── helpers.py             # 工具函数（会话管理、图谱生成等）
│
├── components/                 # UI组件模块
│   ├── __init__.py
│   ├── chat.py                # 聊天界面组件
│   ├── agent.py               # 智能Agent组件
│   ├── knowledge_graph.py     # 知识图谱组件
│   └── settings.py            # 设置界面组件
│
└── styles/                     # 样式模块
    ├── __init__.py
    └── css.py                 # CSS样式定义
```

## 核心模块说明

### 1. 配置模块 (`config/`)

#### `constants.py`
- **功能**: 存储所有系统常量和配置
- **内容**: 
  - 预设提示词配置
  - API地址和超时设置
  - 默认参数（模型、温度等）
  - 文件路径配置

### 2. 服务模块 (`services/`)

#### `api_service.py`
- **功能**: 处理与后端API的所有通信
- **主要类**: `APIService`
- **核心方法**:
  - `check_connectivity()`: 检查后端连接状态
  - `get_available_models()`: 获取可用模型列表
  - `stream_chat_response()`: 流式聊天响应
  - `get_conversation_history()`: 获取会话历史
  - `extract_triplets()`: 提取知识三元组
  - `run_agent_task()`: 运行Agent任务

### 3. 工具模块 (`utils/`)

#### `helpers.py`
- **功能**: 提供通用工具函数和类
- **主要类**:
  - `SessionManager`: 会话管理（创建、切换、删除会话）
  - `GraphUtils`: 知识图谱工具（HTML生成、颜色管理）
  - `StateManager`: 状态管理（初始化、切换设置）

### 4. UI组件模块 (`components/`)

#### `chat.py`
- **功能**: 聊天界面相关组件
- **主要函数**:
  - `show_chat_interface()`: 主聊天界面
  - `show_sidebar()`: 侧边栏（会话列表、设置按钮）

#### `agent.py`
- **功能**: 智能Agent相关组件
- **主要函数**:
  - `show_agent_interface()`: Agent主界面
  - `_show_agent_selection()`: Agent选择界面
  - `_show_agent_chat()`: Agent聊天界面

#### `knowledge_graph.py`
- **功能**: 知识图谱相关组件
- **主要函数**:
  - `render_knowledge_graph()`: 渲染知识图谱
  - `show_triplet_management()`: 三元组管理界面

#### `settings.py`
- **功能**: 设置界面组件
- **主要函数**:
  - `show_model_settings()`: 模型设置对话框
  - `show_prompt_settings()`: 提示词设置对话框
  - `test_model_switching()`: 模型切换测试

### 5. 样式模块 (`styles/`)

#### `css.py`
- **功能**: 存储所有CSS样式定义
- **内容**:
  - `MAIN_CSS`: 主要界面样式
  - `AGENT_CSS`: Agent界面特殊样式
  - `SETTINGS_CSS`: 设置界面样式

## 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行应用

#### 运行应用：
```bash
streamlit run app.py
```

## 主要功能

### 1. 多模型AI对话
- 支持多种AI模型切换
- 可调节创造性参数（Temperature）
- 流式响应显示

### 2. 智能Agent系统
- 支持多种专业Agent
- 工具状态检测
- 独立Agent会话管理

### 3. 知识图谱可视化
- 自动从对话中提取知识三元组
- 可视化知识关系图
- 手动添加和管理三元组

### 4. 会话管理
- 多会话支持
- 会话历史保存和恢复
- 会话导入导出

### 5. 系统设置
- 模型配置管理
- 自定义提示词设置
- 连接状态监控

## 技术特点

### 1. 模块化架构
- 单一职责原则
- 低耦合高内聚
- 便于测试和维护

### 2. 组件化UI
- 可复用组件设计
- 样式分离
- 响应式布局

### 3. 状态管理
- 集中式状态管理
- 持久化支持
- 状态同步

### 4. 错误处理
- 全面的异常捕获
- 用户友好的错误提示
- 降级处理机制

## 开发指南

### 1. 添加新功能
1. 在相应模块中添加功能代码
2. 在 `app.py` 中导入和调用
3. 更新配置和样式（如需要）

### 2. 修改UI组件
1. 编辑 `components/` 目录下的相应文件
2. 更新 `styles/css.py` 中的样式（如需要）
3. 测试组件功能

### 3. 添加新的API接口
1. 在 `services/api_service.py` 中添加方法
2. 在相应的组件中调用
3. 处理错误和异常情况

### 4. 配置管理
1. 在 `config/constants.py` 中添加新的配置项
2. 在需要的地方导入使用
3. 保持配置的一致性

## 注意事项

### 1. 文件依赖
- `graph.html`: 知识图谱可视化需要此模板文件
- `chat_history.json`: 运行时自动生成，存储聊天历史

### 2. 后端依赖
- 需要后端API服务运行在 `http://localhost:8000`
- 确保后端服务正常运行才能使用全部功能

### 3. 性能考虑
- 大量三元组可能影响图谱渲染性能
- 建议定期清理无用的聊天历史

## 故障排除

### 1. 模块导入错误
- 确保所有 `__init__.py` 文件存在
- 检查Python路径设置
- 验证文件结构完整性

### 2. API连接失败
- 检查后端服务状态
- 验证API地址配置
- 查看网络连接

### 3. 样式显示异常
- 清除浏览器缓存
- 检查CSS文件完整性
- 验证Streamlit版本兼容性

## 版本历史

### v2.0.0 (重构版本)
- 模块化架构重构
- 组件化UI设计
- 改进的错误处理
- 更好的代码组织

### v1.0.0 (原始版本)
- 单体应用设计
- 基础功能实现
- 简单的文件结构

## 联系方式

如有问题或建议，请联系开发团队。

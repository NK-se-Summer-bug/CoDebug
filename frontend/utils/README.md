# Utils模块重构说明

## 概述

原来的`helpers.py`文件包含了多种不同的功能，为了提高代码的可维护性和模块化程度，已将其拆分为多个专门的模块。

## 新的模块结构

### 1. session_manager.py
**功能**: 会话管理
- `SessionManager`: 会话管理器类
  - `save_chat_history()`: 保存聊天历史
  - `load_chat_history()`: 加载聊天历史  
  - `create_new_session()`: 创建新会话
  - `switch_session()`: 切换会话
  - `clear_session()`: 清空当前会话
  - `delete_session()`: 删除会话

### 2. graph_manager.py
**功能**: 知识图谱管理
- `GraphManager`: 知识图谱管理器类
  - `get_random_color()`: 生成随机颜色
  - `generate_dynamic_graph_html()`: 生成动态图谱HTML
  - `_load_graph_template()`: 加载图谱模板
- `GraphUtils`: 保持向后兼容的别名

### 3. state_manager.py
**功能**: 状态管理
- `StateManager`: 状态管理器类
  - `init_session_state()`: 初始化session state
  - `toggle_knowledge_graph()`: 切换知识图谱显示
  - `change_model()`: 切换AI模型
  - `change_temperature()`: 更改模型温度
  - `toggle_agent_page()`: 切换Agent页面
  - `reset_agent_state()`: 重置Agent状态
  - `toggle_model_settings()`: 切换模型设置对话框
  - `toggle_prompt_settings()`: 切换提示词设置对话框

### 4. triplet_extractor.py
**功能**: 三元组提取
- `TripletExtractor`: 三元组提取器类
  - `extract_and_store_triplets()`: 提取并存储三元组
  - `clear_triplets()`: 清空所有三元组
  - `get_triplets_count()`: 获取三元组数量
  - `export_triplets()`: 导出三元组数据
- `extract_and_store_triplets()`: 保持向后兼容的函数

### 5. helpers.py
**功能**: 向后兼容性
- 导入所有新模块的类和函数
- 确保原有的导入方式仍然有效
- 包含重构说明和新模块结构的文档

## 使用方式

### 推荐的新方式
```python
# 使用专门的模块
from utils.session_manager import SessionManager
from utils.graph_manager import GraphManager
from utils.state_manager import StateManager
from utils.triplet_extractor import TripletExtractor
```

### 保持兼容的旧方式
```python
# 原有的导入方式仍然有效
from utils.helpers import SessionManager, GraphUtils, StateManager
from utils.helpers import extract_and_store_triplets
```

## 优势

1. **模块化**: 每个模块专注于特定功能
2. **可维护性**: 代码更容易理解和修改
3. **可扩展性**: 新功能可以轻松添加到相应模块
4. **向后兼容**: 原有代码无需修改
5. **清晰的职责分离**: 会话、图谱、状态、三元组各司其职

## 注意事项

- 所有原有的导入方式都保持兼容
- 新功能建议使用新的模块结构
- `helpers.py`现在主要用于兼容性，新代码建议直接导入专门模块

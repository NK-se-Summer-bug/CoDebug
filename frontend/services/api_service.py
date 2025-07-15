# -*- coding: utf-8 -*-
"""
API服务模块
处理与后端API的所有通信
"""

import requests
import json
import streamlit as st
from typing import Generator, Tuple, List, Dict, Any, Optional
from config.constants import API_BASE_URL, API_TIMEOUT


class APIService:
    """API服务类，处理所有后端通信"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
    
    def check_connectivity(self) -> Tuple[bool, str]:
        """检查后端连接状态"""
        try:
            response = requests.get(f'{self.base_url}/models', timeout=5)
            response.raise_for_status()
            return True, "后端连接正常"
        except requests.RequestException as e:
            return False, f"后端连接失败: {e}"
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """获取可用模型列表"""
        try:
            response = requests.get(f'{self.base_url}/models', timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('models', [])
        except requests.RequestException as e:
            st.error(f"加载模型列表失败: {e}")
            # 返回默认模型列表作为备选
            return [
                {"model_name": "gpt-4o-mini", "description": "OpenAI GPT-4o-mini, 性能优秀，成本较低。", "provider": "GPT"},
                {"model_name": "deepseek-chat", "description": "DeepSeek Chat, 中文表现优秀的开源模型。", "provider": "DeepSeek"}
            ]
        except Exception as e:
            st.error(f"处理模型列表时出错: {e}")
            return []
    
    def stream_chat_response(self, user_message: str, session_id: str, 
                           model_name: str, temperature: float, 
                           system_prompt: str) -> Generator[str, None, None]:
        """流式聊天响应"""
        try:
            response = requests.post(
                f'{self.base_url}/qa/chat',
                json={
                    'user_message': user_message,
                    'session_id': session_id,
                    'model_name': model_name,
                    'temperature': temperature,
                    'system_prompt_name': 'current'
                },
                stream=True,
                timeout=API_TIMEOUT
            )
            response.raise_for_status()
            
            for line in response.iter_lines(decode_unicode=True):
                if line.strip():
                    if line.startswith('data: '):
                        try:
                            data = json.loads(line[6:])
                            if data.get('type') == 'content':
                                chunk = data.get('content', '')
                                if chunk:
                                    yield chunk
                            elif data.get('type') == 'end':
                                break
                            elif data.get('type') == 'error':
                                raise Exception(data.get('error', '未知错误'))
                        except json.JSONDecodeError:
                            continue
                            
        except requests.RequestException as e:
            raise Exception(f"请求失败: {e}")
        except Exception as e:
            raise Exception(f"处理响应时出错: {e}")
    
    def get_conversation_history(self, session_id: str) -> Tuple[List[Dict], Optional[str]]:
        """获取会话历史"""
        try:
            response = requests.get(f'{self.base_url}/qa/memory/{session_id}', timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'success':
                return data.get('messages', []), data.get('current_model')
            else:
                return [], None
        except requests.RequestException as e:
            st.error(f"获取会话历史失败: {e}")
            return [], None
    
    def clear_conversation_history(self, session_id: str) -> bool:
        """清空会话历史"""
        try:
            response = requests.delete(f'{self.base_url}/qa/memory/{session_id}', timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'success':
                return True
            else:
                st.error(f"清空历史失败: {data.get('error', '未知错误')}")
                return False
        except requests.RequestException as e:
            st.error(f"清空会话历史失败: {e}")
            return False
    
    def load_system_prompt(self) -> str:
        """加载系统提示词"""
        try:
            response = requests.get(f'{self.base_url}/api/prompt/', timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('system_prompt', '')
        except requests.RequestException:
            return ''
        except Exception:
            return ''
    
    def update_system_prompt(self, prompt: str) -> Tuple[bool, str]:
        """更新系统提示词"""
        try:
            response = requests.post(
                f'{self.base_url}/api/prompt/',
                json={'prompt': prompt},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get('msg'):
                return True, data.get('msg')
            else:
                return False, "更新失败"
        except requests.RequestException as e:
            return False, f"更新失败: {e}"
    
    def extract_triplets(self, text: str) -> Tuple[bool, List[Dict]]:
        """从文本中提取三元组"""
        try:
            if not text or len(text.strip()) < 10:
                return False, []
                
            response = requests.post(
                f'{self.base_url}/api/kg/extract',
                json={'text': text},
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            triplets = data.get("triples", [])
            
            return len(triplets) > 0, triplets
            
        except requests.RequestException as e:
            st.error(f"提取知识三元组失败：{e}")
            return False, []
        except Exception as e:
            st.error(f"处理三元组时出错: {e}")
            return False, []
    
    def get_available_agents(self) -> List[Dict]:
        """加载可用的Agent列表"""
        try:
            response = requests.get(f'{self.base_url}/api/agent/agents', timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('agents', [])
        except requests.RequestException as e:
            st.error(f"加载Agent列表失败: {e}")
            return []
    
    def run_agent_task(self, agent_name: str, user_input: str, session_id: str,
                      model_name: str, system_prompt_name: str = 'default') -> str:
        """运行Agent任务"""
        try:
            response = requests.post(
                f'{self.base_url}/api/agent/agent/run',
                json={
                    'agent_name': agent_name,
                    'user_input': user_input,
                    'session_id': session_id,
                    'llm_model_name': model_name,
                    'system_prompt_name': system_prompt_name,
                    'memory_window': 10
                },
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            if result['status'] == 'success':
                return result['result']
            else:
                raise Exception(result.get('error', '未知错误'))
                
        except requests.RequestException as e:
            raise Exception(f"Agent任务执行失败: {e}")
        except Exception as e:
            raise Exception(f"处理Agent响应时出错: {e}")


# 创建全局API服务实例
api_service = APIService()

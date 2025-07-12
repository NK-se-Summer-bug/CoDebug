import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from ..all_managers.llm_manager import LLMManager

# 加载.env文件
load_dotenv()

class LLMHelper:
    def __init__(self):
        # 默认模型保持不变，用于向后兼容
        self.llm = ChatOpenAI(
            openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
            openai_api_base=os.getenv("DEEPSEEK_API_BASE"),
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            temperature=float(os.getenv("DEEPSEEK_TEMPERATURE", 0.7))
        )

    async def get_completion_from_messages(self, messages, system_prompt=None, model_name=None, temperature=0.7):
        """
        获取指定模型的回复
        """
        # 如果指定了模型名称，使用LLMManager获取对应模型
        if model_name:
            try:
                llm = LLMManager.get_llm(model_name, temperature)
            except ValueError as e:
                raise ValueError(f"Invalid model: {e}")
        else:
            # 使用默认模型
            llm = self.llm
            
        chat_messages = []
        
        # 始终将system_prompt作为第一条消息（如果有）
        if system_prompt:
            chat_messages.append(SystemMessage(content=system_prompt))
            print(f"[DEBUG] 添加系统提示词: {system_prompt}")
        
        # 添加历史消息，但跳过system消息（因为我们已经添加了system_prompt）
        for msg in messages:
            if msg['role'] == 'user':
                chat_messages.append(HumanMessage(content=msg['content']))
                print(f"[DEBUG] 添加用户消息: {msg['content']}")
        
        print(f"[DEBUG] 最终消息列表: {[{type(msg).__name__: msg.content} for msg in chat_messages]}")
        
        # 使用更稳定的调用方式
        try:
            # 优先尝试异步调用
            if hasattr(llm, 'ainvoke'):
                response = await llm.ainvoke(chat_messages)
            else:
                # 如果没有异步方法，使用同步方法
                response = llm.invoke(chat_messages)
            
            # 统一处理不同类型的响应
            if hasattr(response, 'content'):
                return response.content
            elif hasattr(response, 'text'):
                return response.text
            else:
                # 如果都没有，尝试字符串转换
                result = str(response)
                if result and result != 'None':
                    return result
                else:
                    return "模型返回了空响应"
                    
        except Exception as e:
            # 如果异步调用失败，尝试同步调用
            try:
                print(f"[DEBUG] 异步调用失败，尝试同步调用: {e}")
                response = llm.invoke(chat_messages)
                if hasattr(response, 'content'):
                    return response.content
                elif hasattr(response, 'text'):
                    return response.text
                else:
                    result = str(response)
                    return result if result and result != 'None' else "模型返回了空响应"
            except Exception as sync_e:
                raise Exception(f"模型调用失败 - 异步错误: {e}, 同步错误: {sync_e}")

    async def ask_question(self, question, system_prompt=None, model_name=None, temperature=0.7):
        """
        向指定模型提问
        """
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': question})
        return await self.get_completion_from_messages(messages, system_prompt, model_name, temperature)

# 单例实例，便于全局调用
llm_helper = LLMHelper() 
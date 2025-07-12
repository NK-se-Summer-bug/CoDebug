# all_managers/llm_manager.py
from typing import Dict, Any
from langchain_core.language_models.chat_models import BaseChatModel

from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from langchain_community.chat_models import ChatZhipuAI
from langchain_community.chat_models import ChatTongyi
from langchain_community.chat_models import ChatSparkLLM
#from langchain_google_genai import ChatGoogleGenerativeAI

import os
from dotenv import load_dotenv
load_dotenv()

class AvaliableLLMs:
    """
    可用的LLM模型列表
    """
    GPT="gpt-4o-mini"
    DeepSeek="deepseek-chat"
    Zhipu="glm-4-air"
    Qwen="qwen-max"
    Spark="Spark X1"
    #Gemini="gemini-2.5-flash"

class LLMManager:
    _available_models_info = {
        "gpt-4o-mini": {"provider": "GPT"},
        "deepseek-chat": {"provider": "DeepSeek"},
        "glm-4-air": {"provider": "Zhipu"},
        "qwen-max": {"provider": "Qwen"},
        "Spark X1": {"provider": "Spark"},
        #"gemini-2.5-flash": {"provider": "Gemini"},
    }
    _llm_instances: Dict[str, BaseChatModel] = {}

    @classmethod
    def get_llm(cls, model_name: str, temperature: float = 0.7) -> BaseChatModel:
        """
        param model_name: str - 准确模型名称
        param temperature: float - 温度参数，默认值为0.7
        return: BaseChatModel - 返回指定模型的实例
        """
        if model_name not in cls._available_models_info:
            raise ValueError(f"LLM model '{model_name}' is not configured.")

        if model_name in cls._llm_instances and cls._llm_instances[model_name].temperature == temperature:
            return cls._llm_instances[model_name]

        # 若尚未初始化，根据需要创建
        model_config = cls._available_models_info[model_name]
        provider = model_config["provider"]
        if provider == "GPT":
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                api_key=os.environ["OPENAI_API_KEY"],
                base_url=os.environ["OPENAI_API_BASE"],
                temperature=temperature,
            )
        elif provider == "DeepSeek":
            llm = ChatDeepSeek(
                model=model_name,
                api_key=os.environ["DEEPSEEK_API_KEY"],
                base_url=os.environ["DEEPSEEK_API_BASE"],
                temperature=temperature,
            )
        elif provider == "Zhipu":
            llm = ChatZhipuAI(
                model=model_name,
                api_key=os.environ["ZHIPU_API_KEY"],
                base_url=os.environ["ZHIPU_API_BASE"],
                temperature=temperature,
            )
        elif provider == "Qwen":
            llm = ChatTongyi(
                model=model_name,
                api_key=os.environ["QWEN_API_KEY"],
                temperature=temperature,
            )
        elif provider == "Spark":
            llm = ChatSparkLLM(
                model=model_name,
                api_key=os.environ["SPARK_API_KEY"],
                api_secret=os.environ["SPARK_API_SECRET"],
                spark_app_id=os.environ["SPARK_APP_ID"],
                api_url=os.environ["SPARK_API_BASE"],
                temperature=temperature,
            )
        # Gemini加载速度较慢，暂不使用
        # elif provider == "Gemini":
        #     llm = ChatGoogleGenerativeAI(
        #         model=model_name,
        #         google_api_key=os.environ["GEMINI_API_KEY"],
        #         temperature=temperature,
        #     )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

        cls._llm_instances[model_name] = llm
        return llm

    @classmethod
    def get_available_llms_info(cls) -> Dict[str, Any]:
        """
        获取可用的LLM模型信息
        return: Dict[str, Any] - 返回可用模型的字典信息
        Key:实际模型名称
        Value[provider]:调用名称标识
        """
        return cls._available_models_info

if __name__ == "__main__":
    # 测试LLMManager
    try:
        '''
        get_llm方法的使用示例
        调用传参model_name/temperature(default=0.7)
        此处对可用LLM模型名称进行了封装，导包后eg:AvaliableLLMs.Zhipu
        
        导包指令：
        from all_managers.llm_manager import LLMManager, AvaliableLLMs
        '''
        llm = LLMManager.get_llm(model_name=AvaliableLLMs.Zhipu, temperature=0.5)
        print(f"Successfully retrieved LLM")
        response = llm.invoke(input="你好，介绍一下你自己")
        print(response.content)  # 打印AI的响应内容0
    except ValueError as e:
        print(e)
    print("=" * 40)
    available_models = LLMManager.get_available_llms_info()
    print("Available LLMs:", available_models)
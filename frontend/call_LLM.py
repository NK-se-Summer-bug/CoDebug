from openai import OpenAI
import openai
from typing import Generator, Union
import time

def gen_gpt_message(prompt:str):
    """
    : param prompt: str, 用户输入的消息
    : return: message, list, 发送给GPT模型的消息列表
    依据prompt，封装GPT模型请求消息
    """
    message = [
        {
            "role": "user",
            "content": prompt
        }
    ]
    return message
# 获取LLM的返回信息
def get_completion(messages:list, model:str, url, api_key, temperature:float = 0):
    client = OpenAI(
    base_url=url,
    api_key=api_key,
    )
    print("传递给AI的message为：", messages)
    try:
        print("进入try")
        response = client.chat.completions.create(
            model=model,
            messages = messages,
            temperature = temperature,
            stream = True
        )
        print("response对象：", response)
        # got_chunk = False
        for chunk in response: # 迭代API返回的Stream
            yield chunk
    except openai.APIConnectionError as e:
        print(f"API 连接错误: {e}")
        yield f"API 连接失败: {e}"
    except openai.APIStatusError as e: # 捕获HTTP状态码错误 (4xx, 5xx)
        print(f"API 状态错误 ({e.status_code}): {e.response}")
        yield f"API 错误: {e.response.json().get('error', {}).get('message', '未知API错误')}"
    except Exception as e:
        print(f"发生未知错误: {e}")
        yield f"未知错误: {e}"

def get_llm_response(
    model: str, 
    messages: list, 
    api_key: str, 
    api_base: str
) -> Union[str, Generator[str, None, None]]:
    # --- 1. ChatGPT / Deepseek 等兼容OpenAI API的系列模型 ---
    if model.startswith("ChatGPT") or model.startswith("Deepseek"):
        if not api_key:
            return "错误：请输入您的API Key。"
        
        url = api_base if api_base else "https://api.openai.com/v1/chat/completions"
        if model.startswith("Deepseek"):
            url = api_base if api_base else "https://api.deepseek.com/v1"

        model_id = ""
        if model == "ChatGPT-4":
            model_id = "gpt-4"
        elif model == "ChatGPT-3.5":
            model_id = "gpt-3.5-turbo"
        elif model == "Deepseek-V2":
            model_id = "deepseek-chat"
        
        print("调用get_completion!")
        response = get_completion(messages, model_id, url, api_key)
        # print("response is: ",response)
        # print("直接输出chunk str！")
        for chunk in response:
            if isinstance(chunk, str):
                # yield chunk
                continue
            if chunk is not str and chunk.choices and chunk.choices[0].delta.content is not None:
                # yield chunk.choices[0].delta.content
                print(chunk.choices[0].delta.content)

        # yield response # 返回的是一个生成器
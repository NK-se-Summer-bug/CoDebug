from fastapi import APIRouter, Body
from ...core.langchain_helper import llm_helper
from ...all_managers.llm_manager import LLMManager

router = APIRouter()

@router.post("")
async def qa(
    question: str = Body(...), 
    system_prompt: str = Body(""),
    model_name: str = Body("gpt-4o-mini"),  # 新增模型参数，默认使用gpt-4o-mini
    temperature: float = Body(0.7)  # 新增温度参数
):
    # 表示 question 参数的值将从请求的 JSON 体中获取。如果请求体中没有 {"question": "..."} 这样的键值对，FastAPI 会返回错误。
    # 如果请求体中没有 {"system_prompt": "..."} 这样的键值对，FastAPI 会使用默认值 ""。
    try:
        # 验证模型是否可用
        available_models = LLMManager.get_available_llms_info()
        if model_name not in available_models:
            return {
                "response_message": "",
                "model_name": model_name,
                "status": "error",
                "error": f"Invalid model_name. Available models: {list(available_models.keys())}"
            }
        
        # 使用指定模型回答问题
        answer = await llm_helper.ask_question(question, system_prompt, model_name, temperature)
        return {
            "response_message": answer,
            "model_name": model_name,
            "status": "success"
        }
    except Exception as e:
        print(f"Error in qa endpoint: {e}") # 添加这一行，捕获并打印异常
        import traceback
        traceback.print_exc() # 打印完整的错误堆栈
        return {
            "response_message": "",
            "model_name": model_name,
            "status": "error",
            "error": str(e)
        }

@router.get("/models")
async def get_available_models():
    """获取所有可用的LLM模型"""
    try:
        available_models_info = LLMManager.get_available_llms_info()
        
        # 根据文档格式转换响应
        models_list = []
        model_descriptions = {
            "gpt-4o-mini": "OpenAI GPT-4o-mini, 性能优秀，成本较低。",
            "deepseek-chat": "DeepSeek Chat, 中文表现优秀的开源模型。",
            "glm-4-air": "智谱清言 GLM-4-air, 轻量级高效模型。",
            "qwen-max": "阿里通义千问 Qwen-max, 综合能力强。",
            "Spark X1": "科大讯飞星火 Spark X1, 语音和文本处理优秀。"
        }
        
        for model_name, model_info in available_models_info.items():
            models_list.append({
                "model_name": model_name,
                "description": model_descriptions.get(model_name, f"{model_info['provider']} 模型")
            })
        
        return models_list
    except Exception as e:
        print(f"Error in get_available_models endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise
if __name__ == "__main__":
    models_list=get_available_models()
    print(models_list)  # 打印模型列表以验证输出
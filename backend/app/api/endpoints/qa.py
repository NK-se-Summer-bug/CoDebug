from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from ...core.rte import get_completion_from_messages, rte_from_text
import json
import asyncio
import re

router = APIRouter()

class Message(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None

class QARequest(BaseModel):
    message: str
    system_prompt: str = ""
    conversation_history: Optional[List[Message]] = []

@router.post("")
async def qa(request: QARequest):
    """
    QA API endpoint - 支持关系抽取
    """
    try:
        messages = []
        if request.system_prompt:
            messages.append({'role': 'system', 'content': request.system_prompt})
        
        # 添加对话历史
        if request.conversation_history:
            for msg in request.conversation_history:
                messages.append({'role': msg.role, 'content': msg.content})
            print(f"📚 添加历史对话: {len(request.conversation_history)} 条消息")
        
        # 添加当前用户消息
        messages.append({'role': 'user', 'content': request.message})
        
        print(f"🚀 收到QA请求，总消息数: {len(messages)}")
        message_overview = []
        for m in messages:
            message_overview.append(f"{m['role']}: {m['content'][:30]}...")
        print(f"📜 消息概览: {message_overview}")
        
        # 获取AI回答
        answer = get_completion_from_messages(messages, model="deepseek-chat", temperature=0.7)
        
        # 进行关系抽取
        triplets = rte_from_text(answer)
        
        # 返回结果
        return {
            "answer": answer, 
            "triplets": triplets,
            "status": "success"
        }
        
    except Exception as e:
        print(f"❌ QA API错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream")
async def qa_stream(request: QARequest):
    """
    流式QA API endpoint - 支持对话历史上下文
    """
    async def generate():
        try:
            messages = []
            
            # 添加系统提示词
            if request.system_prompt:
                messages.append({'role': 'system', 'content': request.system_prompt})
                print(f"🔧 添加系统提示词: {request.system_prompt[:50]}...")
            else:
                # 默认系统提示词，强调专注当前问题
                default_prompt = "你是一个智能AI助手。请专注回答用户当前提出的问题，提供准确、简洁、有用的回答。不要重复之前已经回答过的内容，专注于当前的问题。"
                messages.append({'role': 'system', 'content': default_prompt})
                print("🔧 使用默认系统提示词")
            
            # 添加对话历史（重要：保持上下文）
            if request.conversation_history:
                for msg in request.conversation_history:
                    messages.append({'role': msg.role, 'content': msg.content})
                print("📚 添加历史对话")
            
            # 添加当前用户消息（重要：确保当前消息被包含）
            messages.append({'role': 'user', 'content': request.message})
            
            print(f"🚀 收到流式请求，总消息数: {len(messages)}")
            print(f"📝 当前用户消息: {request.message[:100]}...")
            
            # 打印完整对话上下文（调试用）
            print("📋 完整对话上下文:")
            for i, msg in enumerate(messages):
                role_emoji = "🤖" if msg['role'] == 'assistant' else "👤" if msg['role'] == 'user' else "⚙️"
                content_preview = msg['content'][:80] + "..." if len(msg['content']) > 80 else msg['content']
                print(f"  {i+1}. {role_emoji} {msg['role']}: {content_preview}")
            
            # 获取AI回答
            answer = get_completion_from_messages(messages, model="deepseek-chat", temperature=0.7)
            
            print(f"✅ 获得AI回答: {len(answer)} 字符")
            print(f"📄 回答预览: {answer[:100]}...")
            
            # 改进的流式输出 - 按合理的块输出
            chunks = split_text_for_streaming(answer)
            
            for i, chunk_text in enumerate(chunks):
                chunk = {
                    "content": chunk_text,
                    "type": "text"
                }
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.05)  # 适中的延迟
            
            # 在流式输出完成后进行关系抽取（不影响主流程）
            try:
                print("🔄 开始对AI回复进行关系抽取...")
                triplets = rte_from_text(answer)
                
                # 发送三元组数据
                if triplets:
                    triplets_chunk = {
                        "content": "",
                        "type": "triplets",
                        "triplets": triplets
                    }
                    yield f"data: {json.dumps(triplets_chunk, ensure_ascii=False)}\n\n"
                    print(f"📊 发送了 {len(triplets)} 个三元组用于动态图生成")
                else:
                    print("⚠️ 未能提取到有效的三元组")
            except Exception as rte_error:
                print(f"❌ 关系抽取失败，但不影响主流程: {rte_error}")
                # RTE失败不应该中断整个响应流
            
            # 发送完成信号
            yield f"data: [DONE]\n\n"
            print(f"🎉 流式输出完成，共发送 {len(chunks)} 个数据块")
            
        except Exception as e:
            print(f"❌ 流式API错误: {e}")
            import traceback
            traceback.print_exc()
            
            error_chunk = {
                "type": "error",
                "error": str(e),
                "content": "抱歉，AI服务暂时不可用，请稍后重试。"
            }
            yield f"data: {json.dumps(error_chunk, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(generate(), media_type="text/plain")

def split_text_for_streaming(text):
    """
    将文本分割成合适的流式输出块
    """
    if not text:
        return []
    
    chunks = []
    
    # 按行分割
    lines = text.split('\n')
    
    for line in lines:
        if not line.strip():
            chunks.append('\n')
            continue
            
        # 对于较长的行，按句子或短语分割
        if len(line) > 50:
            # 按句号、问号、感叹号分割
            sentences = re.split(r'([。！？.!?])', line)
            current_chunk = ""
            
            for i, part in enumerate(sentences):
                current_chunk += part
                
                # 如果是标点符号或积累了足够的字符，输出一个块
                if part in '。！？.!?' or len(current_chunk) >= 20:
                    if current_chunk.strip():
                        chunks.append(current_chunk)
                        current_chunk = ""
            
            # 处理剩余的内容
            if current_chunk.strip():
                chunks.append(current_chunk)
                
            chunks.append('\n')
        else:
            # 短行直接输出
            chunks.append(line + '\n')
    
    # 过滤空块并合并过短的块
    filtered_chunks = []
    for chunk in chunks:
        if chunk.strip() or chunk == '\n':
            filtered_chunks.append(chunk)
    
    return filtered_chunks 
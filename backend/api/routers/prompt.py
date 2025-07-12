# @user: maybemed
# @last_update: 2025-07-12 02:23:07 UTC
# @version: prompt_management_api

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.core.prompt_manager import PromptManager
from backend.utils.logger import logger

router = APIRouter()


class PromptUpdateRequest(BaseModel):
    prompt: str


class PromptResponse(BaseModel):
    system_prompt: str


class PromptUpdateResponse(BaseModel):
    msg: str
    system_prompt: str


@router.get("/", response_model=PromptResponse)
async def get_system_prompt():
    """获取当前系统提示词"""
    try:
        PromptManager.initialize()
        current_prompt = PromptManager.get_current_system_prompt()

        if current_prompt is None:
            raise HTTPException(status_code=500, detail="Failed to get current system prompt")

        return PromptResponse(system_prompt=current_prompt)

    except Exception as e:
        logger.error(f"获取系统提示词失败: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system prompt")


@router.post("/", response_model=PromptUpdateResponse)
async def update_system_prompt(request: PromptUpdateRequest):
    """更新系统提示词"""
    try:
        PromptManager.initialize()

        # 创建或更新名为 "current" 的系统提示词
        prompt_name = "current"

        # 先尝试更新，如果不存在则创建
        success = PromptManager.update_system_prompt(
            name=prompt_name,
            content=request.prompt,
            description="当前使用的系统提示词"
        )

        if not success:
            # 如果更新失败（可能是不存在），则创建新的
            success = PromptManager.create_system_prompt(
                name=prompt_name,
                content=request.prompt,
                description="当前使用的系统提示词"
            )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to update system prompt")

        # 设置为当前使用的提示词
        if not PromptManager.set_current_system_prompt(prompt_name):
            raise HTTPException(status_code=500, detail="Failed to set current system prompt")

        return PromptUpdateResponse(
            msg="系统级prompt已更新",
            system_prompt=request.prompt
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新系统提示词失败: {e}")
        raise HTTPException(status_code=500, detail="Failed to update system prompt")
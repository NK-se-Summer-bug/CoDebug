# main.py
import logging

logging.basicConfig(
    level=logging.DEBUG,  # 输出所有 DEBUG 及以上等级的日志
    format="%(asctime)s [%(levelname)s] %(message)s",
)
from fastapi import FastAPI
from backend.api.routers import prompt, qa, kg, llm, agent
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:8502",  # 假设 Streamlit 运行在 8502 端口
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法 (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # 允许所有 HTTP 头
)

# tags用于指定路由的标签，方便在文档中进行分类
app.include_router(qa.router, prefix="/api/qa", tags=["qa"])
app.include_router(kg.router, prefix="/api/kg", tags=["kg"])
app.include_router(prompt.router, prefix="/api/prompt", tags=["prompt"])
app.include_router(agent.router, prefix="/api/agent", tags=["agent"])
app.include_router(llm.router, tags=["LLM Core"]) # 添加这一行，不加prefix
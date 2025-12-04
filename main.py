# main.py  —— 临时最小可运行版（只加载工具6，保证你现在就能看到页面）
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

# 强制创建必需目录
os.makedirs("downloads", exist_ok=True)
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

app = FastAPI(title="Tools Hub 2025")
app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 只有工具6（已确认存在）
from tools.tool_06_video_downloader import router as tool6_router
app.include_router(tool6_router)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return """
    <h1>Tools Hub 2025 - 开发调试中</h1>
    <ul>
        <li><a href="/tool/6">工具6：微博/小红书无水印下载（已就绪）</a></li>
        <li>其他工具开发中...</li>
    </ul>
    """

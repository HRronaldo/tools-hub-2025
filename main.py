from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

# 创建必需目录
os.makedirs("downloads", exist_ok=True)
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

app = FastAPI(title="Tools Hub 2025")

# 静态文件服务
app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# === 注册所有工具路由 ===
from tools.tool_06_video_downloader import router as tool6_router
from tools.tool_04_md_to_wechat import router as tool4_router

app.include_router(tool6_router)
app.include_router(tool4_router)

# === 首页 ===
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return """
    <h1>Tools Hub 2025 - 程序员自用神器合集（免费无限制）</h1>
    <ol>
        <li><a href="/tool/4"><strong>工具4：Markdown → 微信公众号完美排版（重磅上线）</strong></a></li>
        <li><a href="/tool/6"><strong>工具6：小红书/微博无水印视频下载（已上线）</strong></a></li>
        <li>工具1：WSL Docker 一键加速（开发中）</li>
        <li>更多工具即将上线...</li>
    </ol>
    <p><small>全站免费 · 无广告 · 永久开源 · 欢迎分享</small></p>
    <p><a href="https://github.com/HRronaldo/tools-hub-2025">GitHub 开源地址</a></p>
    """

# 注意：这里故意留空！启动完全交给 run.bat
# if __name__ == "__main__":  ← 永远不写这句！

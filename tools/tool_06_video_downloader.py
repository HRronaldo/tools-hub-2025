# tools/tool_06_video_downloader.py
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import yt_dlp
import os

router = APIRouter()
templates = Jinja2Templates(directory="templates")
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@router.get("/tool/6", response_class=HTMLResponse)
async def tool6_page(request: Request):
    return templates.get_template("tool6.html").render({"request": request})

@router.post("/api/download")
async def download_video(url: str = Form(...)):
    ydl_opts = {
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(id)s.%(ext)s'),
        'format': 'bestvideo+bestaudio/best',   # 强制选最高清晰度
        'quiet': True,
        'no_warnings': False,
        'merge_output_format': 'mp4',
        # 下面这三行是关键：绕过小红书/微博最新反爬
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'Referer': 'https://www.xiaohongshu.com/',
            'Origin': 'https://www.xiaohongshu.com'
        },
        # 'cookiefile': 'cookies.txt',           # 可选：如果有登录态 cookies 更稳
        'retries': 10,
        'fragment_retries': 10,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            title = info.get('title', '未知视频')
        rel_path = os.path.relpath(filename, ".")
        rel_path_fixed = rel_path.replace('\\', '/')
        return JSONResponse({
            "success": True,
            "file": f"/{rel_path_fixed}",
            "title": title
        })
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)})

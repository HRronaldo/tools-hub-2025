# tools/tool_07_bilibili.py —— B站字幕终极修复版（万能查找 + 自动转 SRT + Cookies 支持）
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import yt_dlp
import os
import re
import json
import xml.etree.ElementTree as ET
from datetime import timedelta

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# 创建 cookies 文件夹结构
cookies_dir = os.path.join(os.getcwd(), 'cookies', 'bilibili')
os.makedirs(cookies_dir, exist_ok=True)

@router.get("/tool/7", response_class=HTMLResponse)
async def tool7_page(request: Request):
    return templates.get_template("tool7.html").render({"request": request})

def format_time(td):
    """格式化时间为 SRT 格式: HH:MM:SS,mmm"""
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((td.total_seconds() - total_seconds) * 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

def convert_bilibili_subtitle_to_srt(subtitle_path: str) -> str:
    """将B站字幕（xml/json3/ass）转换为标准 SRT"""
    srt_path = subtitle_path.rsplit('.', 1)[0] + '.srt'
    if os.path.exists(srt_path):
        return srt_path

    try:
        with open(subtitle_path, 'r', encoding='utf-8') as f:
            content = f.read()

        subtitles = []
        if subtitle_path.endswith(('.xml', '.ass')):  # 支持 xml 和 ass
            if subtitle_path.endswith('.xml'):
                root = ET.fromstring(content)
                for i, event in enumerate(root.findall('.//d')):
                    p_str = event.get('p', '0')
                    p = float(p_str.split(',')[0]) if ',' in p_str else float(p_str)  # 解析时间（秒）
                    text = event.text or ''
                    start = timedelta(seconds=p)
                    end = timedelta(seconds=p + 5)  # 估算
                    subtitles.append((i+1, start, end, text))
            elif subtitle_path.endswith('.ass'):
                # 简单处理 .ass，尝试解析时间
                lines = content.splitlines()
                for line in lines:
                    if line.startswith("Dialogue:"):
                        parts = line.split(',', 9)
                        if len(parts) > 9:
                            start_str = parts[1]  # 格式如 0:00:05.00
                            end_str = parts[2]
                            text = parts[9].replace('\\N', '\n').strip()
                            if text:
                                # 转换 ASS 时间到 timedelta（简化）
                                try:
                                    start_td = timedelta(seconds=float(start_str.replace(':', '').replace('.', '')) / 100)  # 粗略转换
                                    end_td = timedelta(seconds=float(end_str.replace(':', '').replace('.', '')) / 100)
                                except:
                                    start_td = timedelta(seconds=0)
                                    end_td = timedelta(seconds=0)
                                subtitles.append((len(subtitles)+1, start_td, end_td, text))
        elif subtitle_path.endswith('.json3'):
            data = json.loads(content)
            for i, seg in enumerate(data.get('body', [])):
                start = timedelta(seconds=seg.get('from', 0))
                end = timedelta(seconds=seg.get('to', 0))
                text = seg.get('content', '')
                subtitles.append((i+1, start, end, text))

        if subtitles:
            with open(srt_path, 'w', encoding='utf-8') as f:
                for idx, start, end, text in subtitles:
                    start_str = format_time(start) if isinstance(start, timedelta) else start
                    end_str = format_time(end) if isinstance(end, timedelta) else end
                    f.write(f"{idx}\n")
                    f.write(f"{start_str} --> {end_str}\n")
                    f.write(f"{text}\n\n")
            print(f"字幕转换成功: {srt_path}")
            return srt_path
        else:
            print(f"字幕文件无内容: {subtitle_path}")
    except Exception as e:
        print(f"字幕转换失败: {e} (文件: {subtitle_path})")
    return subtitle_path  # 转换失败返回原文件

@router.post("/api/bilibili")
async def bilibili_download(url: str = Form(...), cookies_file: str = Form(None)):
    if not url.strip():
        return JSONResponse({"success": False, "error": "请输入B站视频链接"})

    if "bilibili.com" not in url and "b23.tv" not in url:
        return JSONResponse({"success": False, "error": "请输入有效的B站链接"})

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'downloads/%(id)s/%(id)s.%(ext)s',  # 为每个视频创建子文件夹
        'subtitles_outtmpl': 'downloads/%(id)s/%(id)s.%(ext)s',  # 字幕也放在子文件夹
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['zh-CN', 'zh-TW', 'en', 'all'],  # 下载指定语言和所有
        'skip_download': False,
        'quiet': True,
        'no_warnings': True,
    }

    # 如果提供了 cookies 文件路径，添加认证
    if cookies_file:
        cookies_path = os.path.join(os.getcwd(), cookies_file)
        if os.path.exists(cookies_path):
            ydl_opts['cookiefile'] = cookies_path
            print(f"使用 cookies 文件: {cookies_path}")
        else:
            print(f"Cookies 文件不存在: {cookies_path}")
    else:
        print("未提供 cookies 文件，字幕可能需要登录")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info['id']
            title = info.get('title', 'B站视频')

            video_file_path = f"downloads/{video_id}/{video_id}.mp4"
            if not os.path.exists(video_file_path):
                for ext in ['.flv', '.m4s', '.webm', '.mkv']:
                    potential = f"downloads/{video_id}/{video_id}{ext}"
                    if os.path.exists(potential):
                        video_file_path = potential
                        break

            # 万能字幕查找：匹配视频ID开头的所有字幕文件，排除弹幕，转换并返回 SRT
            subtitles = []
            downloads_dir = "downloads"
            video_dir = os.path.join(downloads_dir, video_id)
            if os.path.exists(video_dir):
                print(f"下载目录内容: {os.listdir(video_dir)}")  # 调试：列出所有文件
                # 查找所有可能的字幕文件
                subtitle_files = []
                for file in os.listdir(video_dir):
                    if re.match(re.escape(video_id) + r'.*\.(srt|vtt|ass|xml|json3|json)$', file, re.IGNORECASE) and 'danmaku' not in file:
                        subtitle_files.append(file)
                
                for file in subtitle_files:
                    full_path = os.path.join(video_dir, file)
                    srt_path = convert_bilibili_subtitle_to_srt(full_path)
                    if os.path.exists(srt_path):
                        # 推断语言
                        lang = "未知"
                        if 'zh-CN' in file or 'zh-Hans' in file:
                            lang = "中文（简体）"
                        elif 'zh-TW' in file or 'zh-Hant' in file:
                            lang = "中文（繁体）"
                        elif 'en' in file:
                            lang = "英语"
                        elif 'ai-zh' in file:
                            lang = "AI 中文"
                        elif 'ai-en' in file:
                            lang = "AI 英语"
                        subtitles.append({"lang": lang, "url": f"/downloads/{video_id}/{os.path.basename(srt_path)}"})
            subtitle_status = f"找到 {len(subtitles)} 个字幕文件" if subtitles else "无字幕"

            if not os.path.exists(video_file_path):
                return JSONResponse({"success": False, "error": "下载失败：未找到视频文件"})

            return JSONResponse({
                "success": True,
                "title": title,
                "video": f"/downloads/{video_id}/{os.path.basename(video_file_path)}",
                "subtitles": subtitles,
                "subtitle_status": subtitle_status
            })

    except Exception as e:
        error_msg = str(e)
        if "Subtitles are only available when logged in" in error_msg:
            return JSONResponse({"success": False, "error": "字幕需要登录 B 站账号，请提供 cookies 文件"})
        return JSONResponse({"success": False, "error": f"下载失败：{error_msg}"})

# tools/tool_04_md_to_wechat.py
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import markdown
from bs4 import BeautifulSoup
import re

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def md_to_html(md_text: str) -> str:
    extensions = [
        'extra',           # 支持表格
        'tables',          # 表格增强
        'fenced_code',     # ``` 代码块
        'codehilite',      # 代码高亮
        'toc',             # 目录
        'nl2br',           # 换行转<br>
        'sane_lists',      # 更好列表
        'admonition'       # 警告框
    ]
    html = markdown.markdown(md_text or "", extensions=extensions, output_format='html5')
    return html

def wrap_wechat_html(body_html: str) -> str:
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>微信公众号预览</title>
    <link rel="stylesheet" href="/static/wechat_style.css">
</head>
<body>
<div class="wechat-article">
    {body_html}
</div>
</body>
</html>"""

@router.get("/tool/4", response_class=HTMLResponse)
async def tool4_page(request: Request):
    return templates.get_template("tool4.html").render({"request": request})

@router.post("/api/md2wechat")
async def md_to_wechat(md_text: str = Form(...)):
    try:
        body = md_to_html(md_text)
        
        # 关键修复：把 <pre><code> 替换成微信能识别的结构
        soup = BeautifulSoup(body, 'html.parser')
        
        for pre in soup.find_all('pre'):
            code = pre.find('code')
            if code:
                lang_class = code.get('class', [''])[0] if code.get('class') else ''
                lang = lang_class.replace('language-', '') if lang_class else ''
                code_text = code.get_text()
                # 微信专用代码块样式
                new_block = soup.new_tag("section")
                new_block.append(BeautifulSoup(f'''
                    <section style="background:#f6f8fa;padding:15px;border-radius:8px;margin:20px 0;overflow-x:auto;">
                        <code style="font-family:Consolas;font-size:14px;color:#333;">{code_text}</code>
                    </section>
                ''', 'html.parser'))
                pre.replace_with(new_block)
        
        full_html = wrap_wechat_html(str(soup))
        return JSONResponse({"success": True, "html": full_html})
    
    except Exception as e:
        return JSONResponse({"success": False, "error": f"转换失败：{str(e)}"})

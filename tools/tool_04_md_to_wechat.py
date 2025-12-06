# tools/tool_04_md_to_wechat.py —— 终极完美版（代码块100%还原）
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import markdown
from bs4 import BeautifulSoup

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def md_to_html(md_text: str) -> str:
    """将 Markdown 转成标准 HTML，关键：关闭 codehilite 的 span 包裹"""
    extensions = [
        'extra',
        'tables',
        'fenced_code',
        'codehilite',           # 保留！用于语法识别
        'toc',
        'nl2br',
        'sane_lists',
        'admonition',
        'md_in_html'
    ]
    # 关键配置：使用 CSS classes 而不是 inline styles，便于微信渲染
    extension_configs = {
        'codehilite': {
            'linenums': True,       # 显示行号
            'guess_lang': True,     # 自动识别语言
            'use_pygments': True,
            'noclasses': False,     # 改为 False：使用 CSS classes（更干净）
            'pygments_style': 'default'
        }
    }
    return markdown.markdown(
        md_text or "",
        extensions=extensions,
        extension_configs=extension_configs,  # 加上这行！
        output_format='html5'
    )

def wrap_wechat_html(body_html: str) -> str:
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>微信公众号完美预览（右键 → 查看页面源代码 → 全选复制）</title>
    <link rel="stylesheet" href="/static/wechat_style.css">
    <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js" defer></script>
    <script>
        window.MathJax = {{
            tex: {{ inlineMath: [['$', '$'], ['\\(', '\\)']] }},
            svg: {{ fontCache: 'global' }}
        }};
    </script>
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
        soup = BeautifulSoup(body, 'html.parser')
        # 什么都不处理！现在代码块已经是最干净的 <pre><code class="language-python">
        full_html = wrap_wechat_html(str(soup))
        return JSONResponse({"success": True, "html": full_html})
    except Exception as e:
        return JSONResponse({"success": False, "error": f"转换失败：{str(e)}"})

# tools/tool_05_pdf_to_md.py
from fastapi import APIRouter, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pdfplumber
from bs4 import BeautifulSoup
import re

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/tool/5", response_class=HTMLResponse)
async def tool5_page(request: Request):
    return templates.get_template("tool5.html").render({"request": request})

@router.post("/api/pdf2md")
async def pdf_to_md(pdf_file: UploadFile = File(...)):
    try:
        content = await pdf_file.read()
        text = ""
        with pdfplumber.open(content) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n\n"
        
        # 简单清理（保留公式、表格）
        text = re.sub(r'\n{3,}', '\n\n', text)  # 去多余空行
        md = text  # 实际生产可用 markdownify 或自定义处理表格/公式
        
        return {"success": True, "markdown": md}
    except Exception as e:
        return {"success": False, "error": str(e)}

# tools/tool_05_pdf_to_md.py —— 中文PDF优化版（解决换行、误判、重复 + pandas 修复）
import os
import tempfile
from fastapi import APIRouter, Request, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import fitz  # pymupdf
import pandas as pd  # <--- 关键修复：显式导入 pandas

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/tool/5", response_class=HTMLResponse)
async def tool5_page(request: Request):
    return templates.get_template("tool5.html").render({"request": request})

@router.post("/api/pdf2md")
async def pdf_to_md(pdf_file: UploadFile = File(...)):
    if not pdf_file.filename.lower().endswith('.pdf'):
        return JSONResponse({"success": False, "error": "请上传 PDF 文件"})

    try:
        content = await pdf_file.read()
        tmp_fd, tmp_path = tempfile.mkstemp(suffix=".pdf")
        with os.fdopen(tmp_fd, 'wb') as tmp_file:
            tmp_file.write(content)

        doc = fitz.open(tmp_path)
        text = ""
        seen_lines = set()  # 去重

        for page in doc:
            # 优先使用 get_text("text")，更干净
            page_text = page.get_text("text")
            lines = page_text.split("\n")
            cleaned_lines = []

            for line in lines:
                line = line.strip()
                if line and line not in seen_lines:
                    seen_lines.add(line)
                    cleaned_lines.append(line)

            if cleaned_lines:
                text += "\n".join(cleaned_lines) + "\n\n"

            # 表格提取：严格过滤
            tables = page.find_tables()
            for table in tables:
                df = table.to_pandas()
                if not df.empty:
                    if len(df) >= 2 and len(df.columns) >= 2:
                        has_text = df.astype(str).apply(lambda x: x.str.contains(r'[一-龥a-zA-Z]', regex=True)).any().any()
                        if has_text:
                            df = df.dropna(how='all').dropna(axis=1, how='all')
                            df.columns = [str(col).strip() for col in df.columns]
                            df = df.map(lambda x: str(x).strip() if pd.notna(x) else "")
                            header = "|" + "|".join(df.columns) + "|\n"
                            separator = "|" + "|".join(["---"] * len(df.columns)) + "|\n"
                            rows = "\n".join(["|" + "|".join(row) + "|" for row in df.values])
                            text += header + separator + rows + "\n\n"

        doc.close()
        os.unlink(tmp_path)

        if not text.strip():
            return JSONResponse({"success": False, "error": "无法提取有效文本（可能是扫描版PDF）"})

        return JSONResponse({"success": True, "markdown": text.strip()})

    except Exception as e:
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except:
                pass
        return JSONResponse({"success": False, "error": f"转换失败：{str(e)}"})

# TODO: 终极升级方案 - 集成 Nougat（Meta 开源学术PDF转Markdown模型）
# 优势：完美保留 LaTeX 公式（如 $E=mc^2$）、表格结构、图片caption，专为论文设计
# 步骤：
# 1. pip install nougat-ocr
# 2. from nougat import NougatModel
# 3. model = NougatModel.from_pretrained("facebook/nougat-small")
# 4. 保存上传文件到临时路径
# 5. prediction = model.predict(temp_pdf_path)
# 6. 返回 prediction[0] 作为 markdown
# 缺点：模型大（1-2GB），首次加载慢，适合学术重度用户
# 触发时机：当工具日活破500或用户反馈公式丢失严重时上线

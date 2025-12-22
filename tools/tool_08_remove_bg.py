# tools/tool_08_remove_bg.py —— 工具8：图片背景一键去除（Remove.bg 免费替代）
from fastapi import APIRouter, Request, File, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from rembg import remove
from PIL import Image
import io
import os

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/tool/8", response_class=HTMLResponse)
async def tool8_page(request: Request):
    return templates.get_template("tool8.html").render({"request": request})

# API 路由
@router.post("/api/remove_bg")
async def remove_bg(image: UploadFile = File(...)):
    allowed_extensions = ('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff')
    if not image.filename.lower().endswith(allowed_extensions):
        return {"success": False, "error": "不支持的文件格式，请上传 PNG/JPG/WEBP/BMP/TIFF"}

    try:
        input_data = await image.read()
        output_data = remove(input_data)

        name = os.path.splitext(image.filename)[0]
        download_filename = f"{name}_transparent.png"

        return StreamingResponse(
            io.BytesIO(output_data),
            media_type="image/png",
            headers={"Content-Disposition": f"attachment; filename={download_filename}"}
        )
    except Exception as e:
        return {"success": False, "error": f"处理失败：{str(e)}"}

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
import generators, analyzer, render

app = FastAPI()

@app.get("/")
def index():
    return FileResponse("app/static/index.html")

@app.post("/api/generate")
async def generate(
    image: UploadFile = File(...), 
    title: str = Form("計算演習プリント"),
    juku_name: str = Form("進学塾テスト教室")  # 塾名を受け取る
):
    data = await image.read()
    try:
        sections = analyzer.analyze(data, image.content_type or "image/jpeg")
    finally:
        del data
    if not sections:
        raise HTTPException(422, "対応する計算問題を検出できませんでした")
    
    built = generators.build(sections)
    # render.to_htmlに塾名も渡す
    html_content = render.to_html(title, built, juku_name)
    return HTMLResponse(content=html_content)

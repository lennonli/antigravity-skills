import os
import shutil
import uuid
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from translator import DocumentTranslator

app = FastAPI(title="Document Translator Web UI")

# Setup directories
BASE_DIR = Path(__name__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "temp_uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Serve static files
webui_dir = BASE_DIR / "assets" / "webui"
webui_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(webui_dir)), name="static")

@app.get("/")
async def read_index():
    index_path = webui_dir / "index.html"
    if not index_path.exists():
        return JSONResponse({"error": "Web UI files not found. Please ensure index.html exists in assets/webui/"})
    return FileResponse(index_path)

@app.post("/translate")
async def translate_document(
    file: UploadFile = File(...),
    api_type: str = Form("gemini"),
    target_lang: str = Form("Chinese")
):
    # 1. Save uploaded file
    file_id = str(uuid.uuid4())
    input_path = UPLOAD_DIR / f"{file_id}_{file.filename}"
    
    with input_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    output_path = input_path.with_suffix(".translated.docx")
    
    try:
        # 2. Initialize translator
        # It will use environment variables for keys
        translator = DocumentTranslator(api_type=api_type)
        
        # 3. Process
        translator.process(str(input_path), str(output_path), target_lang, skip_open=True)
        
        return {
            "success": True,
            "filename": output_path.name,
            "download_url": f"/download/{output_path.name}"
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file_path, filename=filename, media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

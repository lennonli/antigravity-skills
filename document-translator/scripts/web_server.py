import os
import shutil
import uuid
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from translator import DocumentTranslator
from pydantic import BaseModel
import datetime

app = FastAPI(title="Document Translator Web UI")

# Global state for simple progress tracking
# Format: { "task_id": { "status": "processing|completed|error", "progress": 0.0, "result_file": "...", "error": "...", "filename": "...", "timestamp": "..." } }
translation_tasks = {}

# Setup directories
BASE_DIR = Path(__file__).resolve().parent.parent
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

def run_translation_task(task_id: str, input_path: Path, output_path: Path, api_type: str, target_lang: str):
    def progress_callback(current, total):
        pct = (current / total) * 100 if total > 0 else 0
        translation_tasks[task_id]["progress"] = round(pct, 1)

    try:
        if api_type == "zhipu":
            translator = DocumentTranslator(api_type=api_type, api_key="774e1727547445519776afe760130fd5.SjqEECRFt3unPPsR")
        else:
            translator = DocumentTranslator(api_type=api_type)
        
        translator.process(str(input_path), str(output_path), target_lang, skip_open=True, progress_callback=progress_callback)
        
        translation_tasks[task_id]["status"] = "completed"
        translation_tasks[task_id]["progress"] = 100.0
        translation_tasks[task_id]["result_file"] = output_path.name
        
    except Exception as e:
        translation_tasks[task_id]["status"] = "error"
        translation_tasks[task_id]["error"] = str(e)


@app.post("/translate")
async def translate_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    api_type: str = Form("gemini"),
    target_lang: str = Form("Chinese"),
    access_code: str = Form(""),
    api_key: str = Form(None)
):
    # Security check
    if ACCESS_CODE and access_code != ACCESS_CODE:
        return JSONResponse(status_code=401, content={"success": False, "error": "Invalid Access Code. Please enter the correct code to use this service."})

    # 1. Save uploaded file
    task_id = str(uuid.uuid4())
    input_path = UPLOAD_DIR / f"{task_id}_{file.filename}"
    
    with input_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    output_path = input_path.with_suffix(".translated.docx")
    
    # 2. Register task state
    translation_tasks[task_id] = {
        "status": "processing",
        "progress": 0.0,
        "filename": file.filename,
        "result_file": None,
        "error": None,
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    # 3. Queue background task
    background_tasks.add_task(run_translation_task, task_id, input_path, output_path, api_type, target_lang, api_key)
    
    return {
        "success": True,
        "task_id": task_id
    }

@app.get("/progress/{task_id}")
async def get_progress(task_id: str):
    if task_id not in translation_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_info = translation_tasks[task_id]
    response = {
        "status": task_info["status"],
        "progress": task_info["progress"]
    }
    
    if task_info["status"] == "completed":
        response["download_url"] = f"/download/{task_info['result_file']}"
        response["filename"] = task_info["result_file"]
    elif task_info["status"] == "error":
        response["error"] = task_info["error"]
        
    return response

@app.get("/history")
async def get_history():
    history = []
    # Sort files by modification time descending
    files = sorted(UPLOAD_DIR.glob("*.translated.docx"), key=os.path.getmtime, reverse=True)
    
    for f in files:
        history.append({
            "filename": f.name.split("_", 1)[-1] if "_" in f.name else f.name,
            "download_url": f"/download/{f.name}",
            "timestamp": datetime.datetime.fromtimestamp(f.stat().st_mtime).isoformat()
        })
    return {"history": history[:10]} # Return top 10 recent

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file_path, filename=filename, media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

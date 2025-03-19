from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
from GeminiDocumentAnalyzer import GeminiDocumentAnalyzer

app = FastAPI()

# CORSの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GeminiDocumentAnalyzerのインスタンスを作成
analyzer = GeminiDocumentAnalyzer()

@app.post("/api/analyze")
async def analyze_documents(files: List[UploadFile] = File(...)):
    # 一時ファイルとして保存
    temp_paths = []
    for file in files:
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        temp_paths.append(temp_path)

    try:
        # 文書を分析
        result = analyzer.process_documents(temp_paths)
        return {"result": result}
    finally:
        # 一時ファイルを削除
        for path in temp_paths:
            if os.path.exists(path):
                os.remove(path)

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import os
import uuid
import asyncio
import sqlite3

from crewai import Crew, Process
from agents import financial_analyst
from task import analyze_financial_document as financial_task
from tools import read_financial_document
from database import init_db, save_log

app = FastAPI(title="Financial Document Q&A System")

# ------------------------------
# Initialize Database on Startup
# ------------------------------
@app.on_event("startup")
async def startup_event():
    init_db()

# In-memory storage (assignment-level persistence)
stored_document_content = None
stored_file_name = None


# ------------------------------
# Helper function to run Crew
# ------------------------------
def run_crew(query: str, document_content: str):
    crew = Crew(
        agents=[financial_analyst],
        tasks=[financial_task],
        process=Process.sequential,
    )

    result = crew.kickoff(
        {
            "query": query,
            "document_content": document_content,
        }
    )

    return result


# ------------------------------
# Health Check
# ------------------------------
@app.get("/")
async def root():
    return {"message": "Financial Document Q&A API is running"}


# ------------------------------
# Upload PDF
# ------------------------------
@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    global stored_document_content, stored_file_name

    file_id = str(uuid.uuid4())
    file_path = f"data/{file_id}.pdf"

    try:
        os.makedirs("data", exist_ok=True)

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        stored_document_content = read_financial_document(file_path)
        stored_file_name = file.filename

        if not stored_document_content:
            raise ValueError("Document content could not be extracted.")

        return {
            "status": "success",
            "message": "Document uploaded and stored successfully.",
            "file_name": file.filename,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


# ------------------------------
# Query Uploaded PDF
# ------------------------------
@app.post("/query")
async def query_document(query: str = Form(...)):
    global stored_document_content, stored_file_name

    if not stored_document_content:
        raise HTTPException(
            status_code=400,
            detail="No document uploaded. Please upload a PDF first.",
        )

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty.",
        )

    try:
        loop = asyncio.get_event_loop()

        response = await loop.run_in_executor(
            None,
            lambda: run_crew(
                query=query.strip(),
                document_content=stored_document_content
            ),
        )

        if not response:
            response = "No response generated from the document."

        response_text = str(response)

        # Save to DB
        save_log(
            file_name=stored_file_name,
            query=query,
            answer=response_text
        )

        return {
            "status": "success",
            "query": query,
            "answer": response_text,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ------------------------------
# 🔥 NEW: Get Database History
# ------------------------------
@app.get("/logs")
async def get_logs():

    conn = sqlite3.connect("analysis.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM analysis_logs ORDER BY id DESC")
    rows = cursor.fetchall()

    conn.close()

    logs = []
    for row in rows:
        logs.append({
            "id": row[0],
            "file_name": row[1],
            "query": row[2],
            "answer": row[3],
            "created_at": row[4],
        })

    return {"logs": logs}


# ------------------------------
# Run Server
# ------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
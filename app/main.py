
from pathlib import Path
import asyncio
from app.database import (
    init_db,
    create_document,
    update_document,
    get_all_documents,
    get_document_by_id,
    delete_document,
)

from fastapi import FastAPI, UploadFile, File, HTTPException

from app.services.document_pipeline import process_document


app = FastAPI(
    title="Document Intelligence System",
    description="Backend API for the Document Intelligence System",
    version="1.0.0",
)
init_db()


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "Document Intelligence API is running"
    }


@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):

    # Allowed document extensions
    allowed_extensions = {
        ".pdf",
        ".docx",
        ".txt",
        ".xlsx",
        ".xls",
        ".csv",
        ".pptx",
        ".png",
        ".jpg",
        ".jpeg",
    }

    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_extension}"
        )

    # Save uploaded file
    input_directory = Path("data/input")
    input_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    file_path = input_directory / file.filename

    file_contents = await file.read()

    file_path.write_bytes(file_contents)
    document_id = create_document(
    file.filename,
    file_path,
    status="processing"
)

    # Run existing document pipeline
    try:

        result = await asyncio.to_thread(
            process_document,
            file_path
        )

        update_document(
            document_id=document_id,
            status="completed",
            validation_status=result["validation"]["status"],
            summary_validation_status=result["summary_validation"]["status"],
            summary_path=result["summary_path"],
            paraphrase_path=result["paraphrase_path"],
            audio_path=result["audio_path"],
        )

    except Exception as error:

        update_document(
            document_id=document_id,
            status="failed"
        )

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    return {
        "document_id": document_id,
        "message": "Document processed successfully",
        "file_name": file.filename,
        "validation": result["validation"],
        "summary_validation": result["summary_validation"],
        "summary": result["summary"],
        "paraphrase": result["paraphrase"],
        "audio_path": result["audio_path"],
        "summary_path": result["summary_path"],
        "paraphrase_path": result["paraphrase_path"],
    }
from app.database import get_all_documents


@app.get("/documents")
def get_documents():
    return get_all_documents()

@app.get("/documents/{document_id}")
def get_document(document_id: int):

    document = get_document_by_id(document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return document

@app.delete("/documents/{document_id}")
def delete_document_endpoint(document_id: int):

    deleted = delete_document(document_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return {
        "message": "Document deleted successfully",
        "document_id": document_id
    }

@app.put("/documents/{document_id}/process")
async def reprocess_document(document_id: int):

    document = get_document_by_id(document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    file_path = Path(document["file_path"])

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Document file no longer exists"
        )

    update_document(
        document_id=document_id,
        status="processing"
    )

    try:
        result = await asyncio.to_thread(
            process_document,
            file_path
        )

        update_document(
            document_id=document_id,
            status="completed",
            validation_status=result["validation"]["status"],
            summary_validation_status=result["summary_validation"]["status"],
            summary_path=result["summary_path"],
            paraphrase_path=result["paraphrase_path"],
            audio_path=result["audio_path"],
        )

        return {
            "message": "Document reprocessed successfully",
            "document_id": document_id,
            "file_name": document["file_name"],
            "validation": result["validation"],
            "summary_validation": result["summary_validation"],
            "summary": result["summary"],
            "paraphrase": result["paraphrase"],
        }

    except Exception as error:

        update_document(
            document_id=document_id,
            status="failed"
        )

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )
from app.api.auth import router as auth_router
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

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse, PlainTextResponse
from app.services.document_pipeline import process_document
from app.api.auth import get_current_user
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.services.google_drive_service import (
    get_drive_service,
    list_supported_files,
    list_all_drive_files_for_ui,
    get_or_create_output_folder,
    get_or_create_subfolder,
    process_drive_file,
    upload_file_to_drive,
    delete_existing_file,
)

app = FastAPI(
    title="Document Intelligence System",
    description="Backend API for the Document Intelligence System",
    version="1.0.0",
)
app.mount(
    "/static",
    StaticFiles(directory="frontend"),
    name="static",
)
@app.get("/", include_in_schema=False)
def home():
    return FileResponse("frontend/index.html")
app.include_router(auth_router)


init_db()


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "Document Intelligence API is running"
    }


@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
):

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
            summary_audio_path=result["summary_audio_path"],
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
def get_documents(current_user=Depends(get_current_user)):
    return get_all_documents()

@app.get("/documents/{document_id}")
def get_document(
    document_id: int,
    current_user=Depends(get_current_user),
):

    document = get_document_by_id(document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return document

@app.delete("/documents/{document_id}")
def delete_document_endpoint(
    document_id: int,
    current_user=Depends(get_current_user),
):
    document = get_document_by_id(document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    # Get all other documents so we don't delete files
    # that are still being used by another database record.
    all_documents = get_all_documents()

    other_documents = [
        item
        for item in all_documents
        if item["id"] != document_id
    ]

    path_fields = [
        "file_path",
        "summary_path",
        "summary_audio_path",
        "paraphrase_path",
        "audio_path",
    ]

    # Collect all paths still referenced by other documents.
    referenced_paths = set()

    for other_document in other_documents:
        for field in path_fields:
            path_value = other_document.get(field)

            if path_value:
                referenced_paths.add(
                    str(Path(path_value))
                )

    # Delete database record first.
    deleted = delete_document(document_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    deleted_files = []
    cleanup_warnings = []

    # Remove files that are no longer referenced.
    for field in path_fields:

        path_value = document.get(field)

        if not path_value:
            continue

        file_path = Path(path_value)

        if str(file_path) in referenced_paths:
            continue

        if not file_path.exists():
            continue

        try:
            file_path.unlink()
            deleted_files.append(str(file_path))

        except Exception as error:
            cleanup_warnings.append(
                f"Could not delete {file_path}: {error}"
            )

    response = {
        "message": "Document deleted successfully",
        "document_id": document_id,
        "deleted_files": deleted_files,
    }

    if cleanup_warnings:
        response["cleanup_warnings"] = cleanup_warnings

    return response

@app.put("/documents/{document_id}/process")
async def reprocess_document(
    document_id: int,
    current_user=Depends(get_current_user),
):

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
            summary_audio_path=result["summary_audio_path"],
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

@app.get("/documents/{document_id}/summary")
def get_document_summary(
    document_id: int,
    current_user=Depends(get_current_user),
):
    document = get_document_by_id(document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    summary_path = Path(document["summary_path"])

    if not summary_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Summary file not found",
        )

    return PlainTextResponse(
        summary_path.read_text(encoding="utf-8")
    )


@app.get("/documents/{document_id}/paraphrase")
def get_document_paraphrase(
    document_id: int,
    current_user=Depends(get_current_user),
):
    document = get_document_by_id(document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    paraphrase_path = Path(document["paraphrase_path"])

    if not paraphrase_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Paraphrase file not found",
        )

    return PlainTextResponse(
        paraphrase_path.read_text(encoding="utf-8")
    )


@app.get("/documents/{document_id}/audio")
def get_document_audio(
    document_id: int,
    current_user=Depends(get_current_user),
):
    document = get_document_by_id(document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    audio_path = Path(document["audio_path"])

    if not audio_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Audio file not found",
        )

    return FileResponse(
        audio_path,
        media_type="audio/mpeg",
        filename=audio_path.name,
    )
@app.get("/documents/{document_id}/summary-audio")
def get_document_summary_audio(
    document_id: int,
    current_user=Depends(get_current_user),
):
    document = get_document_by_id(document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    summary_audio_path = document.get("summary_audio_path")

    if not summary_audio_path:
        raise HTTPException(
            status_code=404,
            detail="Summary audio has not been generated for this document",
        )

    audio_path = Path(summary_audio_path)

    if not audio_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Summary audio file not found",
        )

    return FileResponse(
        audio_path,
        media_type="audio/mpeg",
        filename=audio_path.name,
    )

@app.get("/drive/files")
def get_drive_files(
    current_user=Depends(get_current_user),
):
    try:
        service = get_drive_service()

        output_folder_id = get_or_create_output_folder(service)

        files = list_all_drive_files_for_ui(
            service,
            exclude_folder_id=output_folder_id,
        )

        return {
            "files": files
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to access Google Drive: {error}",
        )


@app.post("/drive/process")
async def process_drive_document(
    file_id: str,
    file_name: str,
    mime_type: str,
    current_user=Depends(get_current_user),
):
    try:
        print(f"\nProcessing Google Drive file: {file_name}")

        # Connect to Google Drive
        service = get_drive_service()

        # Get the main output folder
        output_folder_id = get_or_create_output_folder(service)

        # Create a subfolder for this document
        document_folder_id = get_or_create_subfolder(
            service,
            output_folder_id,
            Path(file_name).stem,
        )

        # Download/export the selected Drive file
        local_file = process_drive_file(
            service,
            file_id,
            file_name,
            mime_type,
            destination_directory="data/input",
        )

        # Create database record
        document_id = create_document(
            file_name,
            local_file,
            status="processing",
        )

        try:
            # Run the complete document pipeline
            result = await asyncio.to_thread(
                process_document,
                local_file,
            )

            # Update database
            update_document(
                document_id=document_id,
                status="completed",
                validation_status=result["validation"]["status"],
                summary_validation_status=result["summary_validation"]["status"],
                summary_path=result["summary_path"],
                summary_audio_path=result["summary_audio_path"],
                paraphrase_path=result["paraphrase_path"],
                audio_path=result["audio_path"],
            )

            # Upload generated outputs to Google Drive
            output_files = [
                result["summary_path"],
                result["paraphrase_path"],
                result["audio_path"],
                result["summary_audio_path"],
            ]

            uploaded_files = []

            for output_file in output_files:

                output_file_name = Path(output_file).name

                delete_existing_file(
                    service,
                    document_folder_id,
                    output_file_name,
                )

                uploaded = upload_file_to_drive(
                    service,
                    output_file,
                    document_folder_id,
                )

                uploaded_files.append(uploaded)

            return {
                "message": "Google Drive document processed successfully",
                "document_id": document_id,
                "file_name": file_name,
                "validation": result["validation"],
                "summary_validation": result["summary_validation"],
                "summary": result["summary"],
                "paraphrase": result["paraphrase"],
                "uploaded_files": uploaded_files,
            }

        except Exception as error:

            update_document(
                document_id=document_id,
                status="failed",
            )

            raise error

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Google Drive processing failed: {error}",
        )
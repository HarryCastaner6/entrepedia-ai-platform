"""
Simplified document routes for demo purposes.
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
import shutil
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status
from pydantic import BaseModel

from backend.processors.simple_processors import (
    SimplePDFProcessor,
    SimpleDOCXProcessor,
    SimpleImageProcessor,
    SimpleAudioProcessor
)
from backend.utils.config import settings
from backend.utils.logger import app_logger


router = APIRouter()

# Initialize processors
pdf_processor = SimplePDFProcessor()
docx_processor = SimpleDOCXProcessor()
image_processor = SimpleImageProcessor()
audio_processor = SimpleAudioProcessor()

# Ensure upload directory exists
UPLOAD_DIR = Path(settings.output_dir) / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class ProcessDocumentResponse(BaseModel):
    success: bool
    filename: str
    file_type: str
    processing_result: Dict[str, Any]
    embeddings_created: bool = False
    error: Optional[str] = None


@router.post("/upload", response_model=ProcessDocumentResponse)
async def upload_and_process_document(
    file: UploadFile = File(...),
    create_embeddings: bool = Form(True)
) -> ProcessDocumentResponse:
    """Upload and process a document (simplified version)."""
    try:
        app_logger.info(f"Processing uploaded file: {file.filename}")

        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")

        file_path = UPLOAD_DIR / file.filename
        file_extension = file_path.suffix.lower()

        # Supported file types
        supported_types = {
            '.pdf': pdf_processor,
            '.docx': docx_processor,
            '.doc': docx_processor,
            '.jpg': image_processor,
            '.jpeg': image_processor,
            '.png': image_processor,
            '.gif': image_processor,
            '.mp3': audio_processor,
            '.wav': audio_processor,
            '.m4a': audio_processor
        }

        if file_extension not in supported_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_extension}. Supported: {list(supported_types.keys())}"
            )

        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process document
        processor = supported_types[file_extension]
        processing_result = processor.process(file_path)

        # Note: Embeddings creation is disabled in demo version
        embeddings_created = False

        return ProcessDocumentResponse(
            success=processing_result.get('success', False),
            filename=file.filename,
            file_type=file_extension,
            processing_result=processing_result,
            embeddings_created=embeddings_created,
            error=processing_result.get('error')
        )

    except Exception as e:
        app_logger.error(f"Document upload/processing failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Processing failed: {str(e)}"
        )


@router.post("/scrape-entrepedia")
async def scrape_entrepedia_courses() -> Dict[str, Any]:
    """Simulate Entrepedia scraping (demo version)."""
    app_logger.info("Demo: Simulating Entrepedia scraping")

    return {
        "success": True,
        "message": "Demo mode: Entrepedia scraping simulated",
        "files_scraped": 0,
        "files_processed": 0,
        "embeddings_created": 0,
        "note": "Configure real Entrepedia credentials in .env to enable actual scraping"
    }


@router.get("/processed")
async def list_processed_documents() -> Dict[str, Any]:
    """List all processed documents."""
    try:
        upload_files = []

        if UPLOAD_DIR.exists():
            for file_path in UPLOAD_DIR.iterdir():
                if file_path.is_file():
                    upload_files.append({
                        "filename": file_path.name,
                        "size": file_path.stat().st_size,
                        "modified": file_path.stat().st_mtime,
                        "source": "upload"
                    })

        return {
            "success": True,
            "upload_files": upload_files,
            "scraped_files": [],
            "total_files": len(upload_files)
        }

    except Exception as e:
        app_logger.error(f"Failed to list processed documents: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list documents: {str(e)}"
        )


@router.get("/stats")
async def get_document_stats() -> Dict[str, Any]:
    """Get statistics about processed documents."""
    try:
        file_types = {}
        total_size = 0
        total_files = 0

        if UPLOAD_DIR.exists():
            for file_path in UPLOAD_DIR.iterdir():
                if file_path.is_file():
                    ext = file_path.suffix.lower()
                    file_types[ext] = file_types.get(ext, 0) + 1
                    total_size += file_path.stat().st_size
                    total_files += 1

        return {
            "success": True,
            "total_files": total_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_types": file_types
        }

    except Exception as e:
        app_logger.error(f"Failed to get document stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Stats retrieval failed: {str(e)}"
        )
"""
Document routes for file upload, processing, and management.
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
import shutil
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status
from pydantic import BaseModel

from backend.processors.pdf_processor import PDFProcessor
from backend.processors.docx_processor import DOCXProcessor
from backend.processors.image_processor import ImageProcessor
from backend.processors.audio_processor import AudioProcessor
from backend.processors.text_processor import TextProcessor
from backend.embeddings.embedding_generator import EmbeddingGenerator
from backend.embeddings.vector_store import VectorStore, global_vector_store
from backend.scraper.entrepedia_scraper import EntrepediaScraper
from backend.utils.config import settings
from backend.utils.logger import app_logger
from backend.utils.storage import storage_manager


router = APIRouter()

# Initialize processors and services
pdf_processor = PDFProcessor()
docx_processor = DOCXProcessor()
image_processor = ImageProcessor()
audio_processor = AudioProcessor()
text_processor = TextProcessor()
embedding_generator = EmbeddingGenerator()
vector_store = global_vector_store
scraper = EntrepediaScraper()

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


class ScrapingStatus(BaseModel):
    status: str
    files_found: int
    files_processed: int
    errors: List[str] = []


@router.post("/upload", response_model=ProcessDocumentResponse)
async def upload_and_process_document(
    file: UploadFile = File(...),
    create_embeddings: bool = Form(True),
    chunk_size: int = Form(512)
) -> ProcessDocumentResponse:
    """
    Upload and process a document with optional embedding generation.
    """
    try:
        app_logger.info(f"Processing uploaded file: {file.filename}")

        # Validate file type
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")

        file_path = UPLOAD_DIR / file.filename
        file_extension = file_path.suffix.lower()

        # Supported file types
        supported_types = {
            '.pdf': pdf_processor,
            '.docx': docx_processor,
            '.doc': docx_processor,
            '.txt': text_processor,
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
                detail=f"Unsupported file type: {file_extension}"
            )

        # Save uploaded file
        app_logger.info(f"Saving file: {file.filename}")
        saved_path = storage_manager.save_file(
            file.file, 
            file.filename, 
            content_type=file.content_type
        )
        app_logger.info(f"File saved successfully to: {saved_path}")
        
        # For local processing, we might still need a local path if the processors expect it
        # If storage is remote, we might need to download it to a temp file for processing
        # For now, if storage is local, saved_path is the path.
        # If remote, we need to handle it.
        
        if settings.storage_type == "local":
            file_path = Path(saved_path)
        else:
            # Create a temp file for processing
            # This is a simplification; ideally processors should handle streams or URLs
            # But for now, let's keep the local file for processing logic
            file_path = UPLOAD_DIR / file.filename
            if not file_path.exists(): # If it wasn't saved locally by storage manager
                file.file.seek(0)
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)

        # Process document
        app_logger.info(f"Starting document processing with {file_extension} processor")
        processor = supported_types[file_extension]
        processing_result = processor.process(file_path)
        app_logger.info(f"Processing complete. Success: {processing_result.get('success')}")

        # Generate embeddings if requested
        embeddings_created = False
        if create_embeddings and processing_result.get('success') and processing_result.get('text'):
            try:
                # Create chunks
                text = processing_result['text']
                
                # Generate embeddings
                embeddings = embedding_generator.generate_embeddings(
                    texts=[text],
                    chunk_size=chunk_size
                )
                
                if embeddings:
                    # Store in vector db
                    vector_store.add_embeddings(
                        embeddings, 
                        metadata=[{
                            'filename': file.filename,
                            'file_type': file_extension,
                            'source': 'upload',
                            **processing_result.get('metadata', {})
                        }] * len(embeddings)
                    )
                    embeddings_created = True
                    app_logger.info(f"Created {len(embeddings)} embeddings for {file.filename}")
            except Exception as e:
                app_logger.error(f"Embedding generation failed: {e}")
                # We don't fail the whole request if embeddings fail, just note it
                processing_result['embedding_error'] = str(e)

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
    """
    Scrape all courses from Entrepedia platform.
    """
    try:
        app_logger.info("Starting Entrepedia scraping")

        # Perform scraping
        scraped_files = scraper.scrape_all()

        if not scraped_files:
            return {
                "success": False,
                "message": "No files were scraped. Check credentials and network connection.",
                "files_scraped": 0
            }

        # Process scraped files
        processed_count = 0
        embeddings_count = 0
        errors = []

        for file_info in scraped_files:
            try:
                file_path = Path(file_info['local_path'])
                file_type = file_info['type']

                # Process based on file type
                if file_type == 'pdf':
                    result = pdf_processor.process(file_path)
                elif file_type == 'docx':
                    result = docx_processor.process(file_path)
                elif file_type == 'image':
                    result = image_processor.process(file_path)
                elif file_type == 'audio':
                    result = audio_processor.process(file_path)
                else:
                    continue  # Skip unsupported types

                if result.get('success') and result.get('text'):
                    processed_count += 1

                    # Generate embeddings
                    try:
                        embeddings = embedding_generator.generate_embeddings([result['text']])
                        if embeddings:
                            metadata = [{
                                'filename': file_info['filename'],
                                'course': file_info.get('course', 'Unknown'),
                                'course_id': file_info.get('course_id', 'Unknown'),
                                'source': 'entrepedia_scraper',
                                'file_type': file_type,
                                'source_url': file_info.get('url', '')
                            }]

                            if vector_store.add_embeddings(embeddings, metadata):
                                embeddings_count += 1

                    except Exception as e:
                        errors.append(f"Embedding failed for {file_info['filename']}: {e}")

            except Exception as e:
                errors.append(f"Processing failed for {file_info.get('filename', 'unknown')}: {e}")

        return {
            "success": True,
            "files_scraped": len(scraped_files),
            "files_processed": processed_count,
            "embeddings_created": embeddings_count,
            "errors": errors[:10],  # Limit errors shown
            "total_errors": len(errors)
        }

    except Exception as e:
        app_logger.error(f"Entrepedia scraping failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Scraping failed: {str(e)}"
        )


@router.get("/scraping-status")
async def get_scraping_status() -> ScrapingStatus:
    """
    Get status of any ongoing scraping operations.
    """
    # This would typically check a task queue or database for active scraping jobs
    # For now, return a simple status
    return ScrapingStatus(
        status="idle",
        files_found=0,
        files_processed=0
    )


@router.get("/processed")
async def list_processed_documents() -> Dict[str, Any]:
    """
    List all processed documents and their status.
    """
    try:
        # List files in upload and scraping directories
        upload_files = []
        scraping_files = []

        # Check upload directory
        if UPLOAD_DIR.exists():
            for file_path in UPLOAD_DIR.iterdir():
                if file_path.is_file():
                    upload_files.append({
                        "filename": file_path.name,
                        "size": file_path.stat().st_size,
                        "modified": file_path.stat().st_mtime,
                        "source": "upload"
                    })

        # Check scraping directory
        scraping_dir = Path(settings.output_dir)
        if scraping_dir.exists():
            for course_dir in scraping_dir.iterdir():
                if course_dir.is_dir() and course_dir.name != "uploads":
                    for file_path in course_dir.iterdir():
                        if file_path.is_file():
                            scraping_files.append({
                                "filename": file_path.name,
                                "course": course_dir.name,
                                "size": file_path.stat().st_size,
                                "modified": file_path.stat().st_mtime,
                                "source": "scraper"
                            })

        return {
            "success": True,
            "upload_files": upload_files,
            "scraped_files": scraping_files,
            "total_files": len(upload_files) + len(scraping_files)
        }

    except Exception as e:
        app_logger.error(f"Failed to list processed documents: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list documents: {str(e)}"
        )


@router.get("/list")
async def list_documents() -> Dict[str, Any]:
    """
    List all documents (alias for /processed endpoint).
    """
    return await list_processed_documents()



@router.delete("/delete/{filename}")
async def delete_document(filename: str) -> Dict[str, Any]:
    """
    Delete a processed document and its embeddings.
    """
    try:
        # Find and delete file
        file_deleted = False

        # Check upload directory
        upload_file = UPLOAD_DIR / filename
        if upload_file.exists():
            upload_file.unlink()
            file_deleted = True

        # Check scraping directories
        scraping_dir = Path(settings.output_dir)
        for course_dir in scraping_dir.iterdir():
            if course_dir.is_dir():
                file_path = course_dir / filename
                if file_path.exists():
                    file_path.unlink()
                    file_deleted = True
                    break

        if not file_deleted:
            raise HTTPException(
                status_code=404,
                detail=f"File not found: {filename}"
            )

        # TODO: Remove embeddings from vector store
        # This would require implementing embedding deletion by filename

        return {
            "success": True,
            "message": f"Deleted {filename}",
            "filename": filename
        }

    except Exception as e:
        app_logger.error(f"Failed to delete document: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Deletion failed: {str(e)}"
        )


@router.get("/stats")
async def get_document_stats() -> Dict[str, Any]:
    """
    Get statistics about processed documents.
    """
    try:
        # Count files by type
        upload_dir = Path(settings.output_dir) / "uploads"
        scraping_dir = Path(settings.output_dir)

        file_types = {}
        total_size = 0
        total_files = 0

        # Process upload directory
        if upload_dir.exists():
            for file_path in upload_dir.rglob("*"):
                if file_path.is_file():
                    ext = file_path.suffix.lower()
                    file_types[ext] = file_types.get(ext, 0) + 1
                    total_size += file_path.stat().st_size
                    total_files += 1

        # Process scraping directory
        for course_dir in scraping_dir.iterdir():
            if course_dir.is_dir() and course_dir.name != "uploads":
                for file_path in course_dir.rglob("*"):
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
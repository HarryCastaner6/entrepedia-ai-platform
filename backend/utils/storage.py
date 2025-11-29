import shutil
import boto3
from pathlib import Path
from typing import BinaryIO, Optional
from backend.utils.config import settings
from backend.utils.logger import app_logger

try:
    from supabase import create_client, Client
except ImportError:
    create_client = None

class StorageManager:
    def __init__(self):
        self.storage_type = settings.storage_type
        self.local_dir = Path(settings.output_dir) / "uploads"
        self.local_dir.mkdir(parents=True, exist_ok=True)
        
        self.s3_client = None
        self.supabase_client: Optional[Client] = None
        
        if self.storage_type == "s3":
            self._init_s3()
        elif self.storage_type == "supabase":
            self._init_supabase()

    def _init_s3(self):
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=settings.aws_region,
                endpoint_url=settings.aws_endpoint_url
            )
        except Exception as e:
            app_logger.error(f"Failed to initialize S3 client: {e}")

    def _init_supabase(self):
        if not create_client:
            app_logger.error("Supabase client not installed")
            return
            
        try:
            self.supabase_client = create_client(
                settings.supabase_url,
                settings.supabase_key
            )
        except Exception as e:
            app_logger.error(f"Failed to initialize Supabase client: {e}")

    def save_file(self, file_obj: BinaryIO, filename: str, content_type: str = None) -> str:
        """
        Save file to storage and return the path/url.
        """
        if self.storage_type == "local":
            return self._save_local(file_obj, filename)
        elif self.storage_type == "s3":
            return self._save_s3(file_obj, filename, content_type)
        elif self.storage_type == "supabase":
            return self._save_supabase(file_obj, filename, content_type)
        else:
            raise ValueError(f"Unsupported storage type: {self.storage_type}")

    def _save_local(self, file_obj: BinaryIO, filename: str) -> str:
        file_path = self.local_dir / filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file_obj, buffer)
        return str(file_path)

    def _save_s3(self, file_obj: BinaryIO, filename: str, content_type: str) -> str:
        if not self.s3_client:
            raise RuntimeError("S3 client not initialized")
            
        try:
            extra_args = {'ContentType': content_type} if content_type else {}
            self.s3_client.upload_fileobj(
                file_obj,
                settings.s3_bucket,
                filename,
                ExtraArgs=extra_args
            )
            return f"s3://{settings.s3_bucket}/{filename}"
        except Exception as e:
            app_logger.error(f"S3 upload failed: {e}")
            raise

    def _save_supabase(self, file_obj: BinaryIO, filename: str, content_type: str) -> str:
        if not self.supabase_client:
            raise RuntimeError("Supabase client not initialized")
            
        try:
            bucket_name = settings.s3_bucket or "courses"
            file_content = file_obj.read()
            
            self.supabase_client.storage.from_(bucket_name).upload(
                path=filename,
                file=file_content,
                file_options={"content-type": content_type} if content_type else None
            )
            
            # Get public URL
            res = self.supabase_client.storage.from_(bucket_name).get_public_url(filename)
            return res
        except Exception as e:
            app_logger.error(f"Supabase upload failed: {e}")
            raise

    def delete_file(self, filename: str) -> bool:
        if self.storage_type == "local":
            file_path = self.local_dir / filename
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        elif self.storage_type == "supabase":
             try:
                bucket_name = settings.s3_bucket or "courses"
                self.supabase_client.storage.from_(bucket_name).remove([filename])
                return True
             except Exception as e:
                app_logger.error(f"Supabase delete failed: {e}")
                return False
        # Implement S3 delete if needed
        return False

# Global instance
storage_manager = StorageManager()

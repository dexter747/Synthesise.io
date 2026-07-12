"""
File storage utilities for Synthesize.io API.
Handles file operations for generated datasets.
"""
import os
import hashlib
import shutil
import gzip
from pathlib import Path
from typing import Optional, BinaryIO, Generator
from datetime import datetime
import uuid
import logging

from app.core.config import settings


logger = logging.getLogger(__name__)


class StorageError(Exception):
    """Storage operation error."""
    pass


class FileStorage:
    """
    File storage manager for generated datasets.
    
    Directory structure:
    /data/generated/
    ├── {user_id}/
    │   ├── {dataset_id}/
    │   │   ├── data.csv
    │   │   ├── data.csv.gz (compressed)
    │   │   └── metadata.json
    """
    
    def __init__(self, base_path: Optional[str] = None):
        self.base_path = Path(base_path or settings.STORAGE_PATH)
        self._ensure_directory(self.base_path)
    
    def _ensure_directory(self, path: Path) -> None:
        """Ensure directory exists."""
        path.mkdir(parents=True, exist_ok=True)
    
    def _get_user_path(self, user_id: str) -> Path:
        """Get user's storage directory."""
        path = self.base_path / str(user_id)
        self._ensure_directory(path)
        return path
    
    def _get_dataset_path(self, user_id: str, dataset_id: str) -> Path:
        """Get dataset's storage directory."""
        path = self._get_user_path(user_id) / str(dataset_id)
        self._ensure_directory(path)
        return path
    
    def get_file_path(
        self,
        user_id: str,
        dataset_id: str,
        filename: str,
        compressed: bool = False
    ) -> Path:
        """
        Get full file path for a dataset file.
        
        Args:
            user_id: User ID
            dataset_id: Dataset ID
            filename: Base filename
            compressed: Whether to get compressed version
        
        Returns:
            Full file path
        """
        dataset_path = self._get_dataset_path(user_id, dataset_id)
        if compressed:
            filename = f"{filename}.gz"
        return dataset_path / filename
    
    def save_file(
        self,
        user_id: str,
        dataset_id: str,
        filename: str,
        content: bytes,
        compress: bool = True
    ) -> tuple:
        """
        Save file content to storage.
        
        Args:
            user_id: User ID
            dataset_id: Dataset ID
            filename: Filename
            content: File content as bytes
            compress: Whether to also save compressed version
        
        Returns:
            Tuple of (file_path, file_size, checksum)
        """
        file_path = self.get_file_path(user_id, dataset_id, filename)
        
        # Calculate checksum
        checksum = hashlib.sha256(content).hexdigest()
        
        try:
            # Save uncompressed
            with open(file_path, 'wb') as f:
                f.write(content)
            
            file_size = len(content)
            
            # Save compressed version if requested
            if compress:
                compressed_path = self.get_file_path(user_id, dataset_id, filename, compressed=True)
                with gzip.open(compressed_path, 'wb') as f:
                    f.write(content)
            
            logger.info(f"Saved file: {file_path} ({file_size} bytes)")
            
            return str(file_path), file_size, checksum
        
        except Exception as e:
            logger.error(f"Failed to save file: {e}")
            raise StorageError(f"Failed to save file: {e}")
    
    def save_file_stream(
        self,
        user_id: str,
        dataset_id: str,
        filename: str,
        stream: BinaryIO,
        compress: bool = True
    ) -> tuple:
        """
        Save file from stream.
        
        Args:
            user_id: User ID
            dataset_id: Dataset ID
            filename: Filename
            stream: Binary file stream
            compress: Whether to also save compressed version
        
        Returns:
            Tuple of (file_path, file_size, checksum)
        """
        file_path = self.get_file_path(user_id, dataset_id, filename)
        
        hasher = hashlib.sha256()
        file_size = 0
        
        try:
            # Save and calculate checksum in chunks
            with open(file_path, 'wb') as f:
                for chunk in iter(lambda: stream.read(8192), b''):
                    f.write(chunk)
                    hasher.update(chunk)
                    file_size += len(chunk)
            
            checksum = hasher.hexdigest()
            
            # Create compressed version if requested
            if compress and file_size > 0:
                compressed_path = self.get_file_path(user_id, dataset_id, filename, compressed=True)
                with open(file_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            
            logger.info(f"Saved file stream: {file_path} ({file_size} bytes)")
            
            return str(file_path), file_size, checksum
        
        except Exception as e:
            logger.error(f"Failed to save file stream: {e}")
            raise StorageError(f"Failed to save file stream: {e}")
    
    def read_file(
        self,
        user_id: str,
        dataset_id: str,
        filename: str,
        compressed: bool = False
    ) -> bytes:
        """
        Read file content.
        
        Args:
            user_id: User ID
            dataset_id: Dataset ID
            filename: Filename
            compressed: Whether to read compressed version
        
        Returns:
            File content as bytes
        """
        file_path = self.get_file_path(user_id, dataset_id, filename, compressed)
        
        if not file_path.exists():
            raise StorageError(f"File not found: {file_path}")
        
        try:
            if compressed or str(file_path).endswith('.gz'):
                with gzip.open(file_path, 'rb') as f:
                    return f.read()
            else:
                with open(file_path, 'rb') as f:
                    return f.read()
        
        except Exception as e:
            logger.error(f"Failed to read file: {e}")
            raise StorageError(f"Failed to read file: {e}")
    
    def stream_file(
        self,
        user_id: str,
        dataset_id: str,
        filename: str,
        chunk_size: int = 8192
    ) -> Generator[bytes, None, None]:
        """
        Stream file content in chunks.
        
        Args:
            user_id: User ID
            dataset_id: Dataset ID
            filename: Filename
            chunk_size: Size of each chunk
        
        Yields:
            File content chunks
        """
        file_path = self.get_file_path(user_id, dataset_id, filename)
        
        if not file_path.exists():
            raise StorageError(f"File not found: {file_path}")
        
        try:
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
        
        except Exception as e:
            logger.error(f"Failed to stream file: {e}")
            raise StorageError(f"Failed to stream file: {e}")
    
    def delete_file(
        self,
        user_id: str,
        dataset_id: str,
        filename: str,
        include_compressed: bool = True
    ) -> bool:
        """
        Delete a file.
        
        Args:
            user_id: User ID
            dataset_id: Dataset ID
            filename: Filename
            include_compressed: Also delete compressed version
        
        Returns:
            True if deleted successfully
        """
        file_path = self.get_file_path(user_id, dataset_id, filename)
        
        deleted = False
        
        try:
            if file_path.exists():
                file_path.unlink()
                deleted = True
            
            if include_compressed:
                compressed_path = self.get_file_path(user_id, dataset_id, filename, compressed=True)
                if compressed_path.exists():
                    compressed_path.unlink()
                    deleted = True
            
            return deleted
        
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            raise StorageError(f"Failed to delete file: {e}")
    
    def delete_dataset(self, user_id: str, dataset_id: str) -> bool:
        """
        Delete entire dataset directory.
        
        Args:
            user_id: User ID
            dataset_id: Dataset ID
        
        Returns:
            True if deleted successfully
        """
        dataset_path = self._get_dataset_path(user_id, dataset_id)
        
        try:
            if dataset_path.exists():
                shutil.rmtree(dataset_path)
                logger.info(f"Deleted dataset directory: {dataset_path}")
                return True
            return False
        
        except Exception as e:
            logger.error(f"Failed to delete dataset directory: {e}")
            raise StorageError(f"Failed to delete dataset directory: {e}")
    
    def get_file_size(self, user_id: str, dataset_id: str, filename: str) -> int:
        """Get file size in bytes."""
        file_path = self.get_file_path(user_id, dataset_id, filename)
        
        if not file_path.exists():
            return 0
        
        return file_path.stat().st_size
    
    def file_exists(self, user_id: str, dataset_id: str, filename: str) -> bool:
        """Check if file exists."""
        file_path = self.get_file_path(user_id, dataset_id, filename)
        return file_path.exists()
    
    def get_user_storage_size(self, user_id: str) -> int:
        """
        Get total storage used by a user.
        
        Returns:
            Total size in bytes
        """
        user_path = self._get_user_path(user_id)
        
        total_size = 0
        for file_path in user_path.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        
        return total_size
    
    def cleanup_expired_datasets(
        self,
        datasets: list,  # List of (user_id, dataset_id) tuples
        batch_size: int = 100
    ) -> int:
        """
        Clean up expired datasets.
        
        Args:
            datasets: List of (user_id, dataset_id) tuples
            batch_size: Maximum number to clean up
        
        Returns:
            Number of datasets deleted
        """
        deleted_count = 0
        
        for user_id, dataset_id in datasets[:batch_size]:
            try:
                if self.delete_dataset(user_id, dataset_id):
                    deleted_count += 1
            except StorageError as e:
                logger.warning(f"Failed to delete dataset {dataset_id}: {e}")
        
        return deleted_count


    def get_file(self, file_path: str) -> Optional[bytes]:
        """
        Read file content from an absolute file path.
        Used by download endpoints when file_path is stored directly.
        
        Args:
            file_path: Absolute path to the file
        
        Returns:
            File content as bytes, or None if not found
        """
        path = Path(file_path)
        
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return None
        
        try:
            if str(path).endswith('.gz'):
                with gzip.open(path, 'rb') as f:
                    return f.read()
            else:
                with open(path, 'rb') as f:
                    return f.read()
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return None


# Global storage instance
file_storage = FileStorage()

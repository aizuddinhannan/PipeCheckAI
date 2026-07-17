"""
File handling utilities for drawing uploads.

Provides validation, metadata extraction, and storage for DWG, DXF, and PDF files.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from utils.drawing_reader import DrawingInfo, DrawingReader

# Supported drawing file extensions (lowercase).
ALLOWED_EXTENSIONS = {".dwg", ".dxf", ".pdf"}


class FileHandler:
    """Handles drawing file selection, validation, and storage."""

    def __init__(self, drawings_dir: Path) -> None:
        """
        Initialize the file handler with a target directory for uploaded drawings.

        Args:
            drawings_dir: Folder where uploaded files are copied for processing.
        """
        self.drawings_dir = drawings_dir
        self.drawings_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def is_allowed_file(filepath: str) -> bool:
        """
        Check whether the selected file has an allowed extension.

        Args:
            filepath: Absolute or relative path to the file.

        Returns:
            True if the extension is DWG, DXF, or PDF.
        """
        return Path(filepath).suffix.lower() in ALLOWED_EXTENSIONS

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        Convert a byte count into a human-readable size string.

        Args:
            size_bytes: File size in bytes.

        Returns:
            Formatted string such as '1.25 MB'.
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        if size_bytes < 1024 ** 2:
            return f"{size_bytes / 1024:.2f} KB"
        if size_bytes < 1024 ** 3:
            return f"{size_bytes / (1024 ** 2):.2f} MB"
        return f"{size_bytes / (1024 ** 3):.2f} GB"

    @staticmethod
    def get_file_metadata(filepath: str) -> dict:
        """
        Extract display metadata from a file on disk.

        Args:
            filepath: Path to the source file.

        Returns:
            Dictionary with filename, size, date, and status fields.
        """
        path = Path(filepath)
        stat = path.stat()
        modified = datetime.fromtimestamp(stat.st_mtime)

        return {
            "filename": path.name,
            "file_size": FileHandler.format_file_size(stat.st_size),
            "date": modified.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "Loaded Successfully",
            "source_path": str(path.resolve()),
        }

    def save_drawing(self, source_path: str) -> Optional[dict]:
        """
        Copy an uploaded drawing into the project drawings folder.

        Args:
            source_path: Path to the user-selected file.

        Returns:
            Metadata dict on success, or None if validation fails.
        """
        if not self.is_allowed_file(source_path):
            return None

        if not os.path.isfile(source_path):
            return None

        filename = Path(source_path).name
        destination = self.drawings_dir / filename

        # Avoid overwriting: append a numeric suffix if the name already exists.
        if destination.exists():
            stem = destination.stem
            suffix = destination.suffix
            counter = 1
            while destination.exists():
                destination = self.drawings_dir / f"{stem}_{counter}{suffix}"
                counter += 1

        shutil.copy2(source_path, destination)

        metadata = self.get_file_metadata(str(destination))
        metadata["stored_path"] = str(destination)
        metadata["drawing_info"] = self._extract_drawing_info(str(destination), metadata["file_size"])
        return metadata

    @staticmethod
    def _extract_drawing_info(stored_path: str, file_size: str) -> Optional[DrawingInfo]:
        """
        Parse CAD drawing statistics for DXF and DWG uploads.

        Args:
            stored_path: Path to the copied file in the drawings folder.
            file_size: Pre-formatted file size string for display.

        Returns:
            DrawingInfo for DXF/DWG files, or None for PDF and other formats.
        """
        return DrawingReader.read_drawing(stored_path, file_size)

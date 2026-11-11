"""
GHOST File Management Tools
Provides safe directory inspection, duplicate detection, and file staging.
All destructive operations require Level 3 authorization.
"""

import os
import hashlib
from pathlib import Path
from typing import Dict, Any, List


def calculate_file_hash(filepath: Path) -> str:
    """Calculates SHA-256 hash for file content comparison."""
    hasher = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return ""


def scan_directory(target_path: str = ".") -> Dict[str, Any]:
    """Inspects a target directory and compiles file statistics."""
    p = Path(target_path).resolve()
    if not p.exists():
        return {"success": False, "error": f"Path '{target_path}' does not exist."}

    file_count = 0
    total_size = 0
    extensions = {}

    for item in p.rglob("*"):
        if item.is_file():
            file_count += 1
            sz = item.stat().st_size
            total_size += sz
            ext = item.suffix.lower() or "no_ext"
            extensions[ext] = extensions.get(ext, 0) + 1

    return {
        "success": True,
        "path": str(p),
        "total_files": file_count,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "extensions": extensions
    }


def find_duplicates(target_path: str = ".") -> List[Dict[str, Any]]:
    """Identifies duplicate files based on content hashes."""
    p = Path(target_path).resolve()
    hashes = {}
    duplicates = []

    for item in p.rglob("*"):
        if item.is_file():
            h = calculate_file_hash(item)
            if not h:
                continue
            if h in hashes:
                duplicates.append({
                    "original": str(hashes[h]),
                    "duplicate": str(item),
                    "size_bytes": item.stat().st_size
                })
            else:
                hashes[h] = item

    return duplicates


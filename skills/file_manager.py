# skills/file_manager.py

import os
import shutil
import stat
from pathlib import Path
from typing import Optional, List, Dict, Union
from datetime import datetime
import mimetypes
import json

from core.logger import log_info, log_error, log_warning, log_debug


class FileManager:
    """Enhanced file manager with advanced file operations"""
    
    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = Path(base_dir) if base_dir else Path.home()
        self.trash_dir = self.base_dir / ".matrix_trash"
        self.trash_dir.mkdir(parents=True, exist_ok=True)
        
        # Statistics
        self.stats = {
            'files_created': 0,
            'folders_created': 0,
            'files_deleted': 0,
            'files_moved': 0,
            'files_copied': 0,
            'operations_failed': 0
        }
        
        log_info(f"File Manager initialized with base: {self.base_dir}")
    
    def create_folder(self, name: str, path: Optional[str] = None) -> bool:
        """
        Create a new folder
        
        Args:
            name: Folder name
            path: Optional path (default: base_dir)
            
        Returns:
            bool: True if created successfully
        """
        try:
            target_path = Path(path) if path else self.base_dir
            folder_path = target_path / name
            
            if folder_path.exists():
                log_warning(f"Folder already exists: {folder_path}")
                return False
            
            folder_path.mkdir(parents=True, exist_ok=False)
            self.stats['folders_created'] += 1
            
            log_info(f"Created folder: {folder_path}")
            return True
            
        except Exception as e:
            log_error(f"Error creating folder '{name}': {e}")
            self.stats['operations_failed'] += 1
            return False
    
    def create_file(self, name: str, content: str = "", path: Optional[str] = None) -> bool:
        """
        Create a new file with optional content
        
        Args:
            name: File name
            content: File content
            path: Optional path (default: base_dir)
            
        Returns:
            bool: True if created successfully
        """
        try:
            target_path = Path(path) if path else self.base_dir
            file_path = target_path / name
            
            if file_path.exists():
                log_warning(f"File already exists: {file_path}")
                return False
            
            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content
            file_path.write_text(content, encoding='utf-8')
            self.stats['files_created'] += 1
            
            log_info(f"Created file: {file_path}")
            return True
            
        except Exception as e:
            log_error(f"Error creating file '{name}': {e}")
            self.stats['operations_failed'] += 1
            return False
    
    def delete_file(self, name: str, path: Optional[str] = None, 
                    permanent: bool = False) -> bool:
        """
        Delete a file (move to trash by default)
        
        Args:
            name: File name
            path: Optional path
            permanent: If True, delete permanently (dangerous!)
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            target_path = Path(path) if path else self.base_dir
            file_path = target_path / name
            
            if not file_path.exists():
                log_warning(f"File not found: {file_path}")
                return False
            
            if not file_path.is_file():
                log_warning(f"Not a file: {file_path}")
                return False
            
            if permanent:
                file_path.unlink()
                log_info(f"Permanently deleted: {file_path}")
            else:
                # Move to trash
                trash_file = self.trash_dir / f"{file_path.name}_{int(datetime.now().timestamp())}"
                shutil.move(str(file_path), str(trash_file))
                log_info(f"Moved to trash: {file_path} -> {trash_file}")
            
            self.stats['files_deleted'] += 1
            return True
            
        except Exception as e:
            log_error(f"Error deleting file '{name}': {e}")
            self.stats['operations_failed'] += 1
            return False
    
    def delete_folder(self, name: str, path: Optional[str] = None, 
                     permanent: bool = False) -> bool:
        """
        Delete a folder and its contents
        
        Args:
            name: Folder name
            path: Optional path
            permanent: If True, delete permanently
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            target_path = Path(path) if path else self.base_dir
            folder_path = target_path / name
            
            if not folder_path.exists():
                log_warning(f"Folder not found: {folder_path}")
                return False
            
            if not folder_path.is_dir():
                log_warning(f"Not a folder: {folder_path}")
                return False
            
            if permanent:
                shutil.rmtree(folder_path)
                log_info(f"Permanently deleted folder: {folder_path}")
            else:
                # Move to trash
                trash_folder = self.trash_dir / f"{folder_path.name}_{int(datetime.now().timestamp())}"
                shutil.move(str(folder_path), str(trash_folder))
                log_info(f"Moved folder to trash: {folder_path}")
            
            return True
            
        except Exception as e:
            log_error(f"Error deleting folder '{name}': {e}")
            self.stats['operations_failed'] += 1
            return False
    
    def rename_file(self, old_name: str, new_name: str, path: Optional[str] = None) -> bool:
        """
        Rename a file or folder
        
        Args:
            old_name: Current name
            new_name: New name
            path: Optional path
            
        Returns:
            bool: True if renamed successfully
        """
        try:
            target_path = Path(path) if path else self.base_dir
            old_path = target_path / old_name
            new_path = target_path / new_name
            
            if not old_path.exists():
                log_warning(f"File not found: {old_path}")
                return False
            
            if new_path.exists():
                log_warning(f"Target already exists: {new_path}")
                return False
            
            old_path.rename(new_path)
            log_info(f"Renamed: {old_path} -> {new_path}")
            return True
            
        except Exception as e:
            log_error(f"Error renaming '{old_name}' to '{new_name}': {e}")
            self.stats['operations_failed'] += 1
            return False
    
    def move_file(self, name: str, destination: str, source_path: Optional[str] = None) -> bool:
        """
        Move a file to a different location
        
        Args:
            name: File name
            destination: Destination path
            source_path: Optional source path
            
        Returns:
            bool: True if moved successfully
        """
        try:
            source_dir = Path(source_path) if source_path else self.base_dir
            source_file = source_dir / name
            dest_path = Path(destination)
            
            if not source_file.exists():
                log_warning(f"Source file not found: {source_file}")
                return False
            
            # Create destination directory if needed
            dest_path.mkdir(parents=True, exist_ok=True)
            
            dest_file = dest_path / name
            shutil.move(str(source_file), str(dest_file))
            
            self.stats['files_moved'] += 1
            log_info(f"Moved: {source_file} -> {dest_file}")
            return True
            
        except Exception as e:
            log_error(f"Error moving file '{name}': {e}")
            self.stats['operations_failed'] += 1
            return False
    
    def copy_file(self, name: str, destination: str, source_path: Optional[str] = None) -> bool:
        """
        Copy a file to a different location
        
        Args:
            name: File name
            destination: Destination path
            source_path: Optional source path
            
        Returns:
            bool: True if copied successfully
        """
        try:
            source_dir = Path(source_path) if source_path else self.base_dir
            source_file = source_dir / name
            dest_path = Path(destination)
            
            if not source_file.exists():
                log_warning(f"Source file not found: {source_file}")
                return False
            
            # Create destination directory if needed
            dest_path.mkdir(parents=True, exist_ok=True)
            
            dest_file = dest_path / name
            shutil.copy2(str(source_file), str(dest_file))
            
            self.stats['files_copied'] += 1
            log_info(f"Copied: {source_file} -> {dest_file}")
            return True
            
        except Exception as e:
            log_error(f"Error copying file '{name}': {e}")
            self.stats['operations_failed'] += 1
            return False
    
    def search_files(self, pattern: str, path: Optional[str] = None, 
                    recursive: bool = True) -> List[Path]:
        """
        Search for files matching pattern
        
        Args:
            pattern: Search pattern (supports wildcards)
            path: Optional search path
            recursive: Search in subdirectories
            
        Returns:
            List of matching file paths
        """
        try:
            search_path = Path(path) if path else self.base_dir
            
            if recursive:
                matches = list(search_path.rglob(pattern))
            else:
                matches = list(search_path.glob(pattern))
            
            log_info(f"Found {len(matches)} files matching '{pattern}'")
            return matches
            
        except Exception as e:
            log_error(f"Error searching files: {e}")
            return []
    
    def get_file_info(self, name: str, path: Optional[str] = None) -> Optional[Dict]:
        """
        Get detailed file information
        
        Args:
            name: File name
            path: Optional path
            
        Returns:
            Dictionary with file info or None
        """
        try:
            target_path = Path(path) if path else self.base_dir
            file_path = target_path / name
            
            if not file_path.exists():
                return None
            
            stat_info = file_path.stat()
            
            info = {
                'name': file_path.name,
                'path': str(file_path.absolute()),
                'size': stat_info.st_size,
                'size_human': self._human_readable_size(stat_info.st_size),
                'created': datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                'accessed': datetime.fromtimestamp(stat_info.st_atime).isoformat(),
                'is_file': file_path.is_file(),
                'is_directory': file_path.is_dir(),
                'extension': file_path.suffix,
                'mime_type': mimetypes.guess_type(str(file_path))[0]
            }
            
            return info
            
        except Exception as e:
            log_error(f"Error getting file info: {e}")
            return None
    
    def list_directory(self, path: Optional[str] = None, 
                      show_hidden: bool = False) -> Dict[str, List[str]]:
        """
        List directory contents
        
        Args:
            path: Optional directory path
            show_hidden: Include hidden files
            
        Returns:
            Dictionary with 'files' and 'folders' lists
        """
        try:
            target_path = Path(path) if path else self.base_dir
            
            if not target_path.exists() or not target_path.is_dir():
                log_warning(f"Invalid directory: {target_path}")
                return {'files': [], 'folders': []}
            
            items = list(target_path.iterdir())
            
            if not show_hidden:
                items = [item for item in items if not item.name.startswith('.')]
            
            files = [item.name for item in items if item.is_file()]
            folders = [item.name for item in items if item.is_dir()]
            
            return {
                'files': sorted(files),
                'folders': sorted(folders)
            }
            
        except Exception as e:
            log_error(f"Error listing directory: {e}")
            return {'files': [], 'folders': []}
    
    def get_disk_usage(self, path: Optional[str] = None) -> Dict:
        """Get disk usage information"""
        try:
            target_path = Path(path) if path else self.base_dir
            usage = shutil.disk_usage(target_path)
            
            return {
                'total': usage.total,
                'used': usage.used,
                'free': usage.free,
                'total_human': self._human_readable_size(usage.total),
                'used_human': self._human_readable_size(usage.used),
                'free_human': self._human_readable_size(usage.free),
                'percent_used': (usage.used / usage.total * 100) if usage.total > 0 else 0
            }
            
        except Exception as e:
            log_error(f"Error getting disk usage: {e}")
            return {}
    
    def empty_trash(self) -> bool:
        """Empty the trash directory"""
        try:
            if self.trash_dir.exists():
                shutil.rmtree(self.trash_dir)
                self.trash_dir.mkdir(parents=True, exist_ok=True)
                log_info("Trash emptied successfully")
                return True
            return False
        except Exception as e:
            log_error(f"Error emptying trash: {e}")
            return False
    
    def _human_readable_size(self, size: int) -> str:
        """Convert bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"
    
    def get_stats(self) -> Dict:
        """Get file manager statistics"""
        return self.stats.copy()


# Global file manager instance
_file_manager: Optional[FileManager] = None


def get_file_manager() -> FileManager:
    """Get or create global file manager instance"""
    global _file_manager
    if _file_manager is None:
        _file_manager = FileManager()
    return _file_manager


def get_matrix_speech():
    """Get Matrix speech engine"""
    try:
        from core.speech import SpeechEngine
        return SpeechEngine()
    except:
        return None


# Convenience functions
def create_folder(name: str, path: Optional[str] = None):
    """Create a new folder"""
    fm = get_file_manager()
    speech = get_matrix_speech()
    
    try:
        if fm.create_folder(name, path):
            if speech:
                speech.speak(f"Folder '{name}' created successfully")
            log_info(f"Folder created: {name}")
        else:
            if speech:
                speech.speak(f"Folder '{name}' already exists or couldn't be created")
    except Exception as e:
        if speech:
            speech.speak("Error creating folder")
        log_error(f"Error in create_folder: {e}")


def delete_file(name: str, path: Optional[str] = None):
    """Delete a file (moves to trash)"""
    fm = get_file_manager()
    speech = get_matrix_speech()
    
    try:
        if fm.delete_file(name, path):
            if speech:
                speech.speak(f"File '{name}' moved to trash")
            log_info(f"File deleted: {name}")
        else:
            if speech:
                speech.speak(f"File '{name}' not found")
    except Exception as e:
        if speech:
            speech.speak("Error deleting file")
        log_error(f"Error in delete_file: {e}")


def rename_file(old_name: str, new_name: str, path: Optional[str] = None):
    """Rename a file"""
    fm = get_file_manager()
    speech = get_matrix_speech()
    
    try:
        if fm.rename_file(old_name, new_name, path):
            if speech:
                speech.speak(f"Renamed '{old_name}' to '{new_name}'")
            log_info(f"File renamed: {old_name} -> {new_name}")
        else:
            if speech:
                speech.speak(f"Couldn't rename file")
    except Exception as e:
        if speech:
            speech.speak("Error renaming file")
        log_error(f"Error in rename_file: {e}")


def move_file(name: str, destination: str, source_path: Optional[str] = None):
    """Move a file"""
    fm = get_file_manager()
    speech = get_matrix_speech()
    
    try:
        if fm.move_file(name, destination, source_path):
            if speech:
                speech.speak(f"Moved '{name}' to {destination}")
        else:
            if speech:
                speech.speak("Couldn't move file")
    except Exception as e:
        if speech:
            speech.speak("Error moving file")
        log_error(f"Error in move_file: {e}")


def copy_file(name: str, destination: str, source_path: Optional[str] = None):
    """Copy a file"""
    fm = get_file_manager()
    speech = get_matrix_speech()
    
    try:
        if fm.copy_file(name, destination, source_path):
            if speech:
                speech.speak(f"Copied '{name}' to {destination}")
        else:
            if speech:
                speech.speak("Couldn't copy file")
    except Exception as e:
        if speech:
            speech.speak("Error copying file")
        log_error(f"Error in copy_file: {e}")


def search_files(pattern: str, path: Optional[str] = None):
    """Search for files"""
    fm = get_file_manager()
    speech = get_matrix_speech()
    
    try:
        matches = fm.search_files(pattern, path)
        
        if speech:
            if matches:
                speech.speak(f"Found {len(matches)} files matching {pattern}")
            else:
                speech.speak(f"No files found matching {pattern}")
        
        return matches
    except Exception as e:
        if speech:
            speech.speak("Error searching files")
        log_error(f"Error in search_files: {e}")
        return []
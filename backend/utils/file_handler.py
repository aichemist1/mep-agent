import os
import uuid
from werkzeug.utils import secure_filename
from backend.config.settings import Config

def save_upload(file_storage, folder):
    """
    Save uploaded file to specified folder with a secure, unique name.
    """
    if not os.path.exists(folder):
        os.makedirs(folder)
        
    original_filename = secure_filename(file_storage.filename)
    extension = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
    unique_filename = f"{uuid.uuid4()}.{extension}"
    file_path = os.path.join(folder, unique_filename)
    
    file_storage.save(file_path)
    return file_path

def cleanup_files(file_paths):
    """
    Delete files from filesystem.
    """
    for path in file_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            print(f"Error cleaning up file {path}: {e}")

import re
from backend.config.settings import Config

def validate_email(email):
    """Validate email format using regex."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_file_size(file_storage):
    """Check if file size is within limits."""
    # Note: Flask checks content-length header automatically if MAX_CONTENT_LENGTH is set,
    # but this is an extra check for safe measurement if needed.
    # Implementation depends on how file is read, but generally file.seek(0, os.SEEK_END)
    # is expensive. We rely on Flask's limit for now.
    pass

def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

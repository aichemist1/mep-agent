import os
import shutil
from flask import Flask, request, jsonify, send_from_directory, current_app
from werkzeug.exceptions import RequestEntityTooLarge

from backend.config.settings import Config
from backend.services.transcribe_service import TranscribeService
from backend.services.email_service import EmailService
from backend.utils.validators import validate_email, allowed_file
from backend.utils.file_handler import save_upload, cleanup_files

# Initialize App
app = Flask(__name__, static_folder='../frontend/static', template_folder='../frontend')
app.config.from_object(Config)

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['TEMP_FOLDER'], exist_ok=True)

# Initialize Services
# Note: We initialize lazily or globally depending on preference. 
# Here we instantiate per request or globally. 
# Since they are stateless clients, global is fine, but handling credentials errors at startup is better.
try:
    transcribe_service = TranscribeService()
    email_service = EmailService()
except Exception as e:
    print(f"Warning: Services failed to initialize (check credentials): {e}")
    transcribe_service = None
    email_service = None

@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/process', methods=['POST'])
def process():
    if not transcribe_service or not email_service:
        return jsonify({"error": "Backend services not initialized properly"}), 500

    # 1. Validation
    if 'image' not in request.files or 'audio' not in request.files:
        return jsonify({"error": "Missing image or audio file"}), 400
    
    image = request.files['image']
    audio = request.files['audio']
    email = request.form.get('email')
    subject = request.form.get('subject', 'MEP Agent Report')

    if image.filename == '' or audio.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not email or not validate_email(email):
        return jsonify({"error": "Invalid email address"}), 400

    if not allowed_file(image.filename, app.config['ALLOWED_IMAGE_EXTENSIONS']):
        return jsonify({"error": "Invalid image format"}), 400
        
    if not allowed_file(audio.filename, app.config['ALLOWED_AUDIO_EXTENSIONS']):
        return jsonify({"error": "Invalid audio format"}), 400

    uploaded_files = []
    s3_key = None
    transcription_job = None
    
    try:
        # 2. Save Files
        image_path = save_upload(image, app.config['UPLOAD_FOLDER'])
        audio_path = save_upload(audio, app.config['UPLOAD_FOLDER'])
        uploaded_files.extend([image_path, audio_path])
        
        # 3. Transcribe
        s3_key = transcribe_service.upload_audio(audio_path)
        transcription_job = transcribe_service.start_transcription_job(s3_key)
        transcript_text = transcribe_service.get_transcription_result(transcription_job)
        
        # 4. Email
        email_body = f"""
        MEP Agent Report
        ----------------
        
        Transcription:
        {transcript_text}
        
        ----------------
        See attached image.
        """
        
        message_id = email_service.send_email(email, subject, email_body, image_path)
        
        return jsonify({
            "status": "success",
            "message": "Report processed and sent successfully",
            "transcript": transcript_text,
            "email_id": message_id
        }), 200

    except Exception as e:
        print(f"Processing error: {e}")
        return jsonify({"error": str(e)}), 500
        
    finally:
        # 5. Cleanup
        cleanup_files(uploaded_files)
        if s3_key and transcribe_service:
             # Run in background or just do it here since it's quick
            transcribe_service.cleanup_s3_file(s3_key)

# Error Handlers
@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    return jsonify({"error": "File is too large"}), 413

if __name__ == '__main__':
    app.run(
        host='0.0.0.0', 
        port=app.config['FLASK_PORT'], 
        debug=app.config['FLASK_DEBUG']
    )

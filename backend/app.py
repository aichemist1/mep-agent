import os
import shutil
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.exceptions import RequestEntityTooLarge

from backend.config.settings import Config
from backend.services.transcribe_service import TranscribeService
from backend.services.email_service import EmailService
from backend.services.llm_service import LLMService
from backend.utils.validators import validate_email, allowed_file
from backend.utils.file_handler import save_upload, cleanup_files

# Initialize App
app = Flask(__name__, static_folder='../frontend/static', template_folder='../frontend')
app.config.from_object(Config)

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['TEMP_FOLDER'], exist_ok=True)

# Initialize Services
try:
    transcribe_service = TranscribeService()
    email_service = EmailService()
    llm_service = LLMService()
except Exception as e:
    print(f"Warning: Services failed to initialize (check credentials): {e}")
    transcribe_service = None
    email_service = None
    llm_service = None

@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/upload', methods=['POST'])
def upload_and_transcribe():
    if not transcribe_service:
        return jsonify({"error": "Transcribe service not available"}), 500

    if 'image' not in request.files or 'audio' not in request.files:
        return jsonify({"error": "Missing image or audio file"}), 400
    
    image = request.files['image']
    audio = request.files['audio']

    if image.filename == '' or audio.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(image.filename, app.config['ALLOWED_IMAGE_EXTENSIONS']):
        return jsonify({"error": "Invalid image format"}), 400
        
    if not allowed_file(audio.filename, app.config['ALLOWED_AUDIO_EXTENSIONS']):
        return jsonify({"error": "Invalid audio format"}), 400

    try:
        # Save Files
        image_path = save_upload(image, app.config['UPLOAD_FOLDER'])
        audio_path = save_upload(audio, app.config['UPLOAD_FOLDER'])
        
        # Transcribe
        s3_key = transcribe_service.upload_audio(audio_path)
        transcription_job = transcribe_service.start_transcription_job(s3_key)
        transcript_text = transcribe_service.get_transcription_result(transcription_job)
        
        # Cleanup S3 audio immediately, keep local files for sending step
        transcribe_service.cleanup_s3_file(s3_key)
        
        return jsonify({
            "status": "success",
            "transcript": transcript_text,
            "image_path": image_path, # Return absolute path or token (in prod use tokens)
            "audio_path": audio_path
        }), 200

    except Exception as e:
        print(f"Upload error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/refine', methods=['POST'])
def refine_text():
    if not llm_service:
        return jsonify({"error": "LLM service not available"}), 500
        
    data = request.json
    text = data.get('text')
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
        
    try:
        refined_text = llm_service.refine_text(text)
        return jsonify({
            "status": "success",
            "refined_text": refined_text
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/send', methods=['POST'])
def send_email():
    if not email_service:
        return jsonify({"error": "Email service not available"}), 500
        
    data = request.json
    recipient = data.get('email')
    subject = data.get('subject')
    body_text = data.get('text')
    image_path = data.get('image_path')
    audio_path = data.get('audio_path') # Only needed for cleanup
    
    if not recipient or not validate_email(recipient):
        return jsonify({"error": "Invalid email address"}), 400
        
    if not image_path or not os.path.exists(image_path):
        return jsonify({"error": "Image file validation failed (expired?)"}), 400

    try:
        email_body = f"""
        MEP Agent Report
        ----------------
        
        {body_text}
        
        ----------------
        See attached image.
        """
        
        message_id = email_service.send_email(recipient, subject, email_body, image_path)
        
        return jsonify({
            "status": "success",
            "message": "Report sent successfully",
            "email_id": message_id
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
    finally:
        # Cleanup local files after attempting to send
        files_to_clean = []
        if image_path: files_to_clean.append(image_path)
        if audio_path: files_to_clean.append(audio_path)
        cleanup_files(files_to_clean)

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

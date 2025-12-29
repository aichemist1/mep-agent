import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-2')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
    SES_SENDER_EMAIL = os.getenv('SES_SENDER_EMAIL')
    SES_REGION = os.getenv('SES_REGION', 'us-east-2')

    AWS_BEDROCK_REGION = os.getenv('AWS_BEDROCK_REGION', 'us-east-2')
    LLM_MODEL_ID = os.getenv('LLM_MODEL_ID', 'amazon.nova-micro-v1:0')
    
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', 25))
    MAX_CONTENT_LENGTH = MAX_FILE_SIZE_MB * 1024 * 1024
    
    ALLOWED_IMAGE_EXTENSIONS = set(os.getenv('ALLOWED_IMAGE_EXTENSIONS', 'jpg,jpeg,png,gif').split(','))
    ALLOWED_AUDIO_EXTENSIONS = set(os.getenv('ALLOWED_AUDIO_EXTENSIONS', 'mp3,wav,m4a,ogg').split(','))
    
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    TEMP_FOLDER = os.path.join(os.getcwd(), 'temp')

    @staticmethod
    def validate():
        required = [
            'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 
            'S3_BUCKET_NAME', 'SES_SENDER_EMAIL'
        ]
        missing = [key for key in required if not getattr(Config, key)]
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")

import boto3
import time
import requests
import uuid
import os
from backend.config.settings import Config

class TranscribeService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
            region_name=Config.AWS_REGION
        )
        self.transcribe_client = boto3.client(
            'transcribe',
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
            region_name=Config.AWS_REGION
        )

    def upload_audio(self, file_path):
        """Upload audio file to S3."""
        file_name = os.path.basename(file_path)
        s3_key = f"temp_audio/{file_name}"
        try:
            self.s3_client.upload_file(file_path, Config.S3_BUCKET_NAME, s3_key)
            return s3_key
        except Exception as e:
            print(f"Error uploading to S3: {e}")
            raise

    def start_transcription_job(self, s3_key):
        """Start an AWS Transcribe job."""
        job_name = f"mep_agent_{uuid.uuid4()}"
        file_uri = f"s3://{Config.S3_BUCKET_NAME}/{s3_key}"
        
        try:
            self.transcribe_client.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': file_uri},
                MediaFormat=s3_key.split('.')[-1],
                LanguageCode='en-US'
            )
            return job_name
        except Exception as e:
            print(f"Error starting transcription job: {e}")
            raise

    def get_transcription_result(self, job_name):
        """Poll for completion and retrieve text."""
        max_retries = 60  # 5 minutes (5s interval)
        
        for _ in range(max_retries):
            status = self.transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
            job_status = status['TranscriptionJob']['TranscriptionJobStatus']
            
            if job_status == 'COMPLETED':
                uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
                response = requests.get(uri)
                data = response.json()
                return data['results']['transcripts'][0]['transcript']
            elif job_status == 'FAILED':
                raise Exception(f"Transcription job failed: {status['TranscriptionJob']['FailureReason']}")
            
            time.sleep(5)
            
        raise Exception("Transcription job timed out")

    def cleanup_s3_file(self, s3_key):
        """Delete file from S3."""
        try:
            self.s3_client.delete_object(Bucket=Config.S3_BUCKET_NAME, Key=s3_key)
        except Exception as e:
            print(f"Error deleting S3 file: {e}")

import boto3
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
from backend.config.settings import Config

class EmailService:
    def __init__(self):
        self.ses_client = boto3.client(
            'ses',
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
            region_name=Config.SES_REGION
        )

    def send_email(self, recipient, subject, body_text, image_path):
        """Send email with image attachment via SES."""
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = Config.SES_SENDER_EMAIL
        msg['To'] = recipient

        # Body
        msg.attach(MIMEText(body_text, "plain"))

        # Attachment
        if image_path and os.path.exists(image_path):
            file_name = os.path.basename(image_path)
            with open(image_path, "rb") as f:
                part = MIMEApplication(f.read())
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {file_name}",
                )
                msg.attach(part)

        try:
            response = self.ses_client.send_raw_email(
                Source=Config.SES_SENDER_EMAIL,
                Destinations=[recipient],
                RawMessage={"Data": msg.as_string()}
            )
            return response['MessageId']
        except ClientError as e:
            print(f"Error sending email: {e.response['Error']['Message']}")
            raise

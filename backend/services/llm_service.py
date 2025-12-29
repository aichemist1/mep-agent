import boto3
import json
from backend.config.settings import Config

class LLMService:
    def __init__(self):
        self.bedrock_client = boto3.client(
            service_name='bedrock-runtime',
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
            region_name=Config.AWS_BEDROCK_REGION
        )

    def refine_text(self, text, style="professional"):
        """
        Refine the input text using AWS Bedrock (Amazon Nova).
        """
        system_prompt = "You are a helpful assistant for a construction field professional. Refine the transcription into a clear, professional field report. Remove filler words. Fix grammar. Keep it concise."
        
        # Amazon Nova payload structure
        body = json.dumps({
            "system": [{"text": system_prompt}],
            "messages": [
                {
                    "role": "user", 
                    "content": [{"text": f"Original Text: \"{text}\"\n\nRefined Report:"}]
                }
            ],
            "inferenceConfig": {
                "maxTokens": 1000,
                "temperature": 0.5,
                "topP": 0.9
            }
        })

        try:
            response = self.bedrock_client.invoke_model(
                body=body,
                modelId=Config.LLM_MODEL_ID,
                accept='application/json',
                contentType='application/json'
            )
            
            response_body = json.loads(response.get('body').read())
            # Nova response structure matches the converse output structure inside 'output' usually, 
            # OR it returns a specific body. 
            # For Nova specifically: {"output": {"message": {"content": [{"text": "..."}]}}}
            
            return response_body['output']['message']['content'][0]['text']
            
        except Exception as e:
            print(f"LLM Error: {e}")
            raise e

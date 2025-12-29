import boto3
import os
from dotenv import load_dotenv

load_dotenv()

def list_available_models():
    region = os.getenv('AWS_BEDROCK_REGION', 'us-east-1')
    print(f"Checking Bedrock models in region: {region}")
    
    try:
        client = boto3.client(
            'bedrock',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=region
        )
        
        response = client.list_foundation_models(
            byProvider='Amazon',
            byOutputModality='TEXT'
        )
        
        print("\nAvailable Amazon Models:")
        found = False
        target_model = os.getenv('LLM_MODEL_ID', 'amazon.nova-micro-v1:0')
        
        for model in response['modelSummaries']:
            print(f"- {model['modelId']} (Status: {model.get('modelLifecycle', {}).get('status')})")
            if model['modelId'] == target_model:
                found = True
                
        print(f"\nTarget Model '{target_model}' found: {found}")
        
        if not found:
            print("\nIMPORTANT: You need to request access to this model in the AWS Console -> Bedrock -> Model access.")
            
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    list_available_models()

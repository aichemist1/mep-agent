# backend/main.py
from fastapi import FastAPI, UploadFile, File
import shutil
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from .MEP_PROMPT import MEP_SYSTEM_PROMPT # Import the prompt module

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()
os.makedirs("temp_uploads", exist_ok=True)

@app.get("/")
def read_root():
    return {"status": "MEP Agent Backend is running"}

@app.post("/process-audio")
async def process_audio(file: UploadFile = File(...)):
    file_location = f"temp_uploads/{file.filename}"

    try:
        # 1. Save and open the file
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)

        # 2. Transcribe Audio (Whisper)
        with open(file_location, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        raw_text = transcript.text

        # 3. Clean and Structure Data (GPT-4o)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": MEP_SYSTEM_PROMPT},
                {"role": "user", "content": f"Field Observation: {raw_text}"}
            ],
            response_format={"type": "json_object"}
        )

        # 4. Parse the structured JSON output
        rfi_payload = json.loads(response.choices[0].message.content)

        return {
            "status": "success",
            "message": "RFI Payload generated successfully.",
            "raw_transcription": raw_text,
            "rfi_data": rfi_payload
        }

    except Exception as e:
        print(f"An error occurred: {e}")
        return {"status": "error", "message": f"Processing failed: {e}"}

    finally:
        # 5. Cleanup the temporary file
        if os.path.exists(file_location):
            os.remove(file_location)

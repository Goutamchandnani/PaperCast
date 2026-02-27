from fastapi import APIRouter, File, UploadFile, BackgroundTasks, HTTPException, Form
from fastapi.responses import JSONResponse
import uuid
import os

from services.s3_service import S3Service
from services.pdf_service import PDFService
from services.gemini_service import GeminiService
from services.tts_service import TTSService

router = APIRouter()

# Initialize services
s3_service = S3Service()
pdf_service = PDFService()
gemini_service = GeminiService()
tts_service = TTSService()

# We could use a proper database, but for simplicity we'll store status in memory
podcast_jobs = {}

def process_podcast_background(job_id: str, file_path: str, language: str):
    try:
        podcast_jobs[job_id]["status"] = "extracting_text"
        podcast_jobs[job_id]["progress"] = 10
        
        # 1. Extract text
        text = pdf_service.extract_text(file_path)
        if not text:
            raise ValueError("No text extracted from PDF.")
            
        podcast_jobs[job_id]["status"] = "generating_script"
        podcast_jobs[job_id]["progress"] = 30
        
        # 2. Generate script using Gemini
        script = gemini_service.generate_podcast_script(text, language)
        
        podcast_jobs[job_id]["status"] = "generating_audio"
        podcast_jobs[job_id]["progress"] = 60
        
        # 3. Text to Speech
        audio_filename = f"{job_id}.mp3"
        audio_path = tts_service.generate_podcast_audio(script, audio_filename, language)
        
        podcast_jobs[job_id]["status"] = "uploading_audio"
        podcast_jobs[job_id]["progress"] = 90
        
        # 4. Upload to S3
        s3_object_name = f"podcasts/{audio_filename}"
        upload_success = s3_service.upload_file(audio_path, s3_object_name)
        
        if not upload_success:
            raise Exception("Failed to upload audio to S3")
            
        # 5. Generate Presigned URL
        url = s3_service.generate_presigned_url(s3_object_name)
        
        podcast_jobs[job_id]["status"] = "completed"
        podcast_jobs[job_id]["progress"] = 100
        podcast_jobs[job_id]["audio_url"] = url
        
    except Exception as e:
        print(f"Error processing job {job_id}: {e}")
        podcast_jobs[job_id]["status"] = "failed"
        podcast_jobs[job_id]["error"] = str(e)
    finally:
        # Cleanup PDF and temporary files
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        # Audio path cleanup should happen in tts_service, 
        # but the final merged audio can be deleted here
        try:
            if 'audio_path' in locals() and os.path.exists(audio_path):
                os.remove(audio_path)
        except:
            pass

@router.post("/generate")
async def generate_podcast(background_tasks: BackgroundTasks, file: UploadFile = File(...), language: str = Form("english")):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    job_id = str(uuid.uuid4())
    
    # Save the uploaded file temporarily
    temp_dir = os.path.join(os.getcwd(), "temp_pdf")
    os.makedirs(temp_dir, exist_ok=True)
    temp_file_path = os.path.join(temp_dir, f"{job_id}.pdf")
    
    with open(temp_file_path, "wb") as f:
        content = await file.read()
        f.write(content)
        
    # Optional: Upload raw PDF to S3 as well, though the user mostly just wants the output MP3.
    # We will skip uploading the raw PDF to S3 to save space/time, unless needed.
    
    podcast_jobs[job_id] = {
        "status": "pending",
        "progress": 0,
        "audio_url": None,
        "error": None
    }
    
    # Start background task
    background_tasks.add_task(process_podcast_background, job_id, temp_file_path, language)
    
    return {"job_id": job_id, "message": "Podcast generation started."}

@router.get("/status/{job_id}")
async def get_status(job_id: str):
    if job_id not in podcast_jobs:
        raise HTTPException(status_code=404, detail="Job not found.")
        
    return podcast_jobs[job_id]

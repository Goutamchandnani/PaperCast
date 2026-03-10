<div align="center">
  <img src="https://lucide.dev/icons/headphones.svg" alt="PaperCast Logo" width="80" height="80">
  <h1>PaperCast</h1>
  <p><strong>Turn complex research papers into engaging, two-host conversational podcasts.</strong></p>

  [![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen.svg)](https://paper-cast-weld.vercel.app/)
  
  [**Live Website: paper-cast-weld.vercel.app**](https://paper-cast-weld.vercel.app/)

  <br />
</div>

## 🎧 What is PaperCast? (The Non-Technical View)

Reading lengthy, jargon-filled academic research papers can be a chore. PaperCast is an AI-powered web tool that aims to solve this by turning dense PDFs into short, engaging 5-10 minute podcast audio tracks. 

Instead of staring at a screen, you simply:
1. **Upload** your target research paper (PDF).
2. **Select your preferred language** (English, Spanish, French, German, Hindi, Chinese, or Arabic).
3. **Listen!** 

The resulting podcast features two distinct AI voices:
- **The Host/Interviewer**: Guides the conversation, asks the questions you'd likely have, and keeps the energy up.
- **The Expert**: Breaks down the complex methodologies, jargon, and results into simple, everyday analogies.

**Perfect for:** Commutes, cardio workouts, walking the dog, or simply resting your eyes while staying up-to-date with your field.

---

## 🛠️ How it Works (The Technical View)

PaperCast uses a modern, decoupled architecture to securely and efficiently orchestrate several robust services.

### The Tech Stack
* **Frontend:** React 18, Vite, Vanilla CSS (Glass-morphic design), Axios.
* **Backend API:** FastAPI, Uvicorn (Python 3).
* **AI & Processing:** PDFPlumber, Google Gemini API (`gemini-2.5-flash`), Edge TTS (Neural Voices).
* **Storage:** Amazon S3 (via Boto3) for secure, ephemeral audio file delivery using pre-signed URLs.

### The Processing Pipeline (System Architecture)
When a user uploads a PDF from the React frontend, the request is intercepted by the FastAPI backend which immediately returns a `job_id`. The heavy lifting then happens asynchronously using FastAPI Background Tasks:

1. **Text Extraction (`pdf_service.py`):** The uploaded PDF is parsed using `pdfplumber` to extract the raw text content.
2. **Script Generation (`gemini_service.py`):** The extracted text is sent to the Google Gemini 2.5 Flash model alongside a highly-engineered prompt. The prompt instructs Gemini to act as a scriptwriter, translating the jargon into a two-person conversational dialogue (e.g., "Alex" as interviewer and "Jamie" as expert) translated entirely into the user's selected language.
3. **Audio Synthesis (Text-to-Speech) (`tts_service.py`):** The script is parsed line-by-line. Using `edge-tts`, the system dynamically assigns distinct, localized neural voices to each host (e.g., a male neural voice for Host 1, a female neural voice for Host 2). The audio chunks are generated asynchronously and concatenated into a single, unified MP3 file.
4. **Cloud Storage & Delivery (`s3_service.py`):** The final MP3 is securely uploaded to an Amazon S3 bucket. A temporary *pre-signed URL* is generated and served back to the React frontend (via its polling logic) so the user can stream the audio locally inline.

Because the system employs a background task and polling mechanism (`/api/podcast/status/{job_id}`), the UI remains responsive and provides real-time progress updates throughout the entire pipeline.

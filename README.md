# Document Intelligence System

An end-to-end document intelligence application that ingests documents, extracts and validates their content, generates LLM-based summaries and paraphrases, produces natural-sounding audio, and provides both Google Drive integration and a FastAPI web interface.

## Features

### Document Processing
- PDF, DOCX, TXT, XLSX, XLS, CSV, PPTX support
- Image/scanned document support
- OCR for scanned PDF pages and images using Tesseract
- Extraction of:
  - paragraphs
  - headings
  - bullets/lists
  - tables
- Document normalization into a common structure
- Document validation and extraction quality checks
- OCR confidence tracking
- Chunking of large documents for LLM processing

### AI Processing
- Local LLM summarization using Ollama and Llama 3.2 3B
- Point-wise factual summaries
- Summary validation against important source values
- Meaning-preserving paraphrasing
- Full-document text-to-speech
- Summary text-to-speech
- Speech pacing adjustments for more natural listening

### Google Drive
- Google OAuth authentication
- List supported documents
- Download normal files
- Export Google Docs, Sheets, and Slides
- Upload generated outputs back to Google Drive
- Per-document output folders
- Replacement of previous generated outputs

### Backend
- FastAPI REST API
- SQLite database
- Document CRUD operations
- Document reprocessing
- JWT authentication
- Protected document endpoints
- Password hashing with Argon2

### Frontend
- Browser-based user interface
- Login/logout
- JWT-based authenticated requests
- Document upload and processing
- Document listing and refresh
- Summary viewing
- Paraphrase viewing
- Full-document audio playback
- Summary audio playback
- Document reprocessing
- Document deletion

## Architecture

```text
                    Google Drive
                         |
                         v
                  File Download / Export
                         |
                         v
                  Document Parser
                         |
                  +------+------+
                  |             |
                  v             v
              Text/Table       OCR
                  |             |
                  +------+------+
                         |
                         v
                 Normalization
                         |
                         v
                    Validation
                         |
                         v
                     Chunking
                         |
              +----------+----------+
              |                     |
              v                     v
         Local LLM              TTS Engine
        (Ollama/Llama)         (Edge TTS)
              |                     |
        +-----+------+        +-----+------+
        |            |        |            |
        v            v        v            v
     Summary    Paraphrase  Full Doc     Summary
        |            |       Audio        Audio
        +------------+---------+------------+
                             |
                             v
                        SQLite + Files
                             |
                             v
                         FastAPI API
                             |
                             v
                       Web Frontend


Technology Stack
Component	            Technology
Language	            Python
API	                    FastAPI
Database	            SQLite
LLM	                    Ollama + Llama 3.2 3B
PDF                     processing	pypdf, pdfplumber, PyMuPDF
DOCX                    processing	python-docx
Spreadsheet             processing	pandas, openpyxl
PPTX                    processing	python-pptx
OCR	                    Tesseract + pytesseract
Image processing	    Pillow
TTS	                    Edge TTS
Authentication	        JWT + Argon2
Frontend	            HTML, CSS, JavaScript
Cloud storage	        Google Drive API

## Environment Setup

This project includes a setup script that prepares the local environment for the Document Intelligence System.

### Requirements

- Windows 10/11
- Python 3.13+
- Git
- Ollama installed and available in the system PATH
- Google Drive credentials for Google Drive integration

### Automated Setup

From the project root, activate the virtual environment and run:

```powershell
python scripts/setup_environment.py
```


## Running the Application

### Local Application

Activate the virtual environment and run:

```powershell
uvicorn app.main:app --reload

## Project Structure

document-intelligence-system/
│
├── app/
│   ├── api/              # Authentication API
│   ├── services/         # Parsing, OCR, LLM, TTS, Drive, etc.
│   ├── database.py       # SQLite database
│   └── main.py           # FastAPI application
│
├── frontend/             # HTML, CSS and JavaScript UI
├── tests/                # Tests
├── scripts/              # Environment setup scripts
│   └── setup_environment.py
├── data/                 # Local input and generated files
├── credentials/          # Google credentials (not committed)
├── .env                  # Environment variables (not committed)
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
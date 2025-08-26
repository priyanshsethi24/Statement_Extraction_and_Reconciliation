# Statement Extraction and Reconciliation

This project is an **LLM-driven hybrid entity extraction system** built using FastAPI.  
It combines **Dolphin architecture** for accurate table extraction with an **external document extraction API** for non-table entities.  
The system is designed to process financial and business documents, extract structured data, and reconcile results into a unified JSON response.

---

## Features
- Table extraction powered by Dolphin architecture (OCR + LLM pipeline).
- Non-table entity extraction via external API.
- Direct S3 integration with versioning support.
- Token usage tracking (input, output, total).
- Automatic cleanup of temporary files.
- Scalable FastAPI microservice architecture.

---

## Project Structure
- `src/detector.py` → Main extraction service.
- `common/` → Logging and S3 helpers.
- `scripts/llm_utils.py` → LLM utility functions.
- `config/Dolphin.yaml` → Dolphin model configuration.
- `demo_page.py` → Dolphin entrypoint for PDF parsing.

---



## Requirements

Python 3.9+
FastAPI
Uvicorn
boto3
requests
OpenAI (for LLM calls)
opencv-python (if OCR fallback needed)

## Install all dependencies:

pip install -r requirements.txt

## Running the Service

Set up required environment variables:
DOC_EXTRACTOR_URL → External API endpoint
AWS credentials for S3 access

Start the FastAPI server:
uvicorn src.detector:router --reload


## Send a request to:

http://127.0.0.1:8000/extract_entity

## Future Improvements

Async subprocess calls for Dolphin.
Streaming responses for large PDFs.
Entity validation using regex/schema.
Caching layer for previously processed documents.

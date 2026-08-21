# AI-Based CV Parsing System

This project is being structured as a scalable AI-based CV parsing system for extracting structured information from resumes and CVs.

## Project Goals

- Process CVs from PDF, DOCX, and scanned image sources
- Detect whether a document is text-based or scanned
- Extract structured fields such as name, contact details, experience, education, skills, and certifications
- Export parsed data as JSON and CSV for downstream use
- Provide a modular foundation that can later evolve into an API, database-backed service, or GUI application

## Proposed Project Structure

- `app/` contains application entry points and future interface layers
- `src/ingestion/` handles file loading and validation
- `src/extraction/` manages PDF extraction and OCR
- `src/preprocessing/` cleans and normalizes text
- `src/nlp/` performs extraction and language processing
- `src/validation/` validates and scores parsed results
- `src/export/` writes JSON, CSV, or database outputs
- `src/common/` stores shared utilities, configuration, and logging
- `src/pipeline/` orchestrates the full processing workflow
- `data/` stores input files, sample documents, and generated outputs
- `tests/` contains unit and integration tests
- `docs/` stores architecture and implementation notes

## Installation

1. Open a terminal in the project root.
2. Create and activate a Python virtual environment (recommended):
   - `python -m venv .venv`
   - `.venv\Scripts\activate`
3. Install the required dependencies:
   - `pip install -r requirements.txt`

## Running the Project

The initial scaffold is in place. The Python implementation modules will be added after confirmation.

To run the project once the main processing script is available:

```bash
python main.py
```

## Notes

- `pypdf` and `pdfplumber` are intended for extracting text from standard PDFs.
- `pytesseract`, `pdf2image`, and `Pillow` support OCR for scanned documents.
- `spacy` and `pydantic` provide the foundation for NLP processing and schema validation.
- `pandas` is used for tabular export, while `fastapi` and `sqlalchemy` prepare the system for future API and database integration.

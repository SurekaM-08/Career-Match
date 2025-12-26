# Smart Resume Job Finder — Mini Project (ZIP package)

## System Requirements

### Hardware Specification
- **PROCESSOR**: Intel Core i3 or equivalent (minimum; i5 recommended for faster ML processing with sentence-transformers)
- **MEMORY (RAM)**: 4 GB (minimum; 8 GB recommended for handling embeddings and vector computations)
- **STORAGE**: 10 GB HDD/SSD (minimum; additional space for uploaded resumes and job data)
- **DISPLAY**: 1024×768 resolution (minimum)
- **NETWORK**: Minimum 5 Mbps speed for web access and optional job scraping

### Software Specification
- **OPERATING SYSTEM**: Windows 11
- **FRONT END**: HTML, CSS, JavaScript
- **BACK END**: Python (Developed with Flask framework)
- **DATABASE**: SQLite
- **SOFTWARE**: Python 3.x, pip (for dependency management)
- **BROWSER COMPATIBILITY**: Google Chrome, Mozilla Firefox, Microsoft Edge, Safari

## What is included
- `app.py` — Flask backend (serves frontend and `/upload` endpoint)
- `index.html` — Colorful multi-step frontend (blue theme) that uploads resumes and shows matches
- `static/styles.css` — Styling (blue theme)
- `seed_jobs.py` — Script to create `jobs.db` with sample job postings
— Optional Selenium scraper skeleton (use responsibly)
- `requirements.txt` — Python dependencies
- `README.md` — This file

## Quick setup (Windows PowerShell)
1. Create & activate virtualenv
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```
> If `Activate.ps1` is blocked, run:
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` then activate.

2. Seed the database:
```powershell
python seed_jobs.py
```
This creates `jobs.db` with sample jobs.

3. Run the Flask app:
```powershell
python app.py
```
Open: http://127.0.0.1:5000/

4. Paste or upload your resume (PDF/DOCX/TXT) and click **Analyze Resume**.
The app will show suggested role and matches. Use the LinkedIn/Indeed/Naukri buttons to open portal searches.

## Notes & troubleshooting
- Sentence-Transformers requires `torch`. If installing `sentence-transformers` fails, install CPU-only torch first:
```powershell
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install sentence-transformers
```
- Model download may take time the first run (embedding model). It is normal.
- Scraping job portals may violate Terms of Service. Prefer opening search URLs instead (this app uses search URLs).

## System Implementation and Maintenance
### 6.1 System Testing
Unit Testing:
Each individual module was tested separately to verify its correctness. For example, the resume text extraction module was tested to ensure accurate parsing from PDF, DOCX, and TXT files, and the job matching module was tested for correct similarity scoring using embeddings.

Integration Testing:
After unit testing, modules were integrated and tested together to ensure they work seamlessly. For instance, after resume upload and text extraction, the embedding generation and job matching modules should correctly process and display results without errors.

Functional Testing:
All supported features were tested under various conditions, including different resume formats, file sizes, and job database sizes, to validate the system’s robustness.

User Acceptance Testing (UAT):
Multiple users tested the application in real-world scenarios to assess usability, responsiveness, and overall satisfaction. Feedback was collected to identify areas for improvement, such as UI enhancements and faster processing.

Performance Testing:
The system’s response time from resume upload to result display was measured. Code optimizations were made to reduce latency, such as efficient embedding computations and database queries, to improve real-time performance.

## Next improvements you can ask for
- Resume parsing (skills/education extraction)
- Highlight matching keywords (explainability)
- React frontend with prettier UI
- Persistent precomputed embeddings & FAISS for large scale
- Dockerfile and deployment guide

If you want, I can now convert this folder into a downloadable ZIP for you or customize the UI more (colors, logos, pages).

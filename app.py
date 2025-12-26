
from flask import Flask, request, jsonify, send_from_directory
import os, sqlite3, uuid
from werkzeug.utils import secure_filename
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
try:
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None
    Image = None
try:
    from sentence_transformers import SentenceTransformer
    EMBED_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    EMBED_MODEL = None
    print('Warning: SentenceTransformer not available at import time. Install sentence-transformers and torch to enable semantic embeddings. Error:', e)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
DB_PATH = os.path.join(os.path.dirname(__file__), 'jobs.db')

ALLOWED_EXT = {'pdf','docx','txt','jpg','jpeg','png'}

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB

def get_db_jobs():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, source, title, company, location, description, url FROM jobs')
    rows = c.fetchall()
    conn.close()
    jobs = []
    for r in rows:
        jobs.append({'id': r[0], 'source': r[1], 'title': r[2], 'company': r[3], 'location': r[4], 'description': r[5], 'url': r[6]})
    return jobs

def extract_text_from_file(path, filename):
    name = filename.lower()
    try:
        if name.endswith('.pdf'):
            import pdfplumber
            text = []
            with pdfplumber.open(path) as pdf:
                for p in pdf.pages:
                    text.append(p.extract_text() or '')
            return '\n'.join(text)
        elif name.endswith('.docx'):
            import docx
            doc = docx.Document(path)
            return '\n'.join([p.text for p in doc.paragraphs])
        elif name.endswith('.txt'):
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        elif name.endswith(('.jpg', '.jpeg', '.png')):
            if pytesseract and Image:
                img = Image.open(path)
                return pytesseract.image_to_string(img)
            else:
                print('OCR not available: pytesseract or PIL not installed')
                return ''
    except Exception as e:
        print('Error extracting:', e)
    return ''

def preprocess(text):
    if not text: return ''
    return ' '.join(text.split())

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/upload', methods=['POST'])
def upload_resume():
    resume_text = ''
    if 'file' in request.files and request.files['file'].filename != '':
        f = request.files['file']
        filename = secure_filename(f.filename)
        if '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXT:
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4().hex}_{filename}")
            f.save(save_path)
            resume_text = extract_text_from_file(save_path, filename)
        else:
            return jsonify({'error': 'unsupported file type'}), 400
    else:
        data = request.form.to_dict() or request.get_json(silent=True) or {}
        resume_text = data.get('resume_text', '')

    resume_text = preprocess(resume_text)
    if not resume_text:
        return jsonify({'error':'empty resume text'}), 400

    jobs = get_db_jobs()
    if not jobs:
        return jsonify({'error':'no jobs available in DB. Run seed_jobs.py'}), 404

    job_texts = []
    job_titles = []
    for j in jobs:
        combined = ((j.get('title') or '') + ' ' + (j.get('company') or '') + ' ' + (j.get('description') or ''))
        job_texts.append(preprocess(combined))
        job_titles.append(j.get('title') or '')

    try:
        vect = TfidfVectorizer(max_features=20000, stop_words='english')
        tfidf_all = vect.fit_transform(job_texts + [resume_text])
        resume_vec = tfidf_all[-1]
        job_tfidf = tfidf_all[:-1]
        tfidf_sim = cosine_similarity(resume_vec, job_tfidf).flatten()
    except Exception as e:
        print('TF-IDF error:', e)
        tfidf_sim = np.zeros(len(job_texts))

    if EMBED_MODEL is not None:
        try:
            emb_all = EMBED_MODEL.encode(job_texts + [resume_text], convert_to_numpy=True, show_progress_bar=False)
            resume_emb = emb_all[-1]
            job_embs = emb_all[:-1]
            def cos_sim(a,b):
                if np.linalg.norm(a)==0 or np.linalg.norm(b)==0: return 0.0
                return float(np.dot(a/np.linalg.norm(a), b/np.linalg.norm(b)))
            emb_sim = np.array([cos_sim(resume_emb, e) for e in job_embs])
        except Exception as e:
            print('Embedding error:', e)
            emb_sim = np.zeros(len(job_texts))
    else:
        emb_sim = np.zeros(len(job_texts))

    combined = 0.6 * emb_sim + 0.4 * tfidf_sim
    if combined.size == 0:
        combined_norm = np.array([])
    else:
        combined_norm = 100 * (combined - combined.min()) / (combined.max() - combined.min() + 1e-8)

    suggested_role = ''
    suggested_confidence = 0.0
    try:
        if EMBED_MODEL is not None:
            title_embs = EMBED_MODEL.encode(job_titles, convert_to_numpy=True, show_progress_bar=False)
            resume_emb = EMBED_MODEL.encode([resume_text], convert_to_numpy=True, show_progress_bar=False)[0]
            sims = np.array([float(np.dot(resume_emb/np.linalg.norm(resume_emb), t/np.linalg.norm(t))) if np.linalg.norm(t)!=0 else 0.0 for t in title_embs])
            best_idx = int(np.argmax(sims))
            suggested_role = job_titles[best_idx]
            suggested_confidence = float(sims[best_idx])
        else:
            best_idx = int(np.argmax(combined_norm))
            suggested_role = job_titles[best_idx]
            suggested_confidence = float(combined_norm[best_idx]/100)
    except Exception as e:
        print('Suggested role error:', e)

    idxs = np.argsort(-combined_norm)[:10] if combined_norm.size>0 else []
    results = []
    for idx in idxs:
        j = jobs[int(idx)]
        score = float(combined_norm[int(idx)]) if combined_norm.size>0 else 0.0
        q = (j.get('title') or '').replace(' ', '+')
        linkedin = f"https://www.linkedin.com/jobs/search/?keywords={q}"
        indeed = f"https://in.indeed.com/jobs?q={q}"
        naukri = f"https://www.naukri.com/{q}-jobs"
        results.append({'job_id': j.get('id'), 'title': j.get('title'), 'company': j.get('company'), 'location': j.get('location'), 'snippet': (j.get('description') or '')[:400], 'url': j.get('url'), 'score': round(score,2), 'search_urls': {'linkedin': linkedin, 'indeed': indeed, 'naukri': naukri}})

    return jsonify({'suggested_role': suggested_role, 'suggested_confidence': round(suggested_confidence,3), 'extracted_text': resume_text[:5000], 'results': results})

@app.route('/static/<path:fname>')
def static_files(fname):
    return send_from_directory('static', fname)

if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        print('jobs.db not found. Run seed_jobs.py to create a database with sample jobs.')
    app.run(host='0.0.0.0', port=5000, debug=True)

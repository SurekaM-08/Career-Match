# seed_jobs.py -- create jobs.db with sample jobs for demo
import sqlite3, os
DB_PATH = os.path.join(os.path.dirname(__file__), 'jobs.db')
jobs = [
  ('indeed', 'Machine Learning Engineer', 'ABC Corp', 'Bengaluru', 'Develop machine learning models, Python, scikit-learn, PyTorch, model deployment', 'https://in.indeed.com/viewjob?jk=abc1'),
  ('naukri', 'Data Scientist', 'XYZ Analytics', 'Hyderabad', 'Data analysis, statistics, Python, SQL, ML pipelines and dashboards', 'https://www.naukri.com/example1'),
  ('linkedin', 'Software Engineer - ML', 'InnovateAI', 'Remote', 'Build ML infrastructure, model deployment, Docker, AWS, TensorFlow', 'https://www.linkedin.com/jobs/view/example1'),
  ('indeed', 'NLP Engineer', 'LangTech', 'Bengaluru', 'NLP, transformers, huggingface, Python, tokenization', 'https://in.indeed.com/viewjob?jk=abc2'),
  ('naukri', 'Business Analyst', 'MarketPulse', 'Chennai', 'Business analysis, SQL, Excel, data visualization, stakeholder communication', 'https://www.naukri.com/example2'),
  ('linkedin', 'DevOps Engineer', 'CloudWorks', 'Pune', 'CI/CD, Docker, Kubernetes, monitoring, AWS', 'https://www.linkedin.com/jobs/view/example2'),
  ('indeed', 'AI Researcher', 'DeepThink', 'Remote', 'Research on ML algorithms, Python, PyTorch, publications', 'https://in.indeed.com/viewjob?jk=abc3'),
  ('naukri', 'Software Developer', 'NextGen Software', 'Bengaluru', 'Backend development, Java, Spring, REST APIs', 'https://www.naukri.com/example3')
]
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS jobs (id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT, title TEXT, company TEXT, location TEXT, description TEXT, url TEXT, scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
for j in jobs:
    c.execute('INSERT INTO_jobs (source,title,company,location,description,url) VALUES (?,?,?,?,?,?)' if False else 'INSERT INTO jobs (source,title,company,location,description,url) VALUES (?,?,?,?,?,?)', j)
conn.commit()
conn.close()
print('Seeded jobs into', DB_PATH)
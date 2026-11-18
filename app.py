import sqlite3
from pathlib import Path
import streamlit as st
from engine import extract_skills, parse_resume, rank_jobs, answer_question

DB = Path(__file__).parent / 'data' / 'jobs.db'
DB.parent.mkdir(exist_ok=True)

def connect():
    db = sqlite3.connect(DB)
    db.execute('CREATE TABLE IF NOT EXISTS jobs (id INTEGER PRIMARY KEY, title TEXT NOT NULL, company TEXT NOT NULL, skills TEXT NOT NULL, description TEXT NOT NULL)')
    if not db.execute('SELECT COUNT(*) FROM jobs').fetchone()[0]:
        db.executemany('INSERT INTO jobs(title,company,skills,description) VALUES (?,?,?,?)', [
            ('Python Developer', 'Demo Tech', 'python, sql, git, flask', 'Develop Python applications and APIs, use SQL databases and Git for collaboration.'),
            ('Data Analyst', 'Demo Analytics', 'python, sql, excel, power bi, statistics', 'Analyze data, build dashboards, clean datasets, and report insights.'),
            ('Machine Learning Intern', 'Demo AI Lab', 'python, pandas, numpy, scikit-learn, machine learning', 'Prepare datasets, train ML models, and evaluate predictive performance.'),
            ('Frontend Developer', 'Demo Web Studio', 'javascript, react, html, css, git', 'Build accessible responsive user interfaces with React and JavaScript.'),
            ('QA Automation Engineer', 'Demo Quality', 'python, testing, automation, selenium, git', 'Design automated tests, report bugs, and maintain regression suites.')
        ])
        db.commit()
    return db

st.set_page_config(page_title='Resume–Job Matching Chatbot', page_icon='🎯', layout='wide')
st.title('🎯 AI-Driven Resume–Job Vacancy Matching Chatbot')
st.caption('College prototype · local NLP · illustrative job listings · no external AI API')
with connect() as db:
    with st.sidebar:
        st.header('Add a job')
        with st.form('new_job'):
            title = st.text_input('Job title')
            company = st.text_input('Company')
            skills = st.text_input('Required skills (comma-separated)')
            description = st.text_area('Job description')
            submitted = st.form_submit_button('Add job')
        if submitted:
            if all(x.strip() for x in [title, company, skills, description]):
                db.execute('INSERT INTO jobs(title,company,skills,description) VALUES (?,?,?,?)', (title.strip(),company.strip(),skills.strip(),description.strip()))
                db.commit()
                st.success('Job added')
            else:
                st.error('All job fields are required')
    rows = db.execute('SELECT id,title,company,skills,description FROM jobs ORDER BY id').fetchall()
    jobs = [dict(zip(['id','title','company','skills','description'], r)) for r in rows]

uploaded = st.file_uploader('Upload your resume', type=['pdf','docx'], help='Maximum 5 MB. Text-based PDFs only.')
if uploaded:
    try:
        resume = parse_resume(uploaded)
        skills = extract_skills(resume)
        ranked = rank_jobs(resume, jobs)
        st.subheader('Detected skills')
        st.write(', '.join(skills) if skills else 'No skills detected from the current dictionary.')
        st.subheader('Recommended jobs')
        for job in ranked:
            with st.expander(f"{job['title']} — {job['company']} · {job['score']}%", expanded=job == ranked[0]):
                st.write(job['description'])
                st.write('**Matched skills:**', ', '.join(job['matched']) or 'None detected')
                st.write('**Missing from resume:**', ', '.join(job['missing']) or 'None detected')
                st.caption('Score is a heuristic, not a hiring probability or eligibility decision.')
        st.subheader('💬 Career guidance chatbot')
        if 'messages' not in st.session_state or st.session_state.get('resume_name') != uploaded.name:
            st.session_state.messages = []
            st.session_state.resume_name = uploaded.name
        for message in st.session_state.messages:
            with st.chat_message(message['role']):
                st.markdown(message['content'])
        if prompt := st.chat_input('Ask about your job matches or skill gaps'):
            st.session_state.messages.append({'role':'user','content':prompt})
            with st.chat_message('user'):
                st.write(prompt)
            response = answer_question(prompt, ranked, skills)
            st.session_state.messages.append({'role':'assistant','content':response})
            with st.chat_message('assistant'):
                st.markdown(response)
    except Exception as exc:
        st.error(f'Unable to process resume: {exc}')
else:
    st.info('Upload a resume to see matching jobs and chat with the assistant.')

from engine import extract_skills, rank_jobs, answer_question

def test_skill_boundaries():
    assert extract_skills('Python, SQL, React') == ['python', 'react', 'sql']

def test_ranking():
    jobs = [{'title':'Python Developer','company':'Demo','skills':'python, sql','description':'Build Python applications using SQL'}, {'title':'Frontend','company':'Demo','skills':'react, css','description':'Build interfaces with React and CSS'}]
    ranked = rank_jobs('Python SQL developer building applications', jobs)
    assert ranked[0]['title'] == 'Python Developer'
    assert ranked[0]['missing'] == []
    assert 'Python Developer' in answer_question('best job', ranked, ['python','sql'])

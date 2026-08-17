from app import app


def test_index_page():
    client = app.test_client()
    r = client.get('/')
    assert r.status_code == 200
    assert b'Welcome' in r.data


def test_dashboard_requires_login():
    client = app.test_client()
    r = client.get('/dashboard', follow_redirects=False)
    # should redirect to login
    assert r.status_code in (302, 301)

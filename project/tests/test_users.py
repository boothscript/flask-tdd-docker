import json

from project.api.models import User


def test_add_user(test_app, test_database):
    client = test_app.test_client()
    resp = client.post('/users', data=json.dumps(
        {'username': 'micheal', 'email': 'micheal@testdriven.io'}), content_type='application/json')
    data = json.loads(resp.data.decode())
    assert resp.status_code == 201
    assert 'micheal@testdriven.io was added!' in data['message']


def test_add_user_invalid_json(test_app, test_database):
    client = test_app.test_client()
    resp = client.post(
        '/users',
        data=json.dumps({}),
        content_type='application/json',
    )
    data = json.loads(resp.data.decode())
    assert resp.status_code == 400
    assert 'Input payload validation failed' in data['message']


def test_add_user_invalid_json_keys(test_app, test_database):
    client = test_app.test_client()
    resp = client.post('/users', data=json.dumps({'email': 'micheal@testdriven.io'}),
                       content_type='application/json')
    data = json.loads(resp.data.decode())
    assert resp.status_code == 400
    assert 'Input payload validation failed' in data['message']


def test_add_user_duplicate_email(test_app, test_database):
    client = test_app.test_client()
    client.post('/users', data=json.dumps({'username': 'micheal', 'email': 'micheal@testdriven.io'}),
                content_type='application/json')
    resp = client.post('/users', data=json.dumps({'username': 'micheal', 'email': 'micheal@testdriven.io'}),
                       content_type='application/json')
    data = json.loads(resp.data.decode())
    assert resp.status_code == 400
    assert 'Sorry, That email allready exists' in data['message']


def test_single_user(test_app, test_database, add_user):
    user = add_user(username='jeff', email='jeff@testdriven.io')
    client = test_app.test_client()
    resp = client.get(f'/users/{user.id}')
    data = json.loads(resp.data.decode())
    assert resp.status_code == 200
    assert 'jeff' in data['username']
    assert 'jeff@testdriven.io' in data['email']


def test_single_user_incorrect_id(test_app, test_database):
    client = test_app.test_client()
    resp = client.get('/users/999')
    data = json.loads(resp.data.decode())
    print(data)
    assert resp.status_code == 404
    assert 'User 999 does not exist' in data['message']


def test_all_users(test_app, test_database, add_user):
    test_database.session.query(User).delete()
    add_user('micheal', 'micheal@mherman.org')
    add_user('fletcher', 'fletcher@notreal.com')
    client = test_app.test_client()
    resp = client.get('/users')
    data = json.loads(resp.data.decode())
    assert resp.status_code == 200
    assert len(data) == 2
    assert 'micheal' in data[0]['username']
    assert 'micheal@mherman.org' in data[0]['email']
    assert 'fletcher' in data[1]['username']
    assert 'fletcher@notreal.com' in data[1]['email']

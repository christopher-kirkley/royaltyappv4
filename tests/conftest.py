import pytest
from royaltyapp import create_app
from royaltyapp.models import insert_initial_values

@pytest.fixture(scope='module')
def flask_app():
    flask_app = create_app('config.TestConfig')
    yield flask_app

@pytest.fixture(scope='module')
def test_client(flask_app):

    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = flask_app.test_client()

    # Establish an application context before running the tests.
    ctx = flask_app.app_context()
    ctx.push()
    
    yield testing_client  # this is where the testing happens!

    ctx.pop()

@pytest.fixture
def db(flask_app):
    from royaltyapp.models import db
    with flask_app.app_context():
        db.reflect()
        db.drop_all()
        db.create_all()
    insert_initial_values(db)
    yield db
    db.session.remove()
    db.reflect()
    db.drop_all()
        
    


import pytest
from royaltyapp import create_app
from royaltyapp.models import db

@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app('config.TestConfig')

    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = flask_app.test_client()

    # Establish an application context before running the tests.
    ctx = flask_app.app_context()
    ctx.push()
    

    yield testing_client  # this is where the testing happens!

    db.session.remove()
    db.drop_all()
    

    ctx.pop()


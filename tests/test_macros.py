import pytest
import responses
from urlobject import URLObject
from flask import Flask
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer import OAuth2ConsumerBlueprint
from flask_dance.consumer.backend import MemoryBackend
from macros.models import User, Macro
from macros.extensions import db


# OAUTH TESTS

def test_blueprint_factory():
    google_bp = make_google_blueprint(
        client_id="foo",
        client_secret="bar",
        redirect_to="index",
    )
    assert isinstance(google_bp, OAuth2ConsumerBlueprint)
    assert google_bp.session.scope == ["profile"]
    assert google_bp.session.base_url == "https://www.googleapis.com/"
    assert google_bp.session.client_id == "foo"
    assert google_bp.client_secret == "bar"
    assert google_bp.authorization_url == "https://accounts.google.com/o/oauth2/auth"
    assert google_bp.token_url == "https://accounts.google.com/o/oauth2/token"


def test_load_from_config():
    app = Flask(__name__)
    app.secret_key = "anything"
    app.config["GOOGLE_OAUTH_CLIENT_ID"] = "foo"
    app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = "bar"
    google_bp = make_google_blueprint(redirect_to="index")
    app.register_blueprint(google_bp)

    resp = app.test_client().get("/google")
    url = resp.headers["Location"]
    client_id = URLObject(url).query.dict.get("client_id")
    assert client_id == "foo"


def test_blueprint_factory_scope():
    google_bp = make_google_blueprint(
        client_id="foo",
        client_secret="bar",
        scope="customscope",
        redirect_to="index",
    )
    assert google_bp.session.scope == "customscope"


@responses.activate
def test_context_local():
    responses.add(responses.GET, "https://google.com")

    # set up two apps with two different set of auth tokens
    app1 = Flask(__name__)
    goog_bp1 = make_google_blueprint(
        "foo1", "bar1", redirect_to="url1",
        backend=MemoryBackend({"access_token": "app1"}),
    )
    app1.register_blueprint(goog_bp1)

    app2 = Flask(__name__)
    goog_bp2 = make_google_blueprint(
        "foo2", "bar2", redirect_to="url2",
        backend=MemoryBackend({"access_token": "app2"}),
    )
    app2.register_blueprint(goog_bp2)

    # outside of a request context, referencing functions on the `google` object
    # will raise an exception
    with pytest.raises(RuntimeError):
        google.get("https://github.com")

    # inside of a request context, `google` should be a proxy to the correct
    # blueprint session
    with app1.test_request_context("/"):
        app1.preprocess_request()
        google.get("https://google.com")
        request = responses.calls[0].request
        assert request.headers["Authorization"] == "Bearer app1"

    with app2.test_request_context("/"):
        app2.preprocess_request()
        google.get("https://google.com")
        request = responses.calls[1].request
        assert request.headers["Authorization"] == "Bearer app2"


def test_offline():
    app = Flask(__name__)
    app.secret_key = "backups"
    goog_bp = make_google_blueprint("foo", "bar", offline=True)
    app.register_blueprint(goog_bp)

    with app.test_client() as client:
        resp = client.get(
            "/google",
            base_url="https://a.b.c",
            follow_redirects=False,
        )
    # check that there is a `access_type=offline` query param in the redirect URL
    assert resp.status_code == 302
    location = URLObject(resp.headers["Location"])
    assert location.query_dict["access_type"] == "offline"


def test_offline_reprompt():
    app = Flask(__name__)
    app.secret_key = "backups"
    goog_bp = make_google_blueprint(
        "foo", "bar", offline=True, reprompt_consent=True,
    )
    app.register_blueprint(goog_bp)

    with app.test_client() as client:
        resp = client.get(
            "/google",
            base_url="https://a.b.c",
            follow_redirects=False,
        )
    assert resp.status_code == 302
    location = URLObject(resp.headers["Location"])
    assert location.query_dict["access_type"] == "offline"
    assert location.query_dict["approval_prompt"] == "force"


# Model Tests

# FIXME: add session data as macro_data/user_data


def test_macro_model(macro_data):
    macros = Macro.query.all()
    assert len(macros) == len(macro_data)


def test_user_model(user_data):
    users = User.query.all()
    assert len(users) == len(user_data)


# DB Connection tests

# FIXME: add postgres values, fix create app function


def create_app(package_name, config, override_config_func=None):
    """
    Flask application factory to configure an application for a REST api. An
    app from this factory will accept `dict` or (`dict`, `int`) as a return
    value and serialize them using JSON. Factory also configures error handlers
    for all common error status codes and unexpected applications to return
    a JSON error instead of the default html one.
    """
    app = Flask(package_name)
    app.config.from_mapping(config)

    if callable(override_config_func):
        override_config_func(app)

    register_blueprints(app)
    register_error_handlers(app)
    register_extensions(app)
    register_hooks(app)
    register_sentry(app)
    return app


TESTDB = 'test_project.db'
TESTDB_PATH = "/opt/project/data/{}".format(TESTDB)
TEST_DATABASE_URI = 'sqlite:///' + TESTDB_PATH


# TEST_DATABASE_URI = "postgresql://macros:macros@localhost:5432/macros_test"


@pytest.fixture(scope='session')
def app(request):
    """Session-wide test `Flask` application."""
    settings_override = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': TEST_DATABASE_URI
    }
    app = create_app(__name__, settings_override)

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture(scope='session')
def db(app, request):
    """Session-wide test database."""
    if os.path.exists(TESTDB_PATH):
        os.unlink(TESTDB_PATH)

    def teardown():
        _db.drop_all()
        os.unlink(TESTDB_PATH)

    _db.app = app
    _db.create_all()

    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope='function')
def session(db, request):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session

# New macro additions tests:

"""
Creates a blueprint for oauth2 with Google.

"""
from macros import app
from flask_dance.contrib.google import make_google_blueprint

blueprint = make_google_blueprint(
    scope=["profile", "email"],
    client_id=app.config['GOOGLE_OAUTH_CLIENT_ID'],
    client_secret=app.config['GOOGLE_OAUTH_CLIENT_SECRET']
)

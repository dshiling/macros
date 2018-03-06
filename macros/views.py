from flask import render_template, request, redirect, url_for
from sqlalchemy import or_
from macros import app
from macros.oauth.views import blueprint
from flask_dance.contrib.google import google
from macros.models import User, Macro
from werkzeug.exceptions import Unauthorized


app.register_blueprint(blueprint, url_prefix="/login")


def get_oauth_info():

    # method for getting current_user info from google/ouath for use in other views

    resp = google.get("/oauth2/v2/userinfo").json()

    email = resp['email']
    username = (resp['name'][0] + resp['family_name']).lower()
    message = "Logged in as: {}".format(username)
    picture = resp['picture']

    current_user = {'email': email, 'username': username, 'message': message, 'picture': picture}

    return current_user


@app.route('/')
def index():

    # limits access to just t&s/legal group after oauth. Gets users in db, compares to current user from oauth info

    if not google.authorized:
        return redirect(url_for("google.login"))

    current_user = get_oauth_info()

    emails = [user.email for user in User.query.all()]

    if current_user['email'] in emails:
        results = Macro.query.all()
        return render_template('index.html', results=results, message=current_user['message'],
                               picture=current_user['picture'])
    else:
        raise Unauthorized('Contact the admin for permissions.')


@app.route('/search', methods=['GET', 'POST'])
def search():
    if not google.authorized:
        raise Unauthorized('You must be authenticated')

    if request.method == 'POST':
        return redirect((url_for('search_results', query=request.form['search'])))
    else:
        return redirect((url_for('index')))


@app.route('/search_results/<query>')
def search_results(query):
    if not google.authorized:
        raise Unauthorized('You must be authenticated')

    message = get_oauth_info()['message']
    picture = get_oauth_info()['picture']

    results = Macro.query.filter(
                or_(
                    Macro.title.ilike('%' + query + '%'),
                    Macro.content.ilike('%' + query + '%')
                )
                ).all()

    return render_template('search_results.html', query=query, results=results, message=message, picture=picture)

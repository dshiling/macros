# Macros

A simple [Flask](http://flask.pocoo.org/) app for finding and tracking my common language snippets.

Far from convention and far from finished. All comments/suggestions/personal criticism welcomed.

## Development


### Setup

#### 1) Environment

```bash
git clone
cd macros

# Creates a virtual environment with pyenv
pyenv virtualenv macros 3.X.X
pyenv activate macros

# Install dependencies
pip install -r requirements.txt
```

#### 2) Configuration

```
touch ./config.local.yaml
```

This file needs to be updated with URIs and credentials for 3rd party services.

Add the following values:

`./config.local.yaml`

```yaml
DEBUG: true
```

#### 3) Start External Services


```bash
docker-compose up -d
```

Creates docker containers for any 3rd party dependencies.

#### 4) Database


```bash
python manage.py db upgrade
```

Initializes the database and runs migrations.

*Make sure a container for your database is running before using these commands.*

#### 5) OAuth Application Credentials

Finally, you'll need to generate google application credentials to hit google in local development.
Go to https://console.developers.google.com and generate a new client application.

In Authorized Redirect URIs field, add the following:

```
http://localhost:5000/login/google/authorized
```
Once generated, you will need to specify the client id and secret in the config. See `config.local.yaml.example`



### Running

```bash
# Load your virtual environment
pyenv activate macros
docker-compose up -d
python manage.py runserver # Starts the backend
```

You can check if services are already running using `docker ps`.
You can check if the backend is running by opening `http://localhost:5000`.

### Testing

```
make test
```

Runs `pylint` and `pytest`.

*Note: Make sure services are running with `docker ps`. Tests may depend on them.*

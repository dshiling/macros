FROM python:3.5

EXPOSE $PROJECT_PORT

COPY requirements.txt /tmp/
RUN pip install  --no-cache-dir -r /tmp/requirements.txt -i $PYTHON_PACKAGE_INDEX

COPY . $PROJECT_DIR
RUN groupadd -r $PROJECT_USER \
  && useradd -r -g $PROJECT_USER $PROJECT_USER \
  && chmod -R a+r $PROJECT_DIR

USER $PROJECT_USER
WORKDIR $PROJECT_DIR

CMD uwsgi conf.ini

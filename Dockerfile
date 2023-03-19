# Python
FROM python:3.10.8

# Define env variables
ENV PORT=8080
ENV SCOPE=$SCOPE

# install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
ENV POETRY_VIRTUALENVS_IN_PROJECT true

# install poetry
RUN pip install "poetry==1.2.2"

# copy project requirement files here to ensure they will be cached.
WORKDIR /root
ADD app/ app/
ADD logs/ logs/
ADD test/ test/
COPY docker/entrypoint.sh poetry.lock pyproject.toml ./

RUN poetry install

EXPOSE $PORT

CMD ["bash", "entrypoint.sh"]

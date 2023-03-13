FROM python:3.10-alpine as base

# Setup env
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1


# For pillow
RUN apk add jpeg-dev zlib-dev libmagic

FROM base AS python-deps

# Install pipenv and compilation dependencies
RUN apk update \
    && apk add gcc python3-dev musl-dev g++ mariadb-connector-c-dev \
    && pip install pipenv

# Install python dependencies in /.venv
COPY Pipfile .
COPY Pipfile.lock .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy

FROM base AS runtime

# Copy virtual env from python-deps stage
COPY --from=python-deps /.venv /.venv
ENV PATH="/.venv/bin:$PATH"

# Create and switch to a new user
RUN addgroup -S appuser && adduser -S appuser -G appuser

WORKDIR /home/appuser/src

# Install application into container
COPY --chown=appuser:appuser . .
RUN chmod +x entrypoint.sh

USER appuser:root


ENTRYPOINT ["/bin/sh", "entrypoint.sh"]
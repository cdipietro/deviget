# Base docker image for Deviget Minsweeper Challenge

FROM python:3.7
LABEL maintainer="Carlos Di Pietro <cdipietro11@gmail.com>"

ENV app=minesweeper

# Set working directory
WORKDIR /$app

# Install Python dependencies
COPY ./Pipfile* ./
RUN pip install --upgrade pip==18.0
RUN pip install pipenv
RUN pipenv install --dev
RUN pipenv install --deploy
RUN pipenv install --system

# Copy application to working directory
COPY ./$app ./$app

# Set application as entrypoint
CMD  gunicorn -b 0.0.0.0:8000 minesweeper.app --reload

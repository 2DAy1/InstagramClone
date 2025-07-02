FROM python:3.12-slim


SHELL ["/bin/bash", '-c']

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip


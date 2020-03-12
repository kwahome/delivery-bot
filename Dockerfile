FROM python:3

ENV PYTHONUNBUFFERED 1

RUN mkdir -p /usr/src/app

COPY . /usr/src/app

WORKDIR /usr/src/app

# upgrade pip
RUN pip install -U pip

RUN pip install -r requirements.txt

EXPOSE 3978
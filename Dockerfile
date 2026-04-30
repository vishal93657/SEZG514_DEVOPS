FROM python:3.14-slim

WORKDIR /app

COPY Pipfile Pipfile.lock /app/

RUN pip install pipenv
RUN pipenv install --deploy --ignore-pipfile

COPY . /app/

EXPOSE 5000

CMD ["pipenv", "run", "python", "app.py"]
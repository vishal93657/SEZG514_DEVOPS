FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir pylint

EXPOSE 5000

CMD ["python", "app.py"]
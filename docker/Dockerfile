FROM python:3.13-slim

WORKDIR /trainee-test-assignment

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
EXPOSE 8501
FROM python:3.12.3-slim

WORKDIR /app

COPY requirement.txt /app/requirement.txt

RUN pip install --no-cache-dir -r requirement.txt

COPY . /app

WORKDIR /app/auth_service

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
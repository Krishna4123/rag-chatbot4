FROM python:3.10

WORKDIR /app

COPY backend_requirements.txt .
RUN pip install --no-cache-dir -r backend_requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "app:app", "-b", "0.0.0.0:8000"]

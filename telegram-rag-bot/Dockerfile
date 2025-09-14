FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

EXPOSE 10000

CMD ["gunicorn", "src.server:app", "-b", "0.0.0.0:10000"]

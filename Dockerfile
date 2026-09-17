FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY Main.py Models.py Database.py ./
COPY alembic.ini ./
COPY alembic/ ./alembic/

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "Main:app", "--host", "0.0.0.0", "--port", "8000"]
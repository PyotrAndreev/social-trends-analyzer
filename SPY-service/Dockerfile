FROM python:3.12

WORKDIR /app

COPY . .

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
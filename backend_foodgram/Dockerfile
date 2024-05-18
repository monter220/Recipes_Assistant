FROM python:3.9

WORKDIR /app

COPY requirements.txt .
COPY ./ingredients.json .

RUN python -m pip install --upgrade pip

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "backend_foodgram.wsgi"]
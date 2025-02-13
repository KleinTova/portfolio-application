FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

ENV FLASK_APP=app/app.py

ARG ENV=development

ENV ENV=$ENV

CMD ["sh", "-c", "if [ \"$ENV\" = \"production\" ]; then gunicorn -w 4 -b 0.0.0.0:5000 app.app:app; else flask run --host=0.0.0.0; fi"]
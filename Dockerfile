FROM python:3.6.9-buster
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip -r requirements.txt
COPY . .
ENTRYPOINT ["python", "app.py"]

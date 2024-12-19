FROM python:3.10-slim

WORKDIR /app

COPY project_files/requirements.txt /app/
COPY project_files/ /app/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]


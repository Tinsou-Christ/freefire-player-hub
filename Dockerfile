FROM python:3.11-slim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ffapi ./ffapi

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/usr/src/app/ffapi
ENV PORT=8000

EXPOSE 8000
CMD ["sh", "-c", "gunicorn --chdir ffapi app:app --bind 0.0.0.0:${PORT} --workers 2 --threads 4 --timeout 60"]

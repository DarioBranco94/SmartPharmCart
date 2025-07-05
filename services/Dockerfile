FROM python:3.11-slim
WORKDIR /app
COPY services/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY cart_event_consumer.py cart_sync_service.py ./
CMD ["python", "cart_event_consumer.py"]

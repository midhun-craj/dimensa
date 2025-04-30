FROM python:3.10-slim

WORKDIR /app

RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8082

CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8082", "--workers", "2" ]
FROM python:3.10-slim

WORKDIR /app

RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8081

CMD [ "streamlit", "run", "streamlit_app.py", "--server.address=0.0.0.0", "--server.port=8081" ]
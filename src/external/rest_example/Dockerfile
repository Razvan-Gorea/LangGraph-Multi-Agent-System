FROM python:3.9-slim

WORKDIR /rest_example

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python3", "fast_api_example.py"]
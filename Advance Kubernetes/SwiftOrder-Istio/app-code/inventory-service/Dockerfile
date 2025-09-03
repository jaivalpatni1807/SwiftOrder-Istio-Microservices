# app-code/inventory-service/Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install Flask psycopg2-binary
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
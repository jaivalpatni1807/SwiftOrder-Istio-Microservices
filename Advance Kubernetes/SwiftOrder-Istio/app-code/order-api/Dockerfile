# app-code/order-api/Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install Flask requests
EXPOSE 3000
CMD ["flask", "run", "--host=0.0.0.0", "--port=3000"]
# Dockerfile
# Utilisation d'une image python ancienne pour garantir des CVEs détectables par Trivy
FROM python:3.7-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Port exposé défini dans la doc d'architecture
EXPOSE 5000

CMD ["python", "app.py"]
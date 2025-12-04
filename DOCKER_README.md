# Docker Setup für die Hypo-Churn REST API

## Schnellstart

**Hinweis:** Verwenden Sie entweder `docker compose` (V2) oder `docker-compose` (V1), je nach Installation.

### Option 1: Mit Makefile (empfohlen - funktioniert mit beiden Versionen)
```bash
make up-bg    # API im Hintergrund starten
make logs     # Logs anzeigen
make down     # Stoppen
```

### Option 2: Mit Docker Compose direkt

#### Docker Compose V2 (neuere Versionen):
```bash
# API starten
docker compose up --build

# Im Hintergrund starten
docker compose up -d --build

# Logs anzeigen
docker compose logs -f api

# Status prüfen
docker compose ps

# Stoppen
docker compose down
```

#### Docker Compose V1 (ältere Versionen):
```bash
# Verwenden Sie docker-compose statt docker compose
docker-compose up -d --build
docker-compose logs -f api
docker-compose down
```

Die API ist dann erreichbar unter:
- **API Endpunkt**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpunkte

### Health Check
```bash
curl http://localhost:8000/health
```

### Model Info
```bash
curl http://localhost:8000/model/info
```

### Einzelne Vorhersage
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "credit_score": 650,
    "Geography": "France",
    "Gender": "Female",
    "Age": 42,
    "loan_age_years": 2,
    "outstanding_loan_balance": 0.0,
    "num_bank_products": 1,
    "has_credit_card": 1,
    "online_banking_active": 1,
    "annual_income": 101348.88,
    "monthly_income": 8445.74,
    "estimated_property_value": 354721.08,
    "ltv_ratio": 0.0,
    "payment_to_income_ratio": 0.0,
    "risk_score": 0.168,
    "balance_per_product": 0.0
  }'
```

### Batch Vorhersage
```bash
curl -X POST http://localhost:8000/predict/batch \
  -H "Content-Type: application/json" \
  -d '{
    "customers": [
      {
        "credit_score": 650,
        "Geography": "France",
        "Gender": "Female",
        "Age": 42,
        "loan_age_years": 2,
        "outstanding_loan_balance": 0.0,
        "num_bank_products": 1,
        "has_credit_card": 1,
        "online_banking_active": 1,
        "annual_income": 101348.88
      }
    ]
  }'
```

## Konfiguration

### Umgebungsvariablen

Die folgenden Umgebungsvariablen können in der `docker-compose.yml` angepasst werden:

- `MODEL_NAME`: Name des zu ladenden Modells (Standard: `best_model_random_forest`)
- `PYTHONUNBUFFERED`: Verhindert Pufferung der Python-Ausgabe (Standard: `1`)

### Port ändern

Um die API auf einem anderen Port laufen zu lassen, ändere in `docker-compose.yml`:

```yaml
ports:
  - "9000:8000"  # Läuft dann auf Port 9000
```

### Development Mode

Für die Entwicklung können Sie den Code als Volume mounten (in `docker-compose.yml` auskommentiert):

```yaml
volumes:
  - ./src:/app/src:ro
  - ./api:/app/api:ro
```

Dann mit `--reload` starten:
```bash
docker-compose run --service-ports api \
  uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

## Troubleshooting

### Container neu bauen
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Logs bei Problemen
```bash
docker-compose logs api
```

### In den Container einsteigen
```bash
docker-compose exec api bash
```

### Modell-Fehler

Falls das Modell nicht geladen werden kann:
1. Überprüfen Sie, dass `models/best_model_random_forest.pkl` existiert
2. Prüfen Sie die Logs: `docker-compose logs api`
3. Setzen Sie `MODEL_NAME` Umgebungsvariable auf den korrekten Modellnamen

### Port bereits belegt

Falls Port 8000 bereits verwendet wird:
```bash
# Ändere Port in docker-compose.yml zu z.B. 8001:8000
# Oder stoppe den Service, der Port 8000 verwendet:
sudo lsof -i :8000
```

## Python-Client Beispiel

```python
import requests

# Health Check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Vorhersage
customer = {
    "credit_score": 650,
    "Geography": "France",
    "Gender": "Female",
    "Age": 42,
    "loan_age_years": 2,
    "outstanding_loan_balance": 0.0,
    "num_bank_products": 1,
    "has_credit_card": 1,
    "online_banking_active": 1,
    "annual_income": 101348.88,
    "monthly_income": 8445.74,
    "estimated_property_value": 354721.08,
    "ltv_ratio": 0.0,
    "payment_to_income_ratio": 0.0,
    "risk_score": 0.168,
    "balance_per_product": 0.0
}

response = requests.post("http://localhost:8000/predict", json=customer)
prediction = response.json()

print(f"Churn Prediction: {prediction['prediction_label']}")
print(f"Probability: {prediction['churn_probability']:.2%}")
print(f"Risk Level: {prediction['risk_level']}")
```

## Produktions-Deployment

Für Produktion sollten Sie:

1. **Secrets Management**: Verwenden Sie Docker Secrets für sensible Daten
2. **Reverse Proxy**: Verwenden Sie nginx oder Traefik als Reverse Proxy
3. **HTTPS**: Aktivieren Sie SSL/TLS
4. **Monitoring**: Fügen Sie Prometheus/Grafana hinzu
5. **Log Aggregation**: Verwenden Sie ELK Stack oder ähnliches
6. **Resource Limits**: Setzen Sie Memory/CPU Limits in docker-compose.yml

Beispiel Resource Limits:
```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

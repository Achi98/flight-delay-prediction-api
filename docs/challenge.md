# Software Engineer (ML & LLMs) Challenge — Entrega

## 1) Repositorio y ramas (GitFlow)

- **Repositorio público:** https://github.com/Achi98/flight-delay-prediction-api.git  
- **Rama release (para revisión):** `main`  
- **Rama de integración:** `develop`  
- **Ramas de desarrollo (NO eliminadas):**
  - `feature/part1-model`
  - `feature/part2-api`
  - `feature/part3-deploy`
  - `feature/part4-cicd`

---

## 2) Parte I — Modelo (`challenge/model.py`)

Se operacionalizó el trabajo del notebook `training.ipynb` dentro de `challenge/model.py`, manteniendo la estructura del repositorio y respetando las firmas de métodos provistos por el challenge.

### Modelo seleccionado
Se eligió **XGBoost (`XGBClassifier`)** por su buen rendimiento en datos tabulares y por ser eficiente en inferencia.

### Dependencias / compatibilidad (ajustes realizados)
Durante la operacionalización y el CI:
- Se agregó `xgboost==1.7.6` a `requirements.txt` para asegurar ejecución en CI y runtime.
- Se fijó `anyio==3.7.1` para compatibilidad entre FastAPI/Starlette y `TestClient` en CI.

### Ejecutar tests de modelo
```bash
make model-test
```
## 3) Parte II — API con FastAPI (`challenge/api.py`)

Se implementó una API con **FastAPI** que expone, como mínimo, los endpoints:

- `GET /health` — endpoint de salud del servicio (healthcheck)..
- `POST /predict` — predicción de delay para una lista de vuelos.

### `GET /health` (ejemplo)

Response (200):

```json
{"status": "OK"}
```

### `POST /predict` (ejemplo)

Request (ejemplo):

```json
{
  "flights": [
    {
      "OPERA": "Aerolineas Argentinas",
      "TIPOVUELO": "N",
      "MES": 3
    }
  ]
}
```

Response (ejemplo):

```json
{ "predict": [0] }
```

### Ejecutar tests de API

```bash
make api-test
```

## 4) Parte III — Deploy en GCP (Cloud Run)

La API fue containerizada con Docker y desplegada en **Google Cloud Run**.

API pública:

https://flight-delay-api-1061646903737.us-central1.run.app

Verificación rápida (health):

```bash
curl.exe https://flight-delay-api-1061646903737.us-central1.run.app/health
```

Verificación predict (ejemplo usando `curl` o Postman):

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"flights":[{"OPERA":"Aerolineas Argentinas","TIPOVUELO":"N","MES":3}]}' \
  https://flight-delay-api-1061646903737.us-central1.run.app/predict
```

Recomendación: usar Postman en Windows para evitar problemas de escape al enviar JSON por terminal.

Stress test (ejecutar desde la raíz del repositorio):

```bash
make stress-test STRESS_URL=https://flight-delay-api-1061646903737.us-central1.run.app
```

## 5) Parte IV — CI/CD (GitHub Actions)

Se añadieron workflows en `.github/workflows/` para CI y CD.

CI (Continuous Integration):

- Ejecuta: `make model-test` y `make api-test`.
- Triggers: PRs a `develop` y `main`, pushes a `develop`.

CD (Continuous Delivery):

- Ejecuta: build + push de la imagen Docker a Artifact Registry y deploy a Cloud Run.
- Trigger: push a `main`.

Workflows:

- `.github/workflows/ci.yml`
- `.github/workflows/cd.yml`

Secrets configurados en GitHub (Settings → Secrets and variables → Actions):

- `GCP_SA_KEY`
- `GCP_PROJECT_ID`
- `GCP_REGION`
- `GCP_AR_REPO`
- `GCP_SERVICE`
- `.github/workflows/cd.yml`


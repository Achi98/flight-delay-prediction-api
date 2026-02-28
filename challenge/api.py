import fastapi
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from pydantic import BaseModel, Field, validator
from typing import List
import pandas as pd

from challenge.model import DelayModel

app = fastapi.FastAPI()

# Instancia para la API
MODEL = DelayModel()

# Lista  de aerolíneas que se usan en el modelo (para asegurar que el preprocesamiento siempre tenga estas columnas)
ALLOWED_AIRLINES = {
    "Aerolineas Argentinas",
    "Grupo LATAM",
    "Sky Airline",
    "Copa Air",
    "Latin American Wings",
}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Convertimos el 422 default de FastAPI a 400 para que sea más compatible con los tests.
    return JSONResponse(
        status_code=400,
        content={"detail": "Invalid input"},
    )


@app.get("/health", status_code=200)
async def get_health() -> dict:
    return {"status": "OK"}


class FlightInput(BaseModel):
    OPERA: str = Field(..., description="Nombre de la aerolínea operadora")
    TIPOVUELO: str = Field(..., description="Tipo de vuelo: I=Internacional, N=Nacional")
    MES: int = Field(..., description="Mes de operación")

    @validator("MES")
    def mes_debe_ser_valido(cls, v: int) -> int:
        if not (1 <= v <= 12):
            raise ValueError("MES must be between 1 and 12")
        return v

    @validator("TIPOVUELO")
    def tipovuelo_debe_ser_valido(cls, v: str) -> str:
        if v not in {"N", "I"}:
            raise ValueError("TIPOVUELO must be 'N' or 'I'")
        return v

    @validator("OPERA")
    def opera_debe_ser_conocida(cls, v: str) -> str:
        if v not in ALLOWED_AIRLINES:
            raise ValueError("Unknown OPERA")
        return v


class PredictRequest(BaseModel):
    flights: List[FlightInput]


class PredictResponse(BaseModel):
    predict: List[int]


@app.post("/predict", status_code=200, response_model=PredictResponse)
async def post_predict(payload: PredictRequest) -> dict:

    flights_dicts = [f.dict() for f in payload.flights]
    df = pd.DataFrame(flights_dicts)

    # valores dummy consistentes
    df["Fecha-I"] = "2022-01-01 10:00:00"
    df["Fecha-O"] = "2022-01-01 10:00:00"

    # Preprocesa + predice
    features = MODEL.preprocess(df)
    preds = MODEL.predict(features)

    return {"predict": preds}
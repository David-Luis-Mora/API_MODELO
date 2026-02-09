from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import mlflow
import mlflow.pyfunc

import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()

os.environ["DATABRICKS_HOST"] = os.getenv("DATABRICKS_HOST")
os.environ["DATABRICKS_TOKEN"] = os.getenv("DATABRICKS_TOKEN")

mlflow.set_tracking_uri("databricks")

URL_MODELO = "models:/workspace.default.consumo_tenerife_version_final/1"


@asynccontextmanager
async def lifespan(app: FastAPI):

    try:
        app.state.modelo = mlflow.pyfunc.load_model(URL_MODELO)
        print("Modelo cargado desde Databricks")

    except Exception as e:
        print("Error cargando modelo:", e)
        app.state.modelo = None

    yield
    print("Aplicación detenida")


app = FastAPI(
    title="API Consumo Energético",
    lifespan=lifespan
)


class PredictRequest(BaseModel):
    dia: int
    mes: int
    cups_municipio: str
    cups_distribuidor: str


@app.post("/predict")
def predict(data: PredictRequest):

    if app.state.modelo is None:
        raise HTTPException(status_code=500, detail="Modelo no cargado")

    X = pd.DataFrame([{
        "dia": data.dia,
        "mes": data.mes,
        "cups_municipio": data.cups_municipio,
        "cups_distribuidor": data.cups_distribuidor
    }])

    X["dia"] = X["dia"].astype("int32")
    X["mes"] = X["mes"].astype("int32")

    pred_log = app.state.modelo.predict(X)[0]
    pred_kwh = int(np.expm1(pred_log))

    return {"prediccion_kWh": pred_kwh}

@app.get("/health")
def health():

    if app.state.modelo is None:
        return {"status": "ko"}

    return {"status": "ok"}

